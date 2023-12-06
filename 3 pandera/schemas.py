from datetime import datetime
from typing import TypedDict

import geopandas as gpd
import pandas as pd
import pandera as pa
from pandera import SchemaModel, Field
from pandera import Series


class IndicatorToPeriod(SchemaModel):
    abbr_en: Series[str] = pa.Field()
    Period: Series[str] = pa.Field()


class ClusterSchemas(SchemaModel):
    ward: Series[str] = pa.Field()
    geometry: Series[gpd.array.GeometryDtype] = Field(coerce=True)


class RegionsShape(SchemaModel):
    Apskritis: Series[str]
    geometry: Series[gpd.array.GeometryDtype] = Field(coerce=True)


class ClusterToRegion(SchemaModel):
    Cluster_ID: Series[str]
    geometry: Series[gpd.array.GeometryDtype] = Field(coerce=True)
    Region: Series[str]


class FlatIndicatorEstimated(SchemaModel):
    Region: Series[str] = pa.Field()
    Date: Series[datetime] = pa.Field(coerce=True)
    Variable: Series[str] = pa.Field()
    Value: Series[float] = pa.Field()
    Level: Series[int] = pa.Field()


class SelectedIndicator(FlatIndicatorEstimated):
    # Period: Series[str] = pa.Field(nullable=True)
    pass


class AdministrativeLevelsCorespondingSchema(SchemaModel):
    Level_1: Series[str] = pa.Field()
    Level_2: Series[str] = pa.Field()
    Level_3: Series[str] = pa.Field()
    Level_4: Series[str] = pa.Field()


class RegionYearQuarterMonthClusterid(SchemaModel):
    Region: Series[str] = pa.Field(nullable=True)
    Year: Series[int] = pa.Field()
    Quarter: Series[int] = pa.Field()
    Month: Series[int] = pa.Field()
    Cluster_ID: Series[str] = pa.Field()


class ShiftIndicatorPeriodOutputSchema(SelectedIndicator):
    Level: Series[float] = pa.Field(nullable=True, coerce=True)
    Value: Series[float] = pa.Field(nullable=True)

    class Config:
        strict = False


class HandleMaxLevelsOutputSchema(ShiftIndicatorPeriodOutputSchema):
    pass


class AdministrativeLevelsSchema(SchemaModel):
    Lygis: Series[int] = Field()
    Regionas: Series[str] = Field()


class IndicatorsList(SchemaModel):
    abbr_en: Series[str] = Field()
    Period: Series[str] = Field()


class AdminRibosSchema(SchemaModel):
    Region: Series[str] = Field()
    geometry: Series[gpd.array.GeometryDtype] = Field()


class GeoCodeResults(TypedDict):
    lat: float
    lng: float


class GetCoordinatesByAddressFromDbSchema(SchemaModel):
    Address: Series[str] = Field()
    lat: Series[float] = Field()
    lng: Series[float] = Field()


class GetPointFromLatLongInputSchema(SchemaModel):
    Date: Series[pd.Timestamp] = Field(coerce=True)
    Address: Series[str] = Field()
    lat: Series[float] = Field()
    lng: Series[float] = Field()
    Cluster_ID: Series[str] = Field(ignore_na=True, nullable=True)


class LatLongToPointSchema(SchemaModel):
    Date: Series[pd.Timestamp] = Field(coerce=True)
    Address: Series[str] = Field()
    Cluster_ID: Series[str] = Field(ignore_na=True, nullable=True)
    point: Series[gpd.array.GeometryDtype] = Field(coerce=True)


class PointToClusterSchema(SchemaModel):
    Date: Series[pd.Timestamp] = Field(coerce=True)
    Address: Series[str] = Field()
    Cluster_ID: Series[str] = Field()


class EnsureClusterIdIsAvailableInputSchema(SchemaModel):
    Date: Series[pd.Timestamp] = Field(coerce=True)
    Address: Series[str] = Field()
    lat: Series[float] = Field(nullable=True, coerce=True)
    lng: Series[float] = Field(nullable=True, coerce=True)
    Cluster_ID: Series[str] = Field(nullable=True, coerce=True)


class EnsureClusterIdIsAvailableOutputSchema(SchemaModel):
    Date: Series[pd.Timestamp] = Field(coerce=True)
    Cluster_ID: Series[str] = Field()
    Region: Series[str] = Field()


class SplitDateToYearQuarterMonthInputSchema(SchemaModel):
    Date: Series[pd.Timestamp] = Field(coerce=True)
    Cluster_ID: Series[str] = Field()
    Region: Series[str] = Field()


class SplitDateToYearQuarterMonthOutputSchema(SchemaModel):
    Cluster_ID: Series[str] = Field()
    Region: Series[str] = Field()
    Year: Series[int] = Field()
    Quarter: Series[int] = Field()
    Month: Series[int] = Field()


class MergeIndicatorsInputSchema(SchemaModel):
    Cluster_ID: Series[str] = Field()
    Region: Series[str] = Field()
    Year: Series[int] = Field()
    Quarter: Series[int] = Field()
    Month: Series[int] = Field()


class MergeIndicatorsOutputSchema(SchemaModel):
    Cluster_ID: Series[pd.CategoricalDtype] = Field()
    Quarter: Series[int] = Field()
    Month: Series[int] = Field()
    BPI: Series[float] = Field(nullable=True, coerce=True)
    Births: Series[float] = Field(nullable=True, coerce=True)
    CIPI: Series[float] = Field(nullable=True, coerce=True)
    CPI: Series[float] = Field(nullable=True, coerce=True)
    DAI: Series[float] = Field(nullable=True, coerce=True)
    EMP_No: Series[float] = Field(nullable=True, coerce=True)
    EXP: Series[float] = Field(nullable=True, coerce=True)
    FDI: Series[float] = Field(nullable=True, coerce=True)
    Fires: Series[float] = Field(nullable=True, coerce=True)
    GDP: Series[float] = Field(nullable=True, coerce=True)
    GDP_resident: Series[float] = Field(nullable=True, coerce=True)
    IPRI: Series[float] = Field(nullable=True, coerce=True)
    Loans_H: Series[float] = Field(nullable=True, coerce=True)
    Loans_HC: Series[float] = Field(nullable=True, coerce=True)
    Loans_HOTH: Series[float] = Field(nullable=True, coerce=True)
    Loans_HRE: Series[float] = Field(nullable=True, coerce=True)
    Loans_NFOH: Series[float] = Field(nullable=True, coerce=True)
    MWN: Series[float] = Field(nullable=True, coerce=True)
    Municipality_expenses: Series[float] = Field(nullable=True, coerce=True)
    NRB: Series[float] = Field(nullable=True, coerce=True)
    Resident_no: Series[float] = Field(nullable=True, coerce=True)
    SRELNO: Series[float] = Field(nullable=True, coerce=True)
    SRELV: Series[float] = Field(nullable=True, coerce=True)
    SREP: Series[float] = Field(nullable=True, coerce=True)
    SRER: Series[float] = Field(nullable=True, coerce=True)
    Taxes: Series[float] = Field(nullable=True, coerce=True)
    UE: Series[float] = Field(nullable=True, coerce=True)


class PrepareIndicatorsOutputSchema(SchemaModel):
    Region: Series[str] = pa.Field()
    Year: Series[int] = Field()
    Quarter: Series[int] = Field()
    Month: Series[int] = Field()
    Indicator: Series[str] = pa.Field()
    Value: Series[float] = pa.Field(nullable=True)
