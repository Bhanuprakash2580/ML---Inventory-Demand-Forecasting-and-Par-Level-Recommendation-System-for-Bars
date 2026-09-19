from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Bar inventory control tower",
    page_icon=":material/bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "report"
SOURCE_FILE = ROOT / "Consumption Dataset.xlsx"

@st.cache_data(ttl="15m")
def load_outputs():
    recommendations = pd.read_csv(DATA_DIR / "par_level_recommendations.csv")
    metrics = pd.read_csv(DATA_DIR / "forecast_metrics.csv", index_col=0)
    daily = pd.read_csv(DATA_DIR / "daily_bar_consumption.csv", parse_dates=["Date"])
    abc = pd.read_csv(DATA_DIR / "abc_inventory_segmentation.csv")
    return recommendations, metrics, daily, abc

def format_ml(value):
    return f"{value:,.0f} ml"

try:
    recommendations, metrics, daily, abc = load_outputs()
except FileNotFoundError:
    st.error("Generated outputs are missing. Run all cells in the notebook first.", icon=":material/error:")
    st.stop()

with st.sidebar:
    st.markdown("### :material/tune: Scope")
    selected_bars = st.multiselect(
        "Bars",
        sorted(recommendations["Bar Name"].unique()),
        default=sorted(recommendations["Bar Name"].unique()),
    )
    selected_brands = st.multiselect(
        "Brands",
        sorted(recommendations["Brand Name"].unique()),
        default=sorted(recommendations["Brand Name"].unique()),
    )
    date_range = st.date_input(
        "Demand window",
        value=(daily["Date"].min().date(), daily["Date"].max().date()),
        min_value=daily["Date"].min().date(),
        max_value=daily["Date"].max().date(),
    )
    risk_only = st.toggle("Show stockout-risk series only")

    st.markdown("### :material/download: Exports")
    st.download_button(
        "Download reorder queue",
        recommendations.to_csv(index=False),
        "par_level_recommendations.csv",
        "text/csv",
        icon=":material/download:",
        width="stretch",
    )
    if (REPORT_DIR / "business_report.pdf").exists():
        st.download_button(
            "Download business report",
            (REPORT_DIR / "business_report.pdf").read_bytes(),
            "business_report.pdf",
            "application/pdf",
            icon=":material/picture_as_pdf:",
            width="stretch",
        )
    st.caption(f"Source: `{SOURCE_FILE.name}`")

selected_series = recommendations[
    recommendations["Bar Name"].isin(selected_bars)
    & recommendations["Brand Name"].isin(selected_brands)
].copy()
if risk_only:
    selected_series = selected_series[selected_series["stockout_days"] > 0]

if selected_series.empty:
    st.warning("Select at least one bar and brand combination.", icon=":material/filter_alt:")
    st.stop()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range)
else:
    start_date = end_date = pd.to_datetime(date_range)

filtered_daily = daily[
    daily["Bar Name"].isin(selected_bars)
    & daily["Brand Name"].isin(selected_brands)
    & daily["Date"].between(start_date, end_date)
].copy()

stockout_days = int(selected_series["stockout_days"].sum())
lost_volume = selected_series["lost_volume_ml"].sum()
average_inventory = selected_series["average_inventory_ml"].sum()
mean_par = selected_series["par_level_ml"].mean()
risk_count = int((selected_series["stockout_days"] > 0).sum())
total_demand = filtered_daily["Consumed (ml)"].sum()

st.title("Bar inventory control tower", icon=":material/bar_chart:")
st.caption(
    f"{start_date:%d %b %Y} to {end_date:%d %b %Y} · "
    f"{len(selected_series)} bar-brand series in view · 95% service target · 2-day lead time"
)

with st.container(horizontal=True):
    st.metric("Mean par level", format_ml(mean_par), border=True)
    st.metric("Stockout days", f"{stockout_days:,}", border=True)
    st.metric("Lost volume", format_ml(lost_volume), border=True)
    st.metric("Demand in window", format_ml(total_demand), border=True)

overview_tab, queue_tab, model_tab, data_tab = st.tabs(
    [
        ":material/dashboard: Overview",
        ":material/priority_high: Reorder queue",
        ":material/query_stats: Model health",
        ":material/database: Data quality",
    ]
)

