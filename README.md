# Inventory Demand Forecasting and Par-Level Recommendation System for Bars

This project analyzes historical bar inventory movement data, forecasts item-level demand, recommends par levels, simulates replenishment, and presents the results through Streamlit.

## Project structure

```text
inventory-demand-forecasting/
├── data/
│   └── Consumption Dataset.xlsx
├── notebooks/
│   └── exploratory_analysis.ipynb
├── src/
│   ├── data_preprocessing.py
│   ├── forecasting.py
│   ├── par_level.py
│   └── evaluation.py
├── models/
│   └── forecasting_model.pkl
├── outputs/
│   └── inventory_recommendations.csv
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

## Dataset

`data/Consumption Dataset.xlsx` contains 6,575 transaction rows in the `Dataset` sheet. The observed fields are date/time served, bar, alcohol category, brand, opening balance, purchases, consumption, and closing balance in milliliters.

The preprocessing module validates dates and numeric values, checks duplicates and negative consumption, verifies the inventory conservation identity, aggregates daily bar-brand demand, and completes missing dates with zero demand where a series exists.

## Forecasting

The project uses a chronological 80/20 time split with no random shuffling. It compares:

- Seven-day moving average baseline used for the recommendation policy.
- Seven-day seasonal-naive challenger.
- Random Forest using lag consumption, rolling mean and standard deviation, weekday, month, weekend, bar, alcohol category, and brand features.

The evaluation reports MAE, RMSE, and WAPE. On the current dataset, the moving average has MAE 92.57 ml, RMSE 153.25 ml, and WAPE 166.35%. These are measured validation results, not guaranteed future accuracy.

## Par-level recommendation

For lead time `L`, review period `R`, forecast daily demand `d`, demand standard deviation `sigma`, and service-level z-score `z`:

```text
coverage demand = max(0, d) * (L + R)
safety stock = z * max(0, sigma) * sqrt(L + R)
par level = coverage demand + safety stock
```

The default is two lead-time days, one review-period day, and a 95% service target (`z = 1.645`). The recommendation file contains bar, alcohol category, brand, forecast method, forecast demand, safety stock, par level, stockout days, lost volume, and average inventory.

## Inventory simulation

The simulation starts at the par level, consumes validation demand, places an order when inventory position falls below par, receives orders after the configured lead time, and records ending inventory, stockout days, lost volume, and average inventory. Unmet demand is treated as lost sales. Results are simulated decision-support evidence, not real-world guarantees.

## Run locally

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Open `notebooks/exploratory_analysis.ipynb` for the narrated data analysis, visualizations, model comparison, par-level calculation, simulation walkthrough, recommendation generation, and model serialization. Run all notebook cells before opening the dashboard.

## Streamlit Community Cloud

Push the repository to GitHub, create a Streamlit Community Cloud app, select `app.py` as the main file, and use Python 3.10 or newer. The dashboard reads the committed workbook, model, and `outputs/inventory_recommendations.csv`.

## Limitations

Historical stockouts may censor observed demand. Promotions, events, weather, holidays, waste, vendor delays, and vendor-specific lead times are not modeled. Future improvements include event features, probabilistic forecasts, censored-demand correction, vendor lead-time data, and automated monitoring.
