# Bar Inventory Forecasting and Par-Level Recommendation

## Executive summary
This notebook cleans the original transaction-level Excel dataset, analyzes consumption by alcohol category, forecasts demand with a seven-day moving average and Random Forest, evaluates the forecasts, and recommends inventory par levels for bar-brand items.

## Data and quality
- Source: `Consumption Dataset.xlsx`; transaction rows loaded: 6,575; completed daily rows: 35,136.
- Scope: 6 bars, 16 brands, 96 bar-brand series.
- Date range: 2023-01-01 to 2024-01-01.
- Alcohol categories analyzed: 5.
- Invalid dates: 0; invalid numeric rows: 0; duplicate rows: 0.
- Maximum absolute conservation error: 0.00000000 ml.

## Forecast evidence
The chronological 80/20 validation compares a seven-day moving-average forecast, a seven-day seasonal-naive challenger, and a Random Forest using lags, rolling statistics, weekday, weekend, bar, and brand features. The moving-average MAE is 92.6 ml and WAPE is 166.3%. The Random Forest MAE is 98.3 ml and WAPE is 176.6%.

## Inventory recommendation
Par level = forecast daily demand x (lead time + review period) + safety stock. The policy uses 2 lead-time days, 1 review-period day, and a 95% service target. The validation simulation produced 200 stockout days, 36,037 ml lost volume, and 45,080 ml summed average inventory across 96 series.

The highest-volume validation series was **Thomas's Bar / Yellow Tail**, with 9 stockout days and 1,446 ml lost volume.

## Assumptions and next steps
Demand is measured in milliliters, unmet demand is treated as lost, lead time is constant, and observed consumption may be censored by historical stockouts. Add promotions, events, vendor lead-time variation, and a live inventory position before production deployment.
