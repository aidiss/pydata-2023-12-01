import re
from typing import Optional

import googlemaps
import pandas as pd
import structlog
from pandera import check_types
from pandera.typing import DataFrame
from pandera.typing.geopandas import GeoDataFrame
from sklearn.pipeline import Pipeline, FunctionTransformer

from va_model import settings
from va_model.preprocessing.data.utils import save_df_to_db
from va_model.preprocessing.transformers import ColumnSelector
from va_model.preprocessing.utils import timeit
from va_model.schemas import SplitDateToYearQuarterMonthInputSchema, SplitDateToYearQuarterMonthOutputSchema

logger = structlog.getLogger()


@timeit
@check_types
def shorten_region_names(df: DataFrame, pattern: re.Pattern) -> DataFrame:
    """
    Shorten region names with provided regex pattern
    """
    logger.debug("shorten_region_names")
    return df.assign(Region=df["Region"].replace(pattern, ".", regex=True))


@timeit
@check_types
def split_date_to_year_quarter_month(
    df: DataFrame[SplitDateToYearQuarterMonthInputSchema],
) -> DataFrame[SplitDateToYearQuarterMonthOutputSchema]:
    logger.info("split_date_to_year_quarter_month")
    date = pd.to_datetime(df["Date"], errors="coerce")
    return df.assign(Year=date.dt.year).assign(Quarter=date.dt.quarter).assign(Month=date.dt.month).drop("Date", axis=1)


@timeit
@check_types
def attempt_to_fill_missing_coordinates(
    df: DataFrame, gmaps_client: googlemaps.client.Client, address_df_transaction: DataFrame
) -> DataFrame:
    """
    Attempt to fill missing lat, lng coordinates from address database
    If matching addresses were not found, google maps API is used to get the coordinates
    Updates address db with found coordinates
    If some coordinates are still missing, append address dataframe with failed addresses

    Return: Updated dataframe with coordinates
    """
    logger.info("attempt_to_fill_missing_coordinates")

    # Get coordinates from addresses db
    df_no_lat = get_rows_without_lat(df)
    logger.info(f"Number of rows without coordinates: {df_no_lat.shape[0]}")
    coordinates_from_db = get_coordinates_by_address_from_db(df_no_lat, address_df_transaction)
    df.update(coordinates_from_db[["lat", "lng"]])

    df_no_lat = get_rows_without_lat(df)
    logger.info(f"Rows without coordinates left, after checking address database: {df_no_lat.shape[0]}")
    if df_no_lat.empty:
        return df

    # Get coordinates from google maps
    logger.info("Attempting to get coordinates from google maps")
    received_coordinates = get_coordinates_from_google_maps(df_no_lat, gmaps_client)
    df.update(received_coordinates[["lat", "lng"]])
    logger.info(f"Number of rows with coordinates received from google maps: {received_coordinates.shape[0]}")

    # Update db with found coordinates
    update_address_db_with_found_coordinates(received_coordinates)

    df_no_lat = get_rows_without_lat(df)
    logger.info(f"Rows without coordinates left, after accessing google maps: {df_no_lat.shape[0]}")
    if df_no_lat.empty:
        return df

    # Update db with incorrect address
    logger.info(f"Rows without coordinates left: \n {df_no_lat}")
    update_address_db_with_incorrect_addresses(df_no_lat)

    return df


@timeit
def update_address_db_with_found_coordinates(df: pd.DataFrame):
    df = df.rename(columns={"Address": "Adress_original"})
    df["Adress_that_works"] = None
    df = df[["Adress_that_works", "Adress_original", "lat", "lng"]]
    save_df_to_db(df, settings.CLASIFICATION_DB, "address_coordinates_rc_transactions", "append")


