# Inventory Demand Forecasting and Par-Level Recommendation System for Bars

An explainable ML system that analyzes transaction-level bar inventory data, forecasts item demand, recommends par levels, simulates replenishment, and exposes the results through a Streamlit dashboard.

## Business objective

Bar managers need enough product to protect availability without carrying unnecessary inventory. This project turns historical opening balance, purchases, consumption, and closing balance records into daily bar-brand demand signals and an operational reorder queue.

## Dataset

The source is `Consumption Dataset.xlsx`, containing 6,575 transaction rows in a `Dataset` sheet with:

- `Date Time Served`
- `Bar Name`
- `Alcohol Type`
- `Brand Name`
- Opening, purchase, consumed, and closing quantities in milliliters

The pipeline validates timestamps and numeric values, checks duplicates, rejects negative consumption, and verifies the conservation identity:

`Opening balance + purchase - consumed - closing balance = 0`

## Architecture

```text
Consumption Dataset.xlsx
        |
        v
src/data_preprocessing.py  -> cleaned daily series and category summaries
        |
        v
src/forecasting.py          -> leakage-safe features and time split models
        |
        +--> src/evaluation.py -> MAE, RMSE, WAPE, inventory simulation
        |
        v
src/par_level.py            -> demand coverage, safety stock, recommendations
        |
        v
src/pipeline.py             -> models/, outputs/, data/processed/, figures
        |
        v
app.py                      -> Streamlit control tower
```

## Forecasting method

The system compares three forecasts without randomly shuffling time series data:

1. A transparent seven-day moving average used for the operational recommendation.
2. A seven-day seasonal-naive challenger.
3. A Random Forest using lag 1/7/14, rolling mean and standard deviation, weekday, month, weekend, bar, category, and brand features.

The model uses a chronological 80/20 train/validation split. Metrics include MAE, RMSE, and WAPE. The results are measured on this dataset and are not claims about future production accuracy.

## Par-level formula

For lead time `L`, review period `R`, forecast daily demand `d`, demand standard deviation `sigma`, and service-level z-score `z`:

`coverage demand = max(0, forecast demand) * (L + R)`

`safety stock = z * max(0, sigma) * sqrt(L + R)`

`par level = coverage demand + safety stock`

The default policy uses two lead-time days, one review-period day, and a 95% service target with `z = 1.645`. These settings are configurable in `src/par_level.py`.

## Inventory simulation

The order-up-to simulation starts at the par level, consumes actual validation demand, places replenishment orders when inventory position falls below par, receives orders after lead time, and records stockout days, lost volume, and average inventory. Unmet demand is treated as lost sales. Simulation results are decision-support evidence, not guaranteed real-world performance.

## Project structure

```text
.
├── data/
│   └── processed/                  # notebook/pipeline-compatible intermediate outputs
├── notebooks/
│   └── inventory_forecasting_solution.ipynb
├── src/
│   ├── data_preprocessing.py
│   ├── evaluation.py
│   ├── forecasting.py
│   ├── par_level.py
│   └── pipeline.py
├── models/
│   └── forecasting_model.pkl
├── outputs/
│   ├── inventory_recommendations.csv
│   ├── forecast_metrics.csv
│   └── category_consumption.csv
├── report/figures/
├── app.py
├── requirements.txt
├── tests/test_pipeline.py
├── .gitignore
└── LICENSE
```

## Run locally

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m src.pipeline
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m streamlit run app.py
```

Open the notebook for the narrated analysis and generated figures. Run the pipeline whenever the source workbook changes. The dashboard consumes the generated CSV files and offers filters, model comparison, risk views, recommendation downloads, and the PDF report download.

## Streamlit Community Cloud

Push this repository to GitHub, create a Streamlit Community Cloud app, select `app.py` as the main file, and use Python 3.10 or newer. The committed workbook, model, and outputs allow the dashboard to open immediately; rerun `src.pipeline` locally when the source data changes.

## Limitations and future improvements

- Historical stockouts can censor observed demand.
- Promotions, events, weather, holidays, waste, and vendor delays are not modeled.
- Supplier lead time is constant rather than vendor-specific or probabilistic.
- Future work can add event features, probabilistic forecasts, censored-demand correction, vendor lead-time data, and automated monitoring.
