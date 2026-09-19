# Hotel Bar Inventory Forecasting and Par Level Recommendation

This project forecasts daily brand consumption for six hotel bars and recommends inventory par levels that cover supplier lead time plus a service-level safety buffer.

## Quick start

1. Install Python 3.10+ and dependencies:

   ```powershell
   py -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. Run the reproducible pipeline with `.venv\Scripts\python.exe run_analysis.py`.
3. Open `notebooks/inventory_forecasting_solution.ipynb` in Jupyter or VS Code for the interactive walkthrough.
4. Launch the dashboard locally:

   ```powershell
   .venv\Scripts\python.exe -m streamlit run app.py
   ```

## Project layout

- `Consumption Dataset.xlsx`: supplied source workbook.
- `notebooks/inventory_forecasting_solution.ipynb`: complete analysis and modeling deliverable.
- `run_analysis.py`: reproducible command-line pipeline used to generate outputs.
- `data/processed/daily_bar_consumption.csv`: generated daily bar-brand series.
- `data/processed/forecast_metrics.csv`: validation MAE, RMSE, and WAPE.
- `data/processed/par_level_recommendations.csv`: bar-brand par levels and simulation metrics.
- `report/business_report.md`: managerial summary, assumptions, trade-offs, and failure modes.
- `report/business_report.pdf`: generated executive report with measured results and figures.
- `app.py`: Streamlit control-tower dashboard for filters, metrics, risk, and par levels.
- `data/processed/random_forest_demand_model.joblib`: trained Random Forest deployment artifact.
- `video_script/video_walkthrough_outline.md`: 3-5 minute presentation outline.

## Important assumptions

- Consumption is measured in milliliters and unmet demand is lost rather than backordered.
- Supplier lead time is configurable and defaults to 2 days.
- The forecast is evaluated chronologically; no random cross-validation is used.
- Par level is calculated as lead-time demand plus a 95% service-level safety stock.
- The simulation uses actual historical demand as the demand stream and does not use stock-constrained consumption to retrain the model.

## Current validation result

The 7-day baseline has WAPE 174.98% and RMSE 203.53 ml. The Random Forest has WAPE 176.66% and RMSE 148.19 ml. The Random Forest reduces large errors but is not better on aggregate absolute error, so the baseline remains a credible operational challenger.

## Streamlit Community Cloud

Push the repository to GitHub, open [Streamlit Community Cloud](https://share.streamlit.io/), choose the repository and branch, set the main file to `app.py`, and deploy. The app reads the committed files under `data/processed/`; run `run_analysis.py` before pushing whenever the source dataset changes.
