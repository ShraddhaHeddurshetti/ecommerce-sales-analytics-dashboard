import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# Allow imports from project root when running via `streamlit run app/dashboard.py`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingest import load_all
from src.clean import run_cleaning
from src.transform import (
    get_master_df,
    monthly_revenue,
    top_categories,
    revenue_by_state,
    headline_kpis,
)

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown(
    """
    <style>
    [data-testid="metric-container"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Load Data (cached) ────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    raw = load_all()
    cleaned = run_cleaning(raw)
    master = get_master_df(
        cleaned["orders"],
        cleaned["items"],
        cleaned["customers"],
        cleaned["products"],
    )
    return cleaned, master


# ── Data check ───────────────────────────────────────────────
DATA_MISSING = not os.path.exists("data/raw/olist_orders_dataset.csv")

if DATA_MISSING:
    st.warning(
        "⚠️ **Dataset not found in `data/raw/`.**\n\n"
        "Download the Olist Brazilian E-Commerce dataset from Kaggle and place the CSV files in `data/raw/`.\n\n"
        "```\n"
        "kaggle datasets download -d olistbr/brazilian-ecommerce --unzip -p data/raw/\n"
        "```"
    )
    st.stop()

cleaned, master = load_data()

# ── Sidebar Filters ───────────────────────────────────────────
st.sidebar.header("🎛 Filters")

months = sorted(master["order_month"].astype(str).unique())
selected_months = st.sidebar.select_slider(
    "Date Range",
    options=months,
    value=(months[0], months[-1]),
)

states = ["All"] + sorted(master["customer_state"].dropna().unique())
selected_state = st.sidebar.selectbox("Customer State", states)

categories_available = sorted(master["category_en"].dropna().unique())
selected_category = st.sidebar.multiselect("Category (multi-select)", categories_available)

# Apply filters
filtered = master.copy()
filtered = filtered[
    (filtered["order_month"].astype(str) >= selected_months[0])
    & (filtered["order_month"].astype(str) <= selected_months[1])
]
if selected_state != "All":
    filtered = filtered[filtered["customer_state"] == selected_state]
if selected_category:
    filtered = filtered[filtered["category_en"].isin(selected_category)]

# ── Header ────────────────────────────────────────────────────
st.title("📦 E-Commerce Sales Dashboard")
st.caption(
    f"Showing **{filtered['order_id'].nunique():,}** orders · "
    f"**{filtered['customer_id'].nunique():,}** customers"
)

# ── KPI Cards ────────────────────────────────────────────────
kpis = headline_kpis(filtered, cleaned["orders"])
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Revenue",       f"R${kpis['total_revenue']:,.0f}")
col2.metric("📦 Orders",        f"{kpis['total_orders']:,}")
col3.metric("🛒 AOV",           f"R${kpis['aov']:,.1f}")
col4.metric("🔁 Repeat Rate",   f"{kpis['repeat_rate']:.1f}%")
col5.metric("🚚 Avg Delivery",  f"{kpis['avg_delivery_days']:.0f} days")

st.divider()

# ── Charts Row 1 ──────────────────────────────────────────────
col_l, col_r = st.columns([2, 1])

with col_l:
    st.subheader("📈 Monthly Revenue")
    rev_df = monthly_revenue(filtered)
    fig = px.line(
        rev_df, x="order_month", y="revenue",
        markers=True, color_discrete_sequence=["#6366f1"],
    )
    fig.update_layout(
        xaxis_title="", yaxis_title="Revenue (R$)",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.subheader("📊 Order Status")
    status_df = cleaned["orders"]["order_status"].value_counts().reset_index()
    status_df.columns = ["order_status", "count"]
    fig2 = px.pie(
        status_df, names="order_status", values="count",
        color_discrete_sequence=px.colors.sequential.Purples_r,
    )
    fig2.update_layout(showlegend=True)
    st.plotly_chart(fig2, use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────────
col_l2, col_r2 = st.columns([1, 1])

with col_l2:
    st.subheader("🏆 Top 10 Categories")
    cat_df = top_categories(filtered)
    fig3 = px.bar(
        cat_df, x="revenue", y="category_en", orientation="h",
        color="revenue", color_continuous_scale="Purples",
    )
    fig3.update_layout(
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig3, use_container_width=True)

with col_r2:
    st.subheader("🗺 Revenue by State")
    state_df = revenue_by_state(filtered)
    fig4 = px.choropleth(
        state_df,
        geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        locations="customer_state",
        featureidkey="properties.sigla",
        color="revenue",
        color_continuous_scale="Purples",
        scope="south america",
    )
    fig4.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig4, use_container_width=True)

# ── Review Score Trend ────────────────────────────────────────
st.subheader("⭐ Avg Review Score by Month")
if "reviews" in cleaned and "order_month" in cleaned["orders"].columns:
    reviews_merged = cleaned["reviews"].merge(
        cleaned["orders"][["order_id", "order_month"]], on="order_id", how="left"
    )
    reviews_merged["order_month"] = reviews_merged["order_month"].astype(str)
    review_trend = (
        reviews_merged.groupby("order_month")["review_score"]
        .mean()
        .reset_index()
        .rename(columns={"review_score": "avg_score"})
    )
    fig5 = px.line(
        review_trend, x="order_month", y="avg_score",
        markers=True, color_discrete_sequence=["#10b981"],
    )
    fig5.update_layout(
        xaxis_title="", yaxis_title="Avg Review Score",
        yaxis=dict(range=[1, 5]),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig5, use_container_width=True)

# ── Raw Data Table ────────────────────────────────────────────
with st.expander("🔍 View Raw Data (first 200 rows)"):
    st.dataframe(filtered.head(200), use_container_width=True)

# ── Footer ────────────────────────────────────────────────────
st.divider()
st.caption("Dataset: Olist Brazilian E-Commerce | Built with Streamlit + Plotly")
