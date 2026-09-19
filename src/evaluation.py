"""Forecast metrics and inventory-policy simulation."""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def wape(actual, forecast):
    denominator = np.abs(actual).sum()
    return float(np.abs(actual - forecast).sum() / denominator) if denominator else np.nan


def evaluate_forecasts(actual: pd.Series, forecasts: dict[str, pd.Series]) -> pd.DataFrame:
    """Calculate MAE, RMSE, and WAPE for named forecasts."""
    rows = {}
    for name, forecast in forecasts.items():
        rows[name] = {
            "MAE_ml": mean_absolute_error(actual, forecast),
            "RMSE_ml": mean_squared_error(actual, forecast) ** 0.5,
            "WAPE": wape(actual.to_numpy(), forecast.to_numpy()),
        }
    return pd.DataFrame.from_dict(rows, orient="index")


def simulate_inventory(actual_demand, par_level, lead_time_days=2):
    """Backtest an order-up-to policy; unmet demand is treated as lost sales."""
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
            pending.append((lead_time_days, par_level - inventory_position))
        history.append(stock)
    return {
        "stockout_days": stockout_days,
        "lost_volume_ml": lost_volume,
        "average_inventory_ml": float(np.mean(history)) if history else 0.0,
        "history": history,
    }
