"""Configurable par-level recommendations."""

import numpy as np
import pandas as pd

from .evaluation import simulate_inventory


def compute_par_level(
    predicted_daily_demand,
    std_daily_demand,
    lead_time_days=2,
    review_period_days=1,
    service_level_z=1.645,
):
    """Return par level and safety stock for the coverage window."""
    coverage_days = lead_time_days + review_period_days
    expected_demand = max(0.0, float(predicted_daily_demand)) * coverage_days
    safety_stock = service_level_z * max(0.0, float(std_daily_demand)) * np.sqrt(coverage_days)
    return expected_demand + safety_stock, safety_stock


def build_recommendations(train, test, lead_time_days=2, review_period_days=1, service_level_z=1.645):
    group_columns = ["Bar Name", "Alcohol Type", "Brand Name"]
    series_stats = (
        train.groupby(group_columns)
        .agg(predicted_daily_demand=("rolling_mean_7", "mean"), std_daily_demand=("Consumed (ml)", "std"))
        .reset_index()
    )
    series_stats["std_daily_demand"] = series_stats["std_daily_demand"].fillna(0)
    series_stats[["par_level_ml", "safety_stock_ml"]] = series_stats.apply(
        lambda row: pd.Series(compute_par_level(
            row["predicted_daily_demand"], row["std_daily_demand"],
            lead_time_days, review_period_days, service_level_z,
        )), axis=1,
    )
    rows = []
    for keys, series in test.groupby(group_columns):
        key_filter = np.logical_and.reduce([series_stats[column].eq(value) for column, value in zip(group_columns, keys)])
        stat = series_stats.loc[key_filter].iloc[0]
        result = simulate_inventory(series["Consumed (ml)"].to_numpy(), stat["par_level_ml"], lead_time_days)
        rows.append({
            **dict(zip(group_columns, keys)),
            "forecast_method": "7-day moving average",
            "predicted_daily_demand_ml": stat["predicted_daily_demand"],
            "safety_stock_ml": stat["safety_stock_ml"],
            "par_level_ml": stat["par_level_ml"],
            "stockout_days": result["stockout_days"],
            "lost_volume_ml": result["lost_volume_ml"],
            "average_inventory_ml": result["average_inventory_ml"],
        })
    return pd.DataFrame(rows).sort_values("lost_volume_ml", ascending=False)
