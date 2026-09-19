# 3-5 Minute Video Walkthrough

## 0:00-0:45 | Business problem
- Show the project title and explain the stockout versus overstock tension.
- State that the decision unit is one brand at one bar, measured in milliliters.

## 0:45-1:45 | Data and forecast
- Open the notebook and show source validation, conservation checks, daily aggregation, and zero-demand completion.
- Show the daily demand and day-of-week charts.
- Explain the chronological split and compare the seasonal-naive baseline with the Random Forest lag model.

## 1:45-3:00 | Par level and simulation
- Explain `par = lead-time demand + safety stock` and the 95% service-level factor.
- Show the selected bar-brand forecast, par level, and inventory policy chart.
- Walk through receipt, consumption, reorder, and lost-demand logic.

## 3:00-4:00 | Business impact
- Show the model metric table and aggregate backtest metrics.
- Explain how managers use the recommendation as a daily reorder quantity.
- Call out assumptions: constant lead time, lost demand, and historical stockout censoring.

## 4:00-4:30 | Production and next steps
- Mention monitoring for WAPE, stockouts, lead-time variance, and data drift.
- Close with promotion/event features, vendor-specific lead times, and a manager dashboard as next improvements.