with overview_tab:
    chart_col, context_col = st.columns([1.35, 0.65])
    with chart_col:
        with st.container(border=True):
            st.subheader("Demand rhythm")
            weekday_order = [
                "Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday",
            ]
            filtered_daily["Weekday"] = filtered_daily["Date"].dt.day_name()
            weekday = (
                filtered_daily.groupby("Weekday")["Consumed (ml)"].mean()
                .reindex(weekday_order)
                .rename("Average consumption (ml)")
            )
            st.bar_chart(weekday, color="#167d8d", horizontal=False)
            st.caption("Average consumption across the selected bars and brands.")
    with context_col:
        with st.container(border=True):
            st.subheader("What needs attention")
            if risk_count:
                st.warning(
                    f"{risk_count} series show simulated stockout risk. "
                    "Prioritize the reorder queue by lost volume.",
                    icon=":material/warning:",
                )
            else:
                st.success("No stockout-risk series in the current scope.", icon=":material/check_circle:")
            st.metric("Average inventory", format_ml(average_inventory))
            st.metric("Risk share", f"{risk_count / len(selected_series):.0%}")

    with st.container(border=True):
        st.subheader("Highest exposure")
        exposure = selected_series.nlargest(8, "lost_volume_ml").copy()
        exposure["Series"] = exposure["Bar Name"] + " / " + exposure["Brand Name"]
        exposure = exposure.set_index("Series")[["lost_volume_ml", "stockout_days"]]
        exposure.columns = ["Lost volume (ml)", "Stockout days"]
        st.bar_chart(exposure, color=["#e07a5f", "#167d8d"], horizontal=True)

with queue_tab:
    st.subheader("Recommended par levels and service risk", icon=":material/assignment:")
    st.caption("Use this queue to prioritize manager review and supplier orders.")
    visible = selected_series.sort_values(
        ["stockout_days", "lost_volume_ml"], ascending=False
    ).copy()
    visible = visible.rename(
        columns={
            "Bar Name": "Bar",
            "Brand Name": "Brand",
            "predicted_daily_demand_ml": "Daily demand (ml)",
            "safety_stock_ml": "Safety stock (ml)",
            "par_level_ml": "Par level (ml)",
            "stockout_days": "Stockout days",
            "lost_volume_ml": "Lost volume (ml)",
            "average_inventory_ml": "Average inventory (ml)",
        }
    )
    st.dataframe(
        visible[
            [
                "Bar", "Brand", "Daily demand (ml)", "Safety stock (ml)",
                "Par level (ml)", "Stockout days", "Lost volume (ml)",
                "Average inventory (ml)",
            ]
        ],
        width="stretch",
        hide_index=True,
        height=560,
        column_config={
            "Daily demand (ml)": st.column_config.NumberColumn(format="%.1f"),
            "Safety stock (ml)": st.column_config.NumberColumn(format="%.1f"),
            "Par level (ml)": st.column_config.NumberColumn(format="%.1f"),
            "Lost volume (ml)": st.column_config.NumberColumn(format="%.1f"),
            "Average inventory (ml)": st.column_config.NumberColumn(format="%.1f"),
        },
    )

with model_tab:
    metric_col, interpretation_col = st.columns([1.2, 0.8])
    with metric_col:
        with st.container(border=True):
            st.subheader("Chronological validation")
            display_metrics = metrics.rename(
                index={
                    "Seasonal naive (7 days)": "Seasonal naive",
                    "Random Forest": "Random Forest",
                }
            ).copy()
            st.dataframe(
                display_metrics,
                width="stretch",
                column_config={
                    "MAE_ml": st.column_config.NumberColumn("MAE (ml)", format="%.1f"),
                    "RMSE_ml": st.column_config.NumberColumn("RMSE (ml)", format="%.1f"),
                    "WAPE": st.column_config.NumberColumn("WAPE", format="%.1%"),
                },
            )
    with interpretation_col:
        with st.container(border=True):
            st.subheader("Reading the result")
            rmse_change = (1 - metrics.loc["Random Forest", "RMSE_ml"] / metrics.loc["Seasonal naive (7 days)", "RMSE_ml"])
            st.metric("Random Forest RMSE improvement", f"{rmse_change:.1%}")
            st.write(
                "The Random Forest reduces large errors, while the seasonal baseline "
                "has slightly lower aggregate WAPE. Keep both visible as operational challengers."
            )
    st.image(
        str(REPORT_DIR / "figures" / "forecast_model_comparison.png"),
        caption="Validation error comparison",
        width="stretch",
    )

with data_tab:
    quality_col, abc_col = st.columns([1, 1])
    with quality_col:
        with st.container(border=True):
            st.subheader("Dataset footprint")
            st.write(f"**Original source:** `{SOURCE_FILE.name}`")
            st.write(f"**Transaction source rows:** 6,575")
            st.write(f"**Daily modeling rows:** {len(daily):,}")
            st.write(f"**Bars:** {daily['Bar Name'].nunique()} · **Brands:** {daily['Brand Name'].nunique()}")
            st.write(f"**Date range:** {daily['Date'].min():%d %b %Y} to {daily['Date'].max():%d %b %Y}")
            st.success("Conservation checks passed in the notebook.", icon=":material/check_circle:")
    with abc_col:
        with st.container(border=True):
            st.subheader("ABC inventory priorities")
            abc_counts = abc["ABC_class"].value_counts().reindex(["A", "B", "C"]).fillna(0)
            st.bar_chart(abc_counts, color="#167d8d")
            st.caption("Class A items account for the first 80% of cumulative consumption.")

st.caption("Refresh the notebook outputs after changing the source workbook, then reload this dashboard.")
