"""Leakage-safe feature engineering and chronological demand forecasting."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .evaluation import evaluate_forecasts

CATEGORICAL_FEATURES = ["Bar Name", "Alcohol Type", "Brand Name"]
FEATURE_COLUMNS = [
    "lag_1", "lag_7", "lag_14", "rolling_mean_7", "rolling_std_7",
    "dayofweek", "month", "is_weekend", *CATEGORICAL_FEATURES,
]


def add_features(daily: pd.DataFrame) -> pd.DataFrame:
    model_df = daily.copy()
    grouped = model_df.groupby(["Bar Name", "Alcohol Type", "Brand Name"], sort=False)["Consumed (ml)"]
    for lag in (1, 7, 14):
        model_df[f"lag_{lag}"] = grouped.shift(lag)
    shifted = grouped.shift(1)
    model_df["rolling_mean_7"] = shifted.transform(lambda values: values.rolling(7, min_periods=3).mean())
    model_df["rolling_std_7"] = shifted.transform(lambda values: values.rolling(7, min_periods=3).std())
    model_df["dayofweek"] = model_df["Date"].dt.dayofweek
    model_df["month"] = model_df["Date"].dt.month
    model_df["is_weekend"] = model_df["dayofweek"].isin([5, 6]).astype(int)
    return model_df.dropna(subset=["lag_1", "lag_7", "lag_14", "rolling_mean_7", "rolling_std_7"]).copy()


def train_and_evaluate(daily: pd.DataFrame):
    """Fit Random Forest and compare moving-average/seasonal-naive baselines chronologically."""
    model_df = add_features(daily)
    cutoff = model_df["Date"].min() + (model_df["Date"].max() - model_df["Date"].min()) * 0.8
    train = model_df[model_df["Date"] < cutoff].copy()
    test = model_df[model_df["Date"] >= cutoff].copy()
    preprocess = ColumnTransformer(
        [("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES)],
        remainder="passthrough",
    )
    model = Pipeline([
        ("preprocess", preprocess),
        ("model", RandomForestRegressor(n_estimators=80, min_samples_leaf=3, random_state=42, n_jobs=-1)),
    ])
    model.fit(train[FEATURE_COLUMNS], train["Consumed (ml)"])
    test["7-day moving average"] = test["rolling_mean_7"].clip(lower=0)
    test["Seasonal naive (7 days)"] = test["lag_7"].clip(lower=0)
    test["Random Forest"] = np.maximum(0, model.predict(test[FEATURE_COLUMNS]))
    forecasts = {name: test[name] for name in ["7-day moving average", "Seasonal naive (7 days)", "Random Forest"]}
    metrics = evaluate_forecasts(test["Consumed (ml)"], forecasts)
    return model, train, test, metrics


def save_model(model, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
