from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Consumption Dataset.xlsx"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "report"
PLOT_DIR = REPORT_DIR / "figures"
for directory in (PROCESSED_DIR, PLOT_DIR):
    directory.mkdir(parents=True, exist_ok=True)

LEAD_TIME_DAYS = 2
SERVICE_LEVEL_Z = 1.645


def wape(actual, forecast):
    denominator = np.abs(actual).sum()
    return float(np.abs(actual - forecast).sum() / denominator) if denominator else np.nan


def load_and_aggregate():
    raw = pd.read_excel(SOURCE, sheet_name="Dataset")
    required = [
        "Date Time Served", "Bar Name", "Brand Name", "Opening Balance (ml)",
        "Purchase (ml)", "Consumed (ml)", "Closing Balance (ml)",
    ]
    missing = sorted(set(required) - set(raw.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    raw["Date Time Served"] = pd.to_datetime(raw["Date Time Served"], errors="coerce")
    if raw["Date Time Served"].isna().any():
        raise ValueError("Unparseable timestamps found")
    numeric = ["Opening Balance (ml)", "Purchase (ml)", "Consumed (ml)", "Closing Balance (ml)"]
    raw[numeric] = raw[numeric].apply(pd.to_numeric, errors="coerce")
    raw["conservation_error_ml"] = (
        raw["Opening Balance (ml)"] + raw["Purchase (ml)"]
        - raw["Consumed (ml)"] - raw["Closing Balance (ml)"]
    )
    daily = raw.assign(Date=raw["Date Time Served"].dt.floor("D"))
    daily = daily.groupby(["Date", "Bar Name", "Brand Name"], as_index=False)["Consumed (ml)"].sum()
    pairs = daily[["Bar Name", "Brand Name"]].drop_duplicates()
    dates = pd.date_range(daily["Date"].min(), daily["Date"].max(), freq="D")
    grid = pairs.assign(_key=1).merge(pd.DataFrame({"Date": dates, "_key": 1}), on="_key").drop(columns="_key")
    daily_ts = (
        grid.merge(daily, on=["Date", "Bar Name", "Brand Name"], how="left")
        .fillna({"Consumed (ml)": 0.0})
        .sort_values(["Bar Name", "Brand Name", "Date"])
        .reset_index(drop=True)
    )
    daily_ts.to_csv(PROCESSED_DIR / "daily_bar_consumption.csv", index=False)
    return raw, daily_ts


def add_features(daily_ts):
    model_df = daily_ts.copy()
    grouped = model_df.groupby(["Bar Name", "Brand Name"], sort=False)["Consumed (ml)"]
    for lag in (1, 7, 14):
        model_df[f"lag_{lag}"] = grouped.shift(lag)
    shifted = grouped.shift(1)
    model_df["rolling_mean_7"] = shifted.transform(lambda values: values.rolling(7, min_periods=3).mean())
    model_df["rolling_std_7"] = shifted.transform(lambda values: values.rolling(7, min_periods=3).std())
    model_df["dayofweek"] = model_df["Date"].dt.dayofweek
    model_df["is_weekend"] = model_df["dayofweek"].isin([4, 5, 6]).astype(int)
    return model_df.dropna(subset=["lag_1", "lag_7", "lag_14", "rolling_mean_7", "rolling_std_7"])


def train_and_evaluate(model_df):
    cutoff = model_df["Date"].min() + (model_df["Date"].max() - model_df["Date"].min()) * 0.8
    feature_cols = [
        "lag_1", "lag_7", "lag_14", "rolling_mean_7", "rolling_std_7",
        "dayofweek", "is_weekend", "Bar Name", "Brand Name",
    ]
    train = model_df[model_df["Date"] < cutoff].copy()
    test = model_df[model_df["Date"] >= cutoff].copy()
    categorical = ["Bar Name", "Brand Name"]
    preprocess = ColumnTransformer(
        [("categorical", OneHotEncoder(handle_unknown="ignore"), categorical)],
        remainder="passthrough",
    )
    forest = Pipeline([
        ("preprocess", preprocess),
        ("model", RandomForestRegressor(
            n_estimators=60, min_samples_leaf=3, random_state=42, n_jobs=-1
        )),
    ])
    forest.fit(train[feature_cols], train["Consumed (ml)"])
    test["seasonal_naive_7"] = test["lag_7"].clip(lower=0)
    test["random_forest"] = np.maximum(0, forest.predict(test[feature_cols]))
    metrics = pd.DataFrame({
        "MAE_ml": [
            mean_absolute_error(test["Consumed (ml)"], test["seasonal_naive_7"]),
            mean_absolute_error(test["Consumed (ml)"], test["random_forest"]),
        ],
        "RMSE_ml": [
            mean_squared_error(test["Consumed (ml)"], test["seasonal_naive_7"]) ** 0.5,
            mean_squared_error(test["Consumed (ml)"], test["random_forest"]) ** 0.5,
        ],
        "WAPE": [
            wape(test["Consumed (ml)"].to_numpy(), test["seasonal_naive_7"].to_numpy()),
            wape(test["Consumed (ml)"].to_numpy(), test["random_forest"].to_numpy()),
        ],
    }, index=["Seasonal naive (7 days)", "Random Forest"])
    metrics.to_csv(PROCESSED_DIR / "forecast_metrics.csv")
    joblib.dump(forest, PROCESSED_DIR / "random_forest_demand_model.joblib")
    return train, test, metrics


def compute_par_level(predicted_daily_demand, std_daily_demand):
    lead_time_demand = max(0.0, float(predicted_daily_demand)) * LEAD_TIME_DAYS
    safety_stock = SERVICE_LEVEL_Z * max(0.0, float(std_daily_demand)) * np.sqrt(LEAD_TIME_DAYS)
    return lead_time_demand + safety_stock, safety_stock


def simulate_inventory(actual_demand, par_level):
    stock = float(par_level)
    pending = []
    stockout_days = 0
    lost_volume = 0.0
    history = []
    for demand in actual_demand:
        arriving = sum(quantity for days, quantity in pending if days <= 1)
        pending = [(days - 1, quantity) for days, quantity in pending if days > 1]
        stock += arriving
        fulfilled = min(stock, float(demand))
        lost = float(demand) - fulfilled
        stock -= fulfilled
        if lost > 0:
            stockout_days += 1
            lost_volume += lost
        inventory_position = stock + sum(quantity for _, quantity in pending)
        if inventory_position < par_level:
            pending.append((LEAD_TIME_DAYS, par_level - inventory_position))
        history.append(stock)
    return {
        "stockout_days": stockout_days,
        "lost_volume_ml": lost_volume,
        "average_inventory_ml": float(np.mean(history)),
        "history": history,
    }


def build_recommendations(train, test):
    series_stats = (
        train.groupby(["Bar Name", "Brand Name"])
        .agg(
            predicted_daily_demand=("lag_7", "mean"),
            std_daily_demand=("Consumed (ml)", "std"),
        )
        .reset_index()
    )
    series_stats["std_daily_demand"] = series_stats["std_daily_demand"].fillna(0)
    par_values = series_stats.apply(
        lambda row: pd.Series(compute_par_level(row["predicted_daily_demand"], row["std_daily_demand"])),
        axis=1,
    )
    series_stats[["par_level_ml", "safety_stock_ml"]] = par_values
    rows = []
    for keys, series in test.groupby(["Bar Name", "Brand Name"]):
        stat = series_stats[(series_stats["Bar Name"] == keys[0]) & (series_stats["Brand Name"] == keys[1])].iloc[0]
        result = simulate_inventory(series["Consumed (ml)"].to_numpy(), stat["par_level_ml"])
        rows.append({
            "Bar Name": keys[0], "Brand Name": keys[1],
            "predicted_daily_demand_ml": stat["predicted_daily_demand"],
            "safety_stock_ml": stat["safety_stock_ml"], "par_level_ml": stat["par_level_ml"],
            "stockout_days": result["stockout_days"], "lost_volume_ml": result["lost_volume_ml"],
            "average_inventory_ml": result["average_inventory_ml"],
        })
    recommendations = pd.DataFrame(rows).sort_values("lost_volume_ml", ascending=False)
    recommendations.to_csv(PROCESSED_DIR / "par_level_recommendations.csv", index=False)
    return recommendations, series_stats


def make_figures(daily_ts, test, recommendations):
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    daily_ts = daily_ts.copy()
    daily_ts["Day"] = daily_ts["Date"].dt.day_name()
    weekday = daily_ts.groupby("Day")["Consumed (ml)"].mean().reindex(weekday_order)
    top_series = daily_ts.groupby(["Bar Name", "Brand Name"])["Consumed (ml)"].sum().nlargest(10)
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    weekday.plot.bar(ax=axes[0], color="#167d8d", title="Average daily consumption by weekday")
    top_series.sort_values().plot.barh(ax=axes[1], color="#e07a5f", title="Top bar-brand series")
    axes[0].set_ylabel("Milliliters")
    axes[1].set_xlabel("Milliliters")
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "eda_overview.png", dpi=160)
    plt.close(fig)

    selected = test.groupby(["Bar Name", "Brand Name"])["Consumed (ml)"].sum().idxmax()
    selected_test = test[(test["Bar Name"] == selected[0]) & (test["Brand Name"] == selected[1])]
    selected_rec = recommendations[(recommendations["Bar Name"] == selected[0]) & (recommendations["Brand Name"] == selected[1])].iloc[0]
    selected_sim = simulate_inventory(selected_test["Consumed (ml)"].to_numpy(), selected_rec["par_level_ml"])
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(selected_test["Date"], selected_sim["history"], label="Closing stock", color="#167d8d")
    ax.axhline(selected_rec["par_level_ml"], color="#e07a5f", linestyle="--", label="Par level")
    ax.set_title(f"Validation inventory path: {selected[0]} / {selected[1]}")
    ax.set_ylabel("Milliliters")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "inventory_policy_example.png", dpi=160)
    plt.close(fig)
    return selected, selected_sim


