# Real Estate valuation

## Intro 5 min
Valentas, a researcher, got working with real estate.
Generic idea was to create a service/product that provides real estate value. (Explain valuation without ESG and with ESG)
To make this happen we have to have a) real estate data, b) ESG data.

## Warmup 5 min
Real estate data. Was able to retrieve real estate transaction data.
Data was very messy, and at that time, long time ago that was that some of the code is excel macros. (Flash some code)
ESG data. From statistics department. A lot of other sources had to be integrated to actualy use data. (Show list of preprocessing)

## First working thing 5 min
The first feature that was implemented was .
Then a project was won and team grew.

## 10-15 min min GENERAL STUFF
- Transaction data is messy
- Statistics deparment is messy. (ATTEMPT TO WORK WITH API)
- voronoi diagram, you can take part of code and use it. Regions is trash, in reality there are more regions. Break down, and combine matching.
- GIS
    - CRS Region resolving,
    - stuff with addresses and more,
    - cheap, almost cost us! 
    - From different sources
    - OUT OF bounds addresses.
    - CRS know your CRS

##  10-15 product/service specific STUFF
Over course of the project Three groups of services were identified: Market indicators, specific asset indicators, financial modelings.

Market indicators. Price forecast. (Requires a lot of predictions)  Seasonality, interpolacija
Market indiciators. Regional risk forecast.
Specific asset. Change in long-term value. (Requires address resolving)
Market comparison. Market comparison. (Requires similarity, leaf approach)
Adjustment factors. Adjustment factors. (Requires shap)

## Business lessons (ask if wants)

?



## Notes
What data tools were specific to each service?
Data preparation good slide.
Explaining LIME with SHAP and why SHAP makes more sense is good.

What we should NOT tell. Less is more.
Should we teach basics of machine learning, test/train, underfiting? Maybe no?
Should we explain grants, research papers? No?

Things to mention:
- Hierarchical indicators. How we predict value of each individual feature but we show only the grouped up thing. Business solution.




For Aidis:
- Wordpress and services stuff?
- Do your transformers need to be fitted?