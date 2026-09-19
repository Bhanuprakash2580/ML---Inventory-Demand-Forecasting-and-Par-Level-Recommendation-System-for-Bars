from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Bar Inventory Control Tower",
    page_icon="🍸",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "processed"

st.markdown(
    """
    <style>
    .block-container {max-width: 1400px; padding-top: 2rem;}
    [data-testid="stMetricValue"] {color: #167d8d;}
    .hero {background: linear-gradient(120deg, #073b4c, #167d8d); color: white; padding: 1.6rem 2rem; border-radius: 12px; margin-bottom: 1.2rem;}
    .hero h1 {margin: 0; font-size: 2.1rem;}
    .hero p {margin: .45rem 0 0; color: #d9f4f2;}
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data():
    recommendations = pd.read_csv(DATA_DIR / "par_level_recommendations.csv")
    metrics = pd.read_csv(DATA_DIR / "forecast_metrics.csv", index_col=0)
    daily = pd.read_csv(DATA_DIR / "daily_bar_consumption.csv", parse_dates=["Date"])
    return recommendations, metrics, daily

try:
    recommendations, metrics, daily = load_data()
except FileNotFoundError:
    st.error("Generated model outputs are missing. Run `python run_analysis.py` first.")
    st.stop()

st.markdown(
    '<div class="hero"><h1>Bar Inventory Control Tower</h1><p>Demand signals, par levels, and service-risk decisions across every hotel bar and brand.</p></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Decision filters")
    selected_bars = st.multiselect("Bars", sorted(recommendations["Bar Name"].unique()), default=sorted(recommendations["Bar Name"].unique()))
    selected_brands = st.multiselect("Brands", sorted(recommendations["Brand Name"].unique()), default=sorted(recommendations["Brand Name"].unique()))
    risk_only = st.checkbox("Show stockout-risk series only")
    selected_series = recommendations[
        recommendations["Bar Name"].isin(selected_bars) & recommendations["Brand Name"].isin(selected_brands)
    ].copy()
    if risk_only:
        selected_series = selected_series[selected_series["stockout_days"] > 0]

if selected_series.empty:
    st.warning("Select at least one bar and brand combination.")
    st.stop()

stockout_days = int(selected_series["stockout_days"].sum())
lost_volume = selected_series["lost_volume_ml"].sum()
average_inventory = selected_series["average_inventory_ml"].sum()
mean_par = selected_series["par_level_ml"].mean()

kpi = st.columns(4)
kpi[0].metric("Series in view", f"{len(selected_series):,}")
kpi[1].metric("Mean par level", f"{mean_par:,.0f} ml")
kpi[2].metric("Stockout days", f"{stockout_days:,}")
kpi[3].metric("Lost volume", f"{lost_volume:,.0f} ml")

left, right = st.columns([1.2, 1])
with left:
    st.subheader("Demand by weekday")
    chart_data = daily[daily["Bar Name"].isin(selected_bars) & daily["Brand Name"].isin(selected_brands)].copy()
    chart_data["Weekday"] = chart_data["Date"].dt.day_name()
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday = chart_data.groupby("Weekday")["Consumed (ml)"].mean().reindex(weekday_order)
    st.bar_chart(weekday)
with right:
    st.subheader("Forecast model comparison")
    display_metrics = metrics.rename(index={"Seasonal naive (7 days)": "Seasonal naive", "Random Forest": "Random Forest"}).copy()
    display_metrics["WAPE"] = display_metrics["WAPE"].map(lambda value: f"{value:.1%}")
    display_metrics["MAE_ml"] = display_metrics["MAE_ml"].map(lambda value: f"{value:,.1f}")
    display_metrics["RMSE_ml"] = display_metrics["RMSE_ml"].map(lambda value: f"{value:,.1f}")
    st.dataframe(display_metrics, use_container_width=True)
    st.caption("The Random Forest reduces RMSE, while the seasonal baseline has slightly lower WAPE on this dataset.")

st.subheader("Recommended par levels and service risk")
visible = selected_series.sort_values(["stockout_days", "lost_volume_ml"], ascending=False).copy()
visible["predicted_daily_demand_ml"] = visible["predicted_daily_demand_ml"].round(1)
visible["safety_stock_ml"] = visible["safety_stock_ml"].round(1)
visible["par_level_ml"] = visible["par_level_ml"].round(1)
visible["lost_volume_ml"] = visible["lost_volume_ml"].round(1)
visible["average_inventory_ml"] = visible["average_inventory_ml"].round(1)
st.dataframe(visible, use_container_width=True, hide_index=True)

st.subheader("Highest-risk bar-brand series")
risk = selected_series.nlargest(10, "lost_volume_ml").copy()
risk["Series"] = risk["Bar Name"] + " / " + risk["Brand Name"]
fig, ax = plt.subplots(figsize=(12, 4.5))
ax.barh(risk["Series"].iloc[::-1], risk["lost_volume_ml"].iloc[::-1], color="#e07a5f")
ax.set_xlabel("Lost demand volume (ml)")
ax.set_ylabel("")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
st.pyplot(fig)

st.caption(f"Inventory position is simulated with a {2}-day lead time and a 95% service-level safety buffer. Total average inventory across selected series: {average_inventory:,.0f} ml.")
