"""Dataset inspection, validation, cleaning, and daily aggregation."""

from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {
    "Date Time Served",
    "Bar Name",
    "Alcohol Type",
    "Brand Name",
    "Opening Balance (ml)",
    "Purchase (ml)",
    "Consumed (ml)",
    "Closing Balance (ml)",
}
NUMERIC_COLUMNS = [
    "Opening Balance (ml)",
    "Purchase (ml)",
    "Consumed (ml)",
    "Closing Balance (ml)",
]


def inspect_dataset(source: Path) -> dict:
    """Return factual schema and coverage information for the source workbook."""
    workbook = pd.ExcelFile(source)
    raw = pd.read_excel(source, sheet_name=workbook.sheet_names[0])
    return {
        "sheets": workbook.sheet_names,
        "rows": len(raw),
        "columns": list(raw.columns),
        "dtypes": {column: str(dtype) for column, dtype in raw.dtypes.items()},
        "missing_values": raw.isna().sum().to_dict(),
        "duplicate_rows": int(raw.duplicated().sum()),
        "date_min": str(raw["Date Time Served"].min()),
        "date_max": str(raw["Date Time Served"].max()),
        "bars": int(raw["Bar Name"].nunique()),
        "brands": int(raw["Brand Name"].nunique()),
        "categories": int(raw["Alcohol Type"].nunique()),
    }


def load_and_clean(source: Path) -> tuple[pd.DataFrame, dict]:
    """Load the workbook and apply deterministic quality checks."""
    raw = pd.read_excel(source, sheet_name="Dataset")
    missing_columns = sorted(REQUIRED_COLUMNS - set(raw.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    raw = raw.copy()
    raw["Date Time Served"] = pd.to_datetime(raw["Date Time Served"], errors="coerce")
    raw[NUMERIC_COLUMNS] = raw[NUMERIC_COLUMNS].apply(pd.to_numeric, errors="coerce")
    quality = {
        "rows_loaded": len(raw),
        "invalid_dates": int(raw["Date Time Served"].isna().sum()),
        "invalid_numeric_values": int(raw[NUMERIC_COLUMNS].isna().any(axis=1).sum()),
        "duplicate_rows": int(raw.duplicated().sum()),
        "negative_consumption": int((raw["Consumed (ml)"] < 0).sum()),
    }
    if quality["invalid_dates"] or quality["invalid_numeric_values"]:
        raise ValueError(f"Invalid dates or numeric values: {quality}")
    if quality["negative_consumption"]:
        raise ValueError(f"Negative consumption values found: {quality}")

    raw["conservation_error_ml"] = (
        raw["Opening Balance (ml)"]
        + raw["Purchase (ml)"]
        - raw["Consumed (ml)"]
        - raw["Closing Balance (ml)"]
    )
    raw["Date"] = raw["Date Time Served"].dt.floor("D")
    quality["max_conservation_error_ml"] = float(raw["conservation_error_ml"].abs().max())
    return raw, quality


def aggregate_daily(raw: pd.DataFrame) -> pd.DataFrame:
    """Aggregate transactions and complete every observed series across all dates."""
    daily = (
        raw.groupby(["Date", "Bar Name", "Alcohol Type", "Brand Name"], as_index=False)["Consumed (ml)"]
        .sum()
    )
    pairs = daily[["Bar Name", "Alcohol Type", "Brand Name"]].drop_duplicates()
    dates = pd.date_range(daily["Date"].min(), daily["Date"].max(), freq="D")
    grid = (
        pairs.assign(_key=1)
        .merge(pd.DataFrame({"Date": dates, "_key": 1}), on="_key")
        .drop(columns="_key")
    )
    return (
        grid.merge(daily, on=["Date", "Bar Name", "Alcohol Type", "Brand Name"], how="left")
        .fillna({"Consumed (ml)": 0.0})
        .sort_values(["Bar Name", "Alcohol Type", "Brand Name", "Date"])
        .reset_index(drop=True)
    )


def category_summary(raw: pd.DataFrame) -> pd.DataFrame:
    """Summarize demand by the observed alcohol category."""
    summary = (
        raw.groupby("Alcohol Type")["Consumed (ml)"]
        .agg(total_consumption_ml="sum", average_transaction_ml="mean", transactions="size")
        .sort_values("total_consumption_ml", ascending=False)
        .reset_index()
    )
    summary["consumption_share"] = summary["total_consumption_ml"] / summary["total_consumption_ml"].sum()
    return summary


def abc_segmentation(daily: pd.DataFrame) -> pd.DataFrame:
    """Classify bar-brand series by cumulative consumption."""
    annual = daily.groupby(["Bar Name", "Brand Name"])["Consumed (ml)"].sum().sort_values(ascending=False)
    result = annual.rename("annual_consumption_ml").to_frame()
    result["cumulative_share"] = result["annual_consumption_ml"].cumsum() / annual.sum()
    result["ABC_class"] = pd.cut(
        result["cumulative_share"], bins=[0, 0.80, 0.95, 1.0], labels=["A", "B", "C"], include_lowest=True
    )
    return result.reset_index()
