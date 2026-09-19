# Hotel Bar Inventory Forecasting and Par-Level Recommendation

This project combines a complete Jupyter Notebook recommendation system with an optional Streamlit control-tower dashboard for forecasting daily brand consumption across six hotel bars and recommending inventory par levels that cover supplier lead time plus a service-level safety buffer.

## Live Demo link: https://nnayvzb8xwhwvp7fwsdfjq.streamlit.app


## Quick start

1. Install Python 3.10+ and dependencies:

   ```powershell
   py -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. Open `notebooks/inventory_forecasting_solution.ipynb` in Jupyter or VS Code.
3. Run all cells. The notebook cleans the original transaction-level Excel workbook, trains and evaluates the models, creates recommendations, saves figures, and writes the Markdown/PDF business reports.
4. Launch the dashboard after running the notebook:

   ```powershell
   .venv\Scripts\python.exe -m streamlit run app.py
   ```

## Project layout

- `Consumption Dataset.xlsx`: original transaction-level source workbook.
- `notebooks/inventory_forecasting_solution.ipynb`: complete cleaning, visualization, modeling, evaluation, recommendation, and reporting workflow.
- `app.py`: Streamlit dashboard for filtering bars/brands, reviewing model health, and prioritizing stockout risk.
- `data/processed/daily_bar_consumption.csv`: generated daily bar-brand series from the workbook.
- `data/processed/forecast_metrics.csv`: validation MAE, RMSE, and WAPE.
- `data/processed/par_level_recommendations.csv`: bar-brand par levels and simulation metrics.
- `data/processed/abc_inventory_segmentation.csv`: A/B/C inventory priority classification.
- `report/figures/`: generated EDA, model comparison, and inventory-policy figures.
- `report/business_report.md` and `report/business_report.pdf`: generated managerial reports.

## Important assumptions

- Consumption is measured in milliliters and unmet demand is lost rather than backordered.
- Supplier lead time is configurable and defaults to 2 days.
- The forecast is evaluated chronologically; no random cross-validation is used.
- Par level is calculated as lead-time demand plus a 95% service-level safety stock.
- The simulation uses actual historical demand as the demand stream and does not use stock-constrained consumption to retrain the model.

## Current validation result

The 7-day baseline has WAPE 174.98% and RMSE 203.53 ml. The Random Forest has WAPE 176.66% and RMSE 148.19 ml. The Random Forest reduces large errors but is not better on aggregate absolute error, so the baseline remains a credible operational challenger.

The notebook remains the analysis and output-generation entry point; `app.py` is an optional user interface over its generated CSV outputs.