@timeit
def update_address_db_with_incorrect_addresses(df: pd.DataFrame):
    df = df.rename(columns={"Address": "Adress_original"})
    df["Adress_that_works"] = "Address not found by google"
    df = df[["Adress_that_works", "Adress_original", "lat", "lng"]]
    save_df_to_db(df, settings.CLASIFICATION_DB, "address_coordinates_rc_transactions", "append")


@timeit
def get_coordinates_from_google_maps(df_no_lat: pd.DataFrame, gmaps_client: googlemaps.client.Client) -> DataFrame:
    coordinate_series_list = []
    for index, content in df_no_lat.iterrows():
        logger.warning("WATCH OUT going to do GOOGLE MAPS REQUESTS!!!!!")
        geocode_result_location = _get_geocode_results(gmaps_client, content.Address)
        if geocode_result_location:
            s = pd.Series(geocode_result_location)
            s["Address"] = content.Address
            s.name = index
            coordinate_series_list.append(s)
    df = pd.DataFrame(coordinate_series_list)
    return df


@timeit
def get_rows_without_lat(df: DataFrame) -> DataFrame:
    """
    Check DataFrame for rows with missing coordinates
    """
    return df[df["lat"].isnull()]


@timeit
@check_types
def get_coordinates_by_address_from_db(
    df_no_lat: pd.DataFrame, address_df_transaction: pd.DataFrame
) -> DataFrame[GetCoordinatesByAddressFromDbSchema]:
    df = (
        df_no_lat[["Address"]]
        .reset_index()
        .merge(address_df_transaction[["Address", "lat", "lng"]], on=["Address"])
        .set_index("index")
    )
    return df


@timeit
@check_types
def _get_geocode_results(gmaps: googlemaps.client.Client, address: str) -> Optional[GeoCodeResults]:
    """Get response from google maps for the adress"""
    logger.info(address)
    if not isinstance(address, str):
        raise TypeError(f"Address should be string, received type {type(address)}")
    if address == "":
        raise ValueError("Address string cannot be empty")

    geocode_response = gmaps.geocode(address)
    try:
        geometry_location = geocode_response[0]["geometry"]["location"]
    except IndexError:
        logger.info("Address not found")
        return None
    return geometry_location


@timeit
@check_types
def get_point_from_lat_long(
    df: DataFrame[GetPointFromLatLongInputSchema],
) -> GeoDataFrame[LatLongToPointSchema]:
    logger.info("get_point_from_lat_long")
    return (
        gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["lng"], df["lat"]))
        .drop(["lat", "lng"], axis=1)
        .rename(columns={"geometry": "point"})
    )


@timeit
@check_types
def point_to_cluster(
    gdf: GeoDataFrame[LatLongToPointSchema], region_shapes: GeoDataFrame[ClusterToRegion]
) -> DataFrame[PointToClusterSchema]:
    logger.info("point_to_cluster")
    logger.info(f"Rows before sjoin: {gdf.shape[0]}")
    gdf = gpd.GeoDataFrame(gdf, geometry="point")
    region_shapes = region_shapes.rename(columns={"Cluster_ID": "ward"})
    gdf = (
        gpd.sjoin(gdf, region_shapes[["ward", "geometry"]], predicate="within", how="inner")
        .drop(["Cluster_ID", "point", "index_right"], axis=1)
        .rename(columns={"ward": "Cluster_ID"})
    )
    logger.info(f"Rows after sjoin: {gdf.shape[0]}")
    return gdf


@timeit
@check_types
def cluster_id_to_region(
    gdf: DataFrame[PointToClusterSchema], cluster_to_region: GeoDataFrame[ClusterToRegion]
) -> DataFrame:
    logger.info("cluster_id_to_region")
    return gdf.merge(cluster_to_region, on="Cluster_ID", how="left")


