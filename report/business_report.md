# Bar Inventory Forecasting and Par-Level Recommendation

## Executive summary
This notebook cleans the committed daily consumption CSV, forecasts demand by bar and brand, evaluates a seasonal baseline against a Random Forest, and recommends inventory par levels for a two-day supplier lead time.

## Data and quality
- Rows loaded: 35,136; completed daily rows: 35,136.
- Scope: 6 bars, 16 brands, 96 bar-brand series.
- Date range: 2023-01-01 to 2024-01-01.
- Invalid dates: 0; invalid demand values: 0; duplicate keys: 0.

## Forecast evidence
The chronological 80/20 validation compares a seven-day seasonal-naive forecast with a Random Forest using lags, rolling statistics, weekday, weekend, bar, and brand features. The seasonal baseline WAPE is 175.0% and the Random Forest WAPE is 176.6%. RMSE values are 203.5 ml and 148.2 ml respectively.

## Inventory recommendation
Par level = predicted daily demand x 2 lead-time days + 1.645 x daily demand standard deviation x sqrt(2). The validation simulation produced 418 stockout days, 68,193 ml lost volume, and 33,579 ml summed average inventory across 96 series.

The highest-volume validation series was **Thomas's Bar / Yellow Tail**, with 14 stockout days and 2,400 ml lost volume.

## Assumptions and next steps
Demand is measured in milliliters, unmet demand is treated as lost, lead time is constant, and observed consumption may be censored by historical stockouts. Add promotions, events, vendor lead-time variation, and a live inventory position before production deployment.
