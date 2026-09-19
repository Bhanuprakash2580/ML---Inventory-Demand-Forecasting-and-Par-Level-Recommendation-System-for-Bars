"""Reproducible command-line pipeline for model and dashboard artifacts."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .data_preprocessing import abc_segmentation, aggregate_daily, category_summary, load_and_clean
from .forecasting import save_model, train_and_evaluate
from .par_level import build_recommendations

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Consumption Dataset.xlsx"
DATA_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"
OUTPUT_DIR = ROOT / "outputs"
FIGURE_DIR = ROOT / "report" / "figures"


def main():
    for directory in (DATA_DIR, MODEL_DIR, OUTPUT_DIR, FIGURE_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    raw, quality = load_and_clean(SOURCE)
    daily = aggregate_daily(raw)
    category = category_summary(raw)
    abc = abc_segmentation(daily)
    model, train, test, metrics = train_and_evaluate(daily)
    recommendations = build_recommendations(train, test)

    daily.to_csv(DATA_DIR / "daily_bar_consumption.csv", index=False)
    category.to_csv(DATA_DIR / "category_consumption.csv", index=False)
    abc.to_csv(DATA_DIR / "abc_inventory_segmentation.csv", index=False)
    metrics.to_csv(DATA_DIR / "forecast_metrics.csv")
    recommendations.to_csv(DATA_DIR / "par_level_recommendations.csv", index=False)
    metrics.to_csv(OUTPUT_DIR / "forecast_metrics.csv")
    recommendations.to_csv(OUTPUT_DIR / "inventory_recommendations.csv", index=False)
    category.to_csv(OUTPUT_DIR / "category_consumption.csv", index=False)
    save_model(model, MODEL_DIR / "forecasting_model.pkl")

    category.plot.barh(x="Alcohol Type", y="total_consumption_ml", legend=False, color="#167d8d")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "category_consumption.png", dpi=160)
    plt.close()
    metrics[["MAE_ml", "RMSE_ml"]].plot.bar(color=["#167d8d", "#e07a5f"])
    plt.ylabel("Error (ml)")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "forecast_model_comparison.png", dpi=160)
    plt.close()
    print(f"Loaded {quality['rows_loaded']:,} transactions")
    print(f"Daily rows: {len(daily):,} | Recommendations: {len(recommendations):,}")
    print(metrics.to_string())
    print(f"Model: {MODEL_DIR / 'forecasting_model.pkl'}")


if __name__ == "__main__":
    main()