@timeit
@check_types
def merge_indicators(
    df: DataFrame[MergeIndicatorsInputSchema], indicator_pivoted
) -> DataFrame[MergeIndicatorsOutputSchema]:
    logger.info("indicators")
    df = df.merge(indicator_pivoted, on=["Region", "Year", "Quarter"], how="left")
    df = df.drop_duplicates(["Region", "Cluster_ID", "TransID", "Year", "Month", "Quarter"])
    df = df.drop(["Region", "Year", "TransID"], axis=1)
    df["Cluster_ID"] = df["Cluster_ID"].str.split("_", n=0, expand=True)[0]
    df["Cluster_ID"] = df["Cluster_ID"].astype("category")
    return df


@timeit
@check_types
def ensure_cluster_id_is_available(
    df: DataFrame[EnsureClusterIdIsAvailableInputSchema],
    gmaps_client: googlemaps.client.Client,
    cluster_to_region: GeoDataFrame[ClusterToRegion],
    address_df_transaction: DataFrame,
) -> DataFrame[EnsureClusterIdIsAvailableOutputSchema]:
    """This pipeline step makes sure that CLUSTER_ID is available
    If column is already available nothing is done
    If No cluster id is available:
        - If lat long is available attempt to get cluster id from it
        - If no lat long, but address is available, try to get lat long from address via google api
    """
    # In Index(['Date', 'Address', 'lat', 'lng', 'Cluster_ID'], dtype='object')
    # Out Index(['Date', 'Cluster_ID', 'Region'], dtype='object')     # 'index_right',

    # This flow is needed only if we do not have Cluster_ID populated
    if df["Cluster_ID"].isna().any():
        # If any of lat lng is na, try to get coordinates from googlemaps
        if df[["lat", "lng"]].isna().any().any():
            df = attempt_to_fill_missing_coordinates(
                df,
                gmaps_client=gmaps_client,
                address_df_transaction=address_df_transaction,
            )
        df = get_point_from_lat_long(df)
        df = point_to_cluster(df, region_shapes=cluster_to_region)
    df = cluster_id_to_region(df, cluster_to_region=cluster_to_region)
    df = df.drop(["Address", "lat", "lng", "geometry"], axis=1, errors="ignore")
    return df


@timeit
def indicators_pipeline(cluster_to_region, indicator_df, address_df_transaction) -> Pipeline:
    indicators_df_pivoted = (
        pd.pivot_table(
            indicator_df,
            index=["Region", "Year", "Quarter", "Month"],
            columns="Indicator",
            values="Value",
            aggfunc="mean",
        )
        .bfill()
        .ffill()
    )
    pipeline = Pipeline(
        [
            ("selector", ColumnSelector(settings.COLUMN_SELECTOR_FEATURES)),
            (
                "ensure_cluster_id_is_available",
                FunctionTransformer(
                    ensure_cluster_id_is_available,
                    kw_args={
                        "gmaps_client": googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY),
                        "cluster_to_region": cluster_to_region,
                        "address_df_transaction": address_df_transaction,
                    },
                    feature_names_out=lambda self, input_features: [
                        x for x in input_features.tolist() if x not in ["Address", "lat", "lng"]
                    ]
                    + ["Region"],
                ),
            ),
            (
                "region_name_shortener",
                FunctionTransformer(
                    func=shorten_region_names,
                    kw_args={"pattern": re.compile("(ajono )|(ivaldybė)")},
                    feature_names_out="one-to-one",
                ),
            ),
            (
                "date",
                FunctionTransformer(
                    split_date_to_year_quarter_month,
                    feature_names_out=lambda self, input_features: [x for x in input_features.tolist() if x != "Date"]
                    + ["Year", "Quarter", "Month"],
                ),
            ),
            (
                "indicators",
                FunctionTransformer(
                    merge_indicators,
                    kw_args={"indicator_pivoted": indicators_df_pivoted},
                    feature_names_out=lambda self, input_features: [
                        x for x in input_features.tolist() if x not in ["Region", "Year", "TransID"]
                    ]
                    + indicators_df_pivoted.columns.tolist(),
                ),
            ),
        ],
    )

    return pipeline
