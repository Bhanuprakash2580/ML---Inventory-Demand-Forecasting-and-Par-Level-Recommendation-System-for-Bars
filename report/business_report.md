# Managerial Report: Bar Inventory Forecasting

## Business problem

Bar managers must protect availability of popular brands without tying cash and storage capacity up in slow-moving stock. A stockout can prevent signature drinks and reduce guest satisfaction; excess stock increases working capital, shrinkage, and spoilage exposure.

## Data and method

The supplied workbook contains transaction-level opening balance, purchase, consumption, and closing balance records. The notebook verifies the conservation identity, converts timestamps to daily dates, aggregates consumption by bar and brand, and fills missing service days with zero. The forecasting evaluation uses a chronological 80/20 split. A seasonal-naive forecast based on the value seven days earlier is compared with a Random Forest using lag, rolling, calendar, bar, and brand features.

The recommended policy is deliberately interpretable: expected daily demand is multiplied by supplier lead time and augmented with safety stock. Safety stock is `1.645 * daily standard deviation * sqrt(lead_time_days)`, corresponding to a 95% target service level. The simulation receives pending orders after lead time, deducts actual consumption, records lost demand, and orders up to the par level.

## Assumptions and trade-offs

- Lead time is constant by default at two days; real vendor variability should be added when available.
- Unmet demand is lost, not backordered.
- Measurements are in milliliters and purchases are immediately available after receipt.
- The implementation favors a transparent Random Forest and seasonal baseline over an opaque advanced model because managers need explainable reorder quantities and the dataset contains intermittent zero demand. On the supplied data, the seasonal-naive baseline achieved 203.53 ml RMSE and 174.98% WAPE; the Random Forest achieved 148.19 ml RMSE and 176.66% WAPE. The Random Forest reduces large errors, while the baseline is slightly better on aggregate absolute error, so both remain visible as operational challengers.
- Historical stockouts can censor observed consumption, so forecast accuracy should be interpreted as demand observed in the inventory system, not perfect unconstrained demand.

## Operational recommendation

Use the notebook output as a daily decision-support table containing bar, brand, forecast demand, safety stock, par level, and reorder quantity. Start with a 95% service level for high-velocity brands and review the resulting simulated stockout and holding-stock trade-off with managers. Apply ABC segmentation to prioritize human review: Class A items deserve the tightest monitoring and lead-time confirmation.

## Failure modes and next steps

Promotions, holidays, events, weather, supplier delays, breakage, and pouring waste can invalidate a historical-only forecast. Production should monitor forecast WAPE, stockout rate, lead-time variance, and data-quality checks. Future improvements include promotion/event features, probabilistic forecasts, per-vendor lead times, censored-demand correction, and a live reorder dashboard.

## Evidence

The completed run generated 35,136 daily bar-brand rows and 96 recommendation series. The validation policy simulation recorded 418 stockout days, 68,193 ml lost volume, and 33,579 ml summed average inventory across the 96 series. Generated evidence is available in `data/processed/forecast_metrics.csv`, `data/processed/par_level_recommendations.csv`, and `report/business_report.pdf`.
