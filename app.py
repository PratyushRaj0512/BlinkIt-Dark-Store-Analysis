"""
app.py -- Blinkit Lucknow Dark Store Intelligence Dashboard (v2)
==================================================================

Expects data files created by generate_data.py / build_database.py /
allocation_engine.py to exist in ../data/
"""

import time
import sqlite3
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Blinkit Lucknow | Dark Store Intelligence",
    page_icon="🟡",
    layout="wide",
    initial_sidebar_state="expanded",
)

BLINKIT_YELLOW = "#F8CB46"
BLINKIT_YELLOW_LIGHT = "#FFE580"
BLINKIT_BLACK = "#0C0C0C"
BLINKIT_DARK_GREY = "#1A1A1A"
ACCENT_GREEN = "#0ECB81"
ACCENT_RED = "#FF4D4D"

# ------------------------------------------------------------------
# CUSTOM CSS -- Blinkit-branded fonts, colors, animated interactions
# ------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Poppins:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Poppins', sans-serif;
}}
h1, h2, h3, .section-title, .main-header h1 {{
    font-family: 'Baloo 2', sans-serif;
}}

.stApp {{
    background: radial-gradient(circle at 20% 0%, #1a1a1a 0%, {BLINKIT_BLACK} 55%);
}}

/* Header banner -- Blinkit yellow */
.main-header {{
    padding: 30px 34px;
    border-radius: 20px;
    background: linear-gradient(120deg, {BLINKIT_YELLOW} 0%, {BLINKIT_YELLOW_LIGHT} 100%);
    box-shadow: 0 10px 34px rgba(248, 203, 70, 0.30);
    margin-bottom: 22px;
    animation: fadeInDown 0.7s ease-out;
    position: relative;
    overflow: hidden;
}}
.main-header::after {{
    content: "";
    position: absolute;
    top: -50%; right: -10%;
    width: 260px; height: 260px;
    background: rgba(12,12,12,0.06);
    border-radius: 50%;
}}
.main-header h1 {{
    color: {BLINKIT_BLACK};
    font-weight: 800;
    font-size: 36px;
    margin: 0;
    letter-spacing: -0.5px;
}}
.main-header p {{
    color: #262626;
    font-size: 15px;
    margin-top: 8px;
    font-weight: 600;
}}
@keyframes fadeInDown {{
    from {{opacity: 0; transform: translateY(-18px);}}
    to {{opacity: 1; transform: translateY(0);}}
}}

/* KPI Cards */
.kpi-card {{
    background: linear-gradient(155deg, #191919 0%, #111111 100%);
    border: 1px solid rgba(248, 203, 70, 0.18);
    border-radius: 18px;
    padding: 20px 22px;
    transition: all 0.3s cubic-bezier(.25,.8,.25,1);
    animation: fadeInUp 0.8s ease-out;
}}
.kpi-card:hover {{
    transform: translateY(-6px) scale(1.015);
    border: 1px solid {BLINKIT_YELLOW};
    box-shadow: 0 14px 30px rgba(248, 203, 70, 0.22);
}}
.kpi-label {{ color: #9a9a9a; font-size: 12.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; }}
.kpi-value {{ color: #ffffff; font-size: 29px; font-weight: 800; margin-top: 6px; font-family: 'Baloo 2', sans-serif; }}
.kpi-value.accent {{ color: {BLINKIT_YELLOW}; }}
.kpi-delta-good {{ color: {ACCENT_GREEN}; font-size: 13px; font-weight: 700; margin-top: 4px; }}
.kpi-delta-bad {{ color: {ACCENT_RED}; font-size: 13px; font-weight: 700; margin-top: 4px; }}

@keyframes fadeInUp {{
    from {{opacity: 0; transform: translateY(18px);}}
    to {{opacity: 1; transform: translateY(0);}}
}}

.section-title {{
    color: {BLINKIT_YELLOW};
    font-weight: 700;
    font-size: 23px;
    margin: 30px 0 14px 0;
    border-left: 5px solid {BLINKIT_YELLOW};
    padding-left: 14px;
}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #141414 0%, #0a0a0a 100%);
    border-right: 1px solid rgba(248,203,70,0.15);
}}
section[data-testid="stSidebar"] .stMarkdown h2, section[data-testid="stSidebar"] .stMarkdown h3 {{
    color: {BLINKIT_YELLOW};
}}

.pulse-dot {{
    height: 10px; width: 10px;
    background-color: {ACCENT_GREEN};
    border-radius: 50%;
    display: inline-block;
    margin-right: 7px;
    animation: pulse 1.7s infinite;
}}
@keyframes pulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(14, 203, 129, 0.55); }}
    70% {{ box-shadow: 0 0 0 11px rgba(14, 203, 129, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(14, 203, 129, 0); }}
}}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    background: #141414;
    border-radius: 14px;
    padding: 6px;
}}
.stTabs [data-baseweb="tab"] {{
    height: 42px;
    border-radius: 10px;
    color: #b5b5b5;
    font-weight: 600;
    font-family: 'Poppins', sans-serif;
}}
.stTabs [aria-selected="true"] {{
    background: {BLINKIT_YELLOW} !important;
    color: {BLINKIT_BLACK} !important;
}}