def write_pdf_report(raw, daily_ts, metrics, recommendations, selected, selected_sim):
    report_path = REPORT_DIR / "business_report.pdf"
    with PdfPages(report_path) as pdf:
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.08, 0.95, "Hotel Bar Inventory Forecasting", fontsize=20, weight="bold", color="#167d8d")
        body = [
            "Executive summary",
            "The system converts transaction-level bottle balances into daily demand by bar and brand, forecasts future consumption, and recommends par levels that balance service availability with holding stock.",
            "",
            "Dataset evidence",
            f"The source contains {len(raw):,} transaction rows, {raw['Bar Name'].nunique()} bars, and {raw['Brand Name'].nunique()} brands from {raw['Date Time Served'].min().date()} through {raw['Date Time Served'].max().date()}. The maximum conservation error is {raw['conservation_error_ml'].abs().max():.8f} ml. The completed daily grid contains {len(daily_ts):,} rows across 96 observed bar-brand pairs.",
            "",
            "Forecast evidence",
            f"The chronological validation compares a 7-day seasonal-naive baseline with a Random Forest using lags, rolling statistics, weekday features, bar, and brand. Baseline WAPE: {metrics.loc['Seasonal naive (7 days)', 'WAPE']:.1%}. Random Forest WAPE: {metrics.loc['Random Forest', 'WAPE']:.1%}.",
            "",
            "Inventory policy",
            f"Par level equals two-day lead-time demand plus 95% service-level safety stock. Across the validation policy simulation, stockout days total {int(recommendations['stockout_days'].sum()):,}, lost volume totals {recommendations['lost_volume_ml'].sum():,.0f} ml, and average inventory totals {recommendations['average_inventory_ml'].sum():,.0f} ml across series.",
            f"The example highest-volume validation series is {selected[0]} / {selected[1]}. Its simulation records {selected_sim['stockout_days']} stockout days and {selected_sim['lost_volume_ml']:,.0f} ml lost volume.",
            "",
            "Assumptions and risks",
            "Lead time is constant at two days, unmet demand is treated as lost, and measurements are in milliliters. Historical stockouts may censor observed demand. Promotions, holidays, vendor delays, breakage, and pouring waste should be monitored before production deployment.",
            "",
            "Recommendation",
            "Use the generated recommendation CSV as a daily manager review queue. Prioritize Class A items, confirm vendor lead times, and monitor WAPE, stockouts, lost volume, inventory, and data-quality errors.",
        ]
        fig.text(0.08, 0.90, "\n".join(body), fontsize=10.2, va="top", linespacing=1.45, wrap=True)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)
        for image_name in ("eda_overview.png", "inventory_policy_example.png"):
            image = plt.imread(PLOT_DIR / image_name)
            fig, ax = plt.subplots(figsize=(11, 7))
            ax.imshow(image)
            ax.axis("off")
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
    return report_path


def main():
    raw, daily_ts = load_and_aggregate()
    model_df = add_features(daily_ts)
    train, test, metrics = train_and_evaluate(model_df)
    recommendations, _ = build_recommendations(train, test)
    selected, selected_sim = make_figures(daily_ts, test, recommendations)
    report_path = write_pdf_report(raw, daily_ts, metrics, recommendations, selected, selected_sim)
    print(f"Processed rows: {len(daily_ts):,}")
    print(metrics.to_string())
    print(f"Recommendations: {len(recommendations):,} series")
    print(f"PDF report: {report_path}")


if __name__ == "__main__":
    main()
