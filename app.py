from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Bar Inventory Control Tower", page_icon="🍸", layout="wide")

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "processed"

st.markdown(
    """
    <style>
    .block-container {max-width: 1480px; padding: 2.4rem 3rem 3rem;}
    [data-testid="stSidebar"] {border-right: 1px solid rgba(125, 139, 156, .22);}
    [data-testid="stMetric"] {background: rgba(22, 125, 141, .08); border: 1px solid rgba(22, 125, 141, .2); border-radius: 10px; padding: 1rem 1.1rem;}
    [data-testid="stMetricLabel"] {font-size: .78rem; text-transform: uppercase; letter-spacing: .08em;}
    [data-testid="stMetricValue"] {color: #167d8d; font-size: 1.55rem;}
    .masthead {display:flex; justify-content:space-between; align-items:flex-end; gap:2rem; border-bottom:1px solid rgba(125,139,156,.28); padding-bottom:1.25rem; margin-bottom:1.5rem;}
    .eyebrow {color:#e07a5f; font-size:.75rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; margin:0 0 .45rem;}
    .masthead h1 {font-size:2.35rem; line-height:1.05; margin:0; letter-spacing:-.02em;}
    .masthead p {color:#78909c; margin:.6rem 0 0; max-width:720px;}
    .as-of {color:#78909c; font-size:.82rem; text-align:right; white-space:nowrap;}
    .section-kicker {color:#78909c; font-size:.73rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; margin:.2rem 0 .4rem;}
    .risk-note {border-left:4px solid #e07a5f; background:rgba(224,122,95,.1); border-radius:0 8px 8px 0; padding:.7rem 1rem; margin:.5rem 0 1rem;}
    div[data-testid="stDataFrame"] {border:1px solid rgba(125,139,156,.24); border-radius:8px; overflow:hidden;}
    @media (max-width: 900px) {
        .block-container {padding: 1.4rem 1rem 2rem;}
        .masthead {display:block;}
        .masthead h1 {font-size:1.8rem;}
        .as-of {margin-top:1rem; text-align:left; white-space:normal;}
    }
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
    '<div class="masthead"><div><p class="eyebrow">Operations / Inventory intelligence</p><h1>Bar Inventory Control Tower</h1><p>Turn demand signals into confident reorder decisions across every hotel bar and brand.</p></div><div class="as-of">MODEL RUN<br><strong>95% service target · 2-day lead time</strong></div></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("<p class='section-kicker'>Scope</p>", unsafe_allow_html=True)
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

st.markdown("<p class='section-kicker'>Portfolio pulse</p>", unsafe_allow_html=True)
kpi = st.columns(4, gap="medium")
kpi[0].metric("Series in view", f"{len(selected_series):,}", "bar x brand combinations")
kpi[1].metric("Mean par level", f"{mean_par:,.0f} ml", "lead-time demand + buffer")
kpi[2].metric("Stockout days", f"{stockout_days:,}", "validation simulation")
kpi[3].metric("Lost volume", f"{lost_volume:,.0f} ml", "unfulfilled demand")

tab_overview, tab_queue, tab_model = st.tabs(["Overview", "Reorder queue", "Model health"])

with tab_overview:
    left, right = st.columns([1.15, .85], gap="large")
    with left:
        st.markdown("<p class='section-kicker'>Demand rhythm</p>", unsafe_allow_html=True)
        st.subheader("Average consumption by weekday")
        chart_data = daily[daily["Bar Name"].isin(selected_bars) & daily["Brand Name"].isin(selected_brands)].copy()
        chart_data["Weekday"] = chart_data["Date"].dt.day_name()
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday = chart_data.groupby("Weekday")["Consumed (ml)"].mean().reindex(weekday_order)
        st.bar_chart(weekday, color="#167d8d", height=310)
    with right:
        st.markdown("<p class='section-kicker'>Decision context</p>", unsafe_allow_html=True)
        st.subheader("What needs attention")
        risk_count = int((selected_series["stockout_days"] > 0).sum())
        st.markdown(f'<div class="risk-note"><strong>{risk_count} series</strong> show simulated stockout risk in the selected scope.<br>Use the reorder queue to prioritize lost-volume exposure first.</div>', unsafe_allow_html=True)
        st.write(f"Average simulated inventory is **{average_inventory:,.0f} ml** across the selected series.")
        st.write("The policy uses a 95% service target with a two-day supplier lead time.")

with tab_queue:
    st.markdown("<p class='section-kicker'>Action list</p>", unsafe_allow_html=True)
    st.subheader("Recommended par levels and service risk")
    st.caption("Sorted by stockout exposure. Use this queue to focus manager review and supplier orders.")
    visible = selected_series.sort_values(["stockout_days", "lost_volume_ml"], ascending=False).rename(columns={
        "Bar Name": "Bar", "Brand Name": "Brand", "predicted_daily_demand_ml": "Daily demand (ml)",
        "safety_stock_ml": "Safety stock (ml)", "par_level_ml": "Par level (ml)",
        "stockout_days": "Stockout days", "lost_volume_ml": "Lost volume (ml)",
        "average_inventory_ml": "Avg inventory (ml)",
    })
    st.dataframe(
        visible[["Bar", "Brand", "Daily demand (ml)", "Safety stock (ml)", "Par level (ml)", "Stockout days", "Lost volume (ml)", "Avg inventory (ml)"]],
        width="stretch",
        hide_index=True,
        height=520,
        column_config={
            "Daily demand (ml)": st.column_config.NumberColumn(format="%.1f"),
            "Safety stock (ml)": st.column_config.NumberColumn(format="%.1f"),
            "Par level (ml)": st.column_config.NumberColumn(format="%.1f"),
            "Lost volume (ml)": st.column_config.NumberColumn(format="%.1f"),
            "Avg inventory (ml)": st.column_config.NumberColumn(format="%.1f"),
        },
    )

with tab_model:
    st.markdown("<p class='section-kicker'>Forecast evaluation</p>", unsafe_allow_html=True)
    st.subheader("Baseline versus Random Forest")
    display_metrics = metrics.rename(index={"Seasonal naive (7 days)": "Seasonal naive", "Random Forest": "Random Forest"}).copy()
    display_metrics["WAPE"] = display_metrics["WAPE"].map(lambda value: f"{value:.1%}")
    display_metrics["MAE_ml"] = display_metrics["MAE_ml"].map(lambda value: f"{value:,.1f} ml")
    display_metrics["RMSE_ml"] = display_metrics["RMSE_ml"].map(lambda value: f"{value:,.1f} ml")
    st.dataframe(display_metrics, width="stretch")
    st.caption("The Random Forest reduces RMSE, while the seasonal baseline has slightly lower WAPE on this dataset. Both remain useful operational challengers.")

st.markdown("<p class='section-kicker'>Risk concentration</p>", unsafe_allow_html=True)
st.subheader("Highest-risk bar-brand series")
risk = selected_series.nlargest(10, "lost_volume_ml").copy()
risk["Series"] = risk["Bar Name"] + " / " + risk["Brand Name"]
fig, ax = plt.subplots(figsize=(12, 4.5))
ax.barh(risk["Series"].iloc[::-1], risk["lost_volume_ml"].iloc[::-1], color="#e07a5f")
ax.set_xlabel("Lost demand volume (ml)")
ax.set_ylabel("")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
st.pyplot(fig, width="stretch")

st.caption(f"Inventory position is simulated with a 2-day lead time and a 95% service-level safety buffer. Total average inventory across selected series: {average_inventory:,.0f} ml.")