div[data-testid="stMetric"] {{
    background: #141414;
    border: 1px solid rgba(248,203,70,0.15);
    border-radius: 14px;
    padding: 12px;
}}

/* Slider accent color */
div[data-testid="stSlider"] div[role="slider"] {{
    background-color: {BLINKIT_YELLOW} !important;
    border-color: {BLINKIT_YELLOW} !important;
}}
div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div {{
    background: {BLINKIT_YELLOW} !important;
}}

.callout {{
    background: rgba(248, 203, 70, 0.08);
    border-left: 4px solid {BLINKIT_YELLOW};
    border-radius: 8px;
    padding: 14px 18px;
    color: #e5e5e5;
    font-size: 14.5px;
    margin: 10px 0 6px 0;
}}

/* Multiselect tags -- match Blinkit branding instead of default red */
span[data-tag] {{
    background-color: {BLINKIT_YELLOW} !important;
    color: {BLINKIT_BLACK} !important;
    border-radius: 8px !important;
}}
span[data-tag] * {{
    color: {BLINKIT_BLACK} !important;
    fill: {BLINKIT_BLACK} !important;
}}

div[data-testid="stMultiSelect"] [data-baseweb="select"] {{
    background-color: #141414 !important;
}}

ul[role="listbox"] {{
    background-color: #141414 !important;
}}
li[role="option"]:hover {{
    background-color: rgba(248, 203, 70, 0.15) !important;
}}
</style>
""", unsafe_allow_html=True)
# ------------------------------------------------------------------
# DATA LOADING (cached)
# ------------------------------------------------------------------
@st.cache_data
def load_data():
    conn = sqlite3.connect("../data/blinkit_lucknow.db")
    orders = pd.read_sql("SELECT * FROM orders", conn, parse_dates=["timestamp"])
    stores = pd.read_sql("SELECT * FROM stores", conn)
    products = pd.read_sql("SELECT * FROM products", conn)
    conn.close()
    orders["date"] = orders["timestamp"].dt.date
    orders["hour"] = orders["timestamp"].dt.hour
    orders["day_name"] = orders["timestamp"].dt.day_name()
    merged = orders.merge(stores, on="store_id").merge(products, on="sku_id")
    return merged, stores, products

try:
    allocation_df = pd.read_csv("../data/allocation_recommendation.csv")
except FileNotFoundError:
    allocation_df = None

df, stores_df, products_df = load_data()

# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------
st.markdown(f"""
<div class="main-header">
    <h1>🟡 Blinkit Lucknow — Dark Store Intelligence</h1>
    <p><span class="pulse-dot"></span>Live Demand-Supply Analytics · {stores_df.shape[0]} Dark Stores · 30-Day Rolling Window</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------------------------
st.sidebar.markdown("## 🎛️ Filters")
zone_filter = st.sidebar.multiselect("Zone", options=sorted(df["zone"].unique()), default=sorted(df["zone"].unique()))
store_filter = st.sidebar.multiselect("Store", options=sorted(df["store_name"].unique()), default=sorted(df["store_name"].unique()))
category_filter = st.sidebar.multiselect("Category", options=sorted(df["category"].unique()), default=sorted(df["category"].unique()))
date_range = st.sidebar.date_input("Date range", value=(df["date"].min(), df["date"].max()))

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 About this project")
st.sidebar.info(
    f"Simulates dark-store inventory & demand across {stores_df.shape[0]} Lucknow "
    "localities, quantifies revenue lost to stockouts, and models a smarter "
    "inventory allocation strategy to recover that revenue."
)

mask = (
    df["zone"].isin(zone_filter)
    & df["store_name"].isin(store_filter)
    & df["category"].isin(category_filter)
    & (df["date"] >= date_range[0])
    & (df["date"] <= date_range[1])
)
fdf = df[mask]

# ------------------------------------------------------------------
# ANIMATED KPI COUNTER HELPER
# ------------------------------------------------------------------
def animated_metric(placeholder, label, target_value, is_currency=False, accent=False, duration=0.5, steps=16):
    css_class = "kpi-value accent" if accent else "kpi-value"
    for i in range(steps + 1):
        val = target_value * (i / steps)
        display_val = f"₹{val:,.0f}" if is_currency else f"{val:,.0f}"
        placeholder.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="{css_class}">{display_val}</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(duration / steps)

# ------------------------------------------------------------------
# TABS
# ------------------------------------------------------------------
tab_overview, tab_stores, tab_sku, tab_simulator = st.tabs(
    ["🏠 Overview", "🗺️ Store Deep-Dive", "📦 SKU Analysis", "🎯 Reallocation Simulator"]
)

# ==================================================================
# TAB 1 — OVERVIEW
# ==================================================================
with tab_overview:
    total_revenue = fdf["revenue"].sum()
    total_lost_revenue = fdf["lost_revenue"].sum()
    stockout_rate = fdf["stockout_flag"].mean() * 100
    avg_fulfillment = (fdf["fulfilled_qty"].sum() / fdf["demand_qty"].sum()) * 100 if fdf["demand_qty"].sum() else 0

    col1, col2, col3, col4 = st.columns(4)
    ph1, ph2, ph3, ph4 = col1.empty(), col2.empty(), col3.empty(), col4.empty()
    animated_metric(ph1, "Realized Revenue", total_revenue, is_currency=True)
    animated_metric(ph2, "Revenue Lost to Stockouts", total_lost_revenue, is_currency=True, accent=True)
    ph3.markdown(f"""<div class="kpi-card"><div class="kpi-label">Stockout Rate</div>
        <div class="kpi-value">{stockout_rate:.1f}%</div></div>""", unsafe_allow_html=True)
    ph4.markdown(f"""<div class="kpi-card"><div class="kpi-label">Order Fulfillment Rate</div>
        <div class="kpi-value">{avg_fulfillment:.1f}%</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">⏱️ Hourly Demand Pattern (animated across days)</div>', unsafe_allow_html=True)
    anim_df = fdf.groupby(["date", "hour"]).agg(total_demand=("demand_qty", "sum"), lost_units=("lost_qty", "sum")).reset_index()
    anim_df["date"] = anim_df["date"].astype(str)
    fig_anim = px.bar(
        anim_df.sort_values("date"), x="hour", y="total_demand", animation_frame="date",
        color="lost_units", color_continuous_scale=["#222222", BLINKIT_YELLOW, ACCENT_RED],
        range_y=[0, anim_df["total_demand"].max() * 1.1],
        labels={"hour": "Hour of Day", "total_demand": "Units Demanded", "lost_units": "Units Lost"},
        template="plotly_dark",
    )
    fig_anim.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=430,
                            transition={"duration": 350, "easing": "cubic-in-out"}, font=dict(color="white", family="Poppins"))
    st.plotly_chart(fig_anim, use_container_width=True)

    st.markdown('<div class="section-title">🧩 Revenue Contribution by Category</div>', unsafe_allow_html=True)
    cat_summary = fdf.groupby("category").agg(revenue=("revenue", "sum"), lost_revenue=("lost_revenue", "sum")).reset_index()
    fig_cat = px.pie(
        cat_summary, names="category", values="revenue", hole=0.55,
        color_discrete_sequence=px.colors.sequential.YlOrBr_r,
    )
    fig_cat.update_traces(textinfo="percent+label", pull=[0.03]*len(cat_summary))
    fig_cat.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=420, font=dict(color="white", family="Poppins"),
                           legend=dict(orientation="h", y=-0.1))
    st.plotly_chart(fig_cat, use_container_width=True)

# ==================================================================
# TAB 2 — STORE DEEP-DIVE
# ==================================================================
with tab_stores:
    st.markdown('<div class="section-title">🗺️ Store-wise Revenue Leakage Map</div>', unsafe_allow_html=True)
    store_summary = fdf.groupby(["store_name", "lat", "lon", "zone"]).agg(
        lost_revenue=("lost_revenue", "sum"), revenue=("revenue", "sum")
    ).reset_index()

    fig_map = px.scatter(
        store_summary, x="lon", y="lat", size="lost_revenue", color="lost_revenue",
        color_continuous_scale=["#2b2b2b", BLINKIT_YELLOW, ACCENT_RED],
        text="store_name",
        hover_name="store_name",
        hover_data={"lat": False, "lon": False, "lost_revenue": ":,.0f", "revenue": ":,.0f"},
        size_max=45,
    )
    fig_map.update_traces(textposition="top center", textfont=dict(color="white", size=11))
    fig_map.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=460, xaxis_title="Longitude", yaxis_title="Latitude",
        font=dict(color="white", family="Poppins"),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    col_zone, col_rank = st.columns(2)
    with col_zone:
        st.markdown('<div class="section-title">📍 Revenue by Zone</div>', unsafe_allow_html=True)
        zone_summary = fdf.groupby("zone").agg(revenue=("revenue", "sum"), lost_revenue=("lost_revenue", "sum")).reset_index()
        fig_zone = go.Figure()
        fig_zone.add_trace(go.Bar(x=zone_summary["zone"], y=zone_summary["revenue"], name="Realized", marker_color=ACCENT_GREEN))
        fig_zone.add_trace(go.Bar(x=zone_summary["zone"], y=zone_summary["lost_revenue"], name="Lost", marker_color=ACCENT_RED))
        fig_zone.update_layout(barmode="group", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)", height=400, legend=dict(orientation="h", y=1.1),
                                font=dict(color="white", family="Poppins"))
        st.plotly_chart(fig_zone, use_container_width=True)

    with col_rank:
        st.markdown('<div class="section-title">🏆 Store Stockout Leaderboard</div>', unsafe_allow_html=True)
        rank_df = fdf.groupby("store_name").agg(
            stockout_rate=("stockout_flag", "mean"), lost_revenue=("lost_revenue", "sum")
        ).reset_index().sort_values("stockout_rate", ascending=False)
        rank_df["stockout_rate"] = (rank_df["stockout_rate"] * 100).round(1)
        fig_rank = px.bar(
            rank_df, x="stockout_rate", y="store_name", orientation="h", color="stockout_rate",
            color_continuous_scale=["#2b2b2b", BLINKIT_YELLOW, ACCENT_RED],
            labels={"stockout_rate": "Stockout Rate (%)", "store_name": ""}, template="plotly_dark",
        )
        fig_rank.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400,
                                font=dict(color="white", family="Poppins"), yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_rank, use_container_width=True)

# ==================================================================
# TAB 3 — SKU ANALYSIS
# ==================================================================
with tab_sku:
    st.markdown('<div class="section-title">📦 Top 10 SKUs Driving Stockout Losses</div>', unsafe_allow_html=True)
    sku_summary = fdf.groupby("sku_name").agg(
        lost_revenue=("lost_revenue", "sum"), stockout_rate=("stockout_flag", "mean")
    ).reset_index().sort_values("lost_revenue", ascending=False).head(10)
    sku_summary["stockout_rate"] = (sku_summary["stockout_rate"] * 100).round(1)

    fig_sku = px.bar(
        sku_summary.sort_values("lost_revenue"), x="lost_revenue", y="sku_name", orientation="h",
        color="stockout_rate", color_continuous_scale=["#2b2b2b", BLINKIT_YELLOW, ACCENT_RED],
        text="lost_revenue", labels={"lost_revenue": "Lost Revenue (₹)", "sku_name": "", "stockout_rate": "Stockout %"},
        template="plotly_dark",
    )
    fig_sku.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig_sku.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=460,
                           font=dict(color="white", family="Poppins"))
    st.plotly_chart(fig_sku, use_container_width=True)

    st.markdown('<div class="section-title">🔎 Explore Any SKU</div>', unsafe_allow_html=True)
    chosen_sku = st.selectbox("Pick an SKU to inspect its hourly demand-vs-fulfillment pattern:", sorted(fdf["sku_name"].unique()))
    sku_hourly = fdf[fdf["sku_name"] == chosen_sku].groupby("hour").agg(
        demand=("demand_qty", "sum"), fulfilled=("fulfilled_qty", "sum")
    ).reset_index()
    fig_sku_hourly = go.Figure()
    fig_sku_hourly.add_trace(go.Scatter(x=sku_hourly["hour"], y=sku_hourly["demand"], name="Demand",
                                         line=dict(color=BLINKIT_YELLOW, width=3), fill="tozeroy"))
    fig_sku_hourly.add_trace(go.Scatter(x=sku_hourly["hour"], y=sku_hourly["fulfilled"], name="Fulfilled",
                                         line=dict(color=ACCENT_GREEN, width=3, dash="dot")))
    fig_sku_hourly.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  height=380, font=dict(color="white", family="Poppins"),
                                  xaxis_title="Hour of Day", yaxis_title="Units")
    st.plotly_chart(fig_sku_hourly, use_container_width=True)

# ==================================================================
# TAB 4 — REALLOCATION SIMULATOR (live, interactive)
# ==================================================================
with tab_simulator:
    st.markdown('<div class="section-title">🎯 Live Inventory Reallocation Simulator</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="callout">
    Drag the slider to control how aggressively inventory is reallocated toward
    high-demand stores — 0% keeps today's status quo allocation, 100% applies the
    fully demand-proportional recommendation. Watch the recovered revenue update live.
    </div>
    """, unsafe_allow_html=True)

    if allocation_df is not None:
        aggressiveness = st.slider("Reallocation aggressiveness", 0, 100, 100, step=5, format="%d%%")
        frac = aggressiveness / 100

        sim_df = allocation_df.copy()
        sim_df["blended_allocation"] = (
            sim_df["current_allocation"] * (1 - frac) + sim_df["recommended_allocation"] * frac
        )
        sim_df["sim_new_lost_units"] = np.where(
            sim_df["blended_allocation"] >= sim_df["total_demand"],
            0,
            sim_df["total_demand"] - sim_df["blended_allocation"],
        ).clip(min=0)
        sim_df["sim_recovered_units"] = (sim_df["total_lost_units"] - sim_df["sim_new_lost_units"]).clip(lower=0)
        sim_df["sim_recovered_revenue"] = sim_df["sim_recovered_units"] * sim_df["unit_price"]

        baseline_lost = sim_df["lost_revenue"].sum()
        recovered_now = sim_df["sim_recovered_revenue"].sum()
        pct_recovered_now = (recovered_now / baseline_lost * 100) if baseline_lost else 0

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"""<div class="kpi-card"><div class="kpi-label">Current Lost Revenue (30d)</div>
            <div class="kpi-value">₹{baseline_lost:,.0f}</div></div>""", unsafe_allow_html=True)
        c2.markdown(f"""<div class="kpi-card"><div class="kpi-label">Recovered at {aggressiveness}% Aggressiveness</div>
            <div class="kpi-value accent">₹{recovered_now:,.0f}</div>
            <div class="kpi-delta-good">▲ {pct_recovered_now:.1f}% of leakage recovered</div></div>""", unsafe_allow_html=True)
        c3.markdown(f"""<div class="kpi-card"><div class="kpi-label">Projected Annualized Recovery</div>
            <div class="kpi-value">₹{recovered_now*12:,.0f}</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        top_moves = sim_df.sort_values("sim_recovered_revenue", ascending=False).head(10)
        fig_alloc = px.bar(
            top_moves, x="sku_name", y=["current_allocation", "blended_allocation"], barmode="group",
            template="plotly_dark", labels={"value": "Units Allocated", "sku_name": "SKU", "variable": "Allocation"},
            color_discrete_map={"current_allocation": "#555555", "blended_allocation": BLINKIT_YELLOW},
        )
        fig_alloc.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=430,
                                 font=dict(color="white", family="Poppins"), xaxis_tickangle=-30)
        st.plotly_chart(fig_alloc, use_container_width=True)
    else:
        st.warning("Run `allocation_engine.py` first to generate allocation_recommendation.csv")

# ------------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------------
st.markdown(f"""
<div style="text-align:center; padding: 26px; color: #6b6b6b; font-size: 13px;">
    Built with Python · SQL · Streamlit · Plotly &nbsp;|&nbsp; Synthetic dataset simulating Blinkit dark-store operations across {stores_df.shape[0]} Lucknow localities
</div>
""", unsafe_allow_html=True)

# =========================================================
# FOOTER — brass nameplate (kept: LinkedIn link)
# =========================================================
st.markdown("""
<div class="footer-wrapper">
    <div class="plaque">
        Built by <a href="https://www.linkedin.com/in/pratyushraj05" target="_blank" title="Connect on LinkedIn">Pratyush Kant Raj</a>
    </div>
</div>
""", unsafe_allow_html=True)