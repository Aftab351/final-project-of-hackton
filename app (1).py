import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import STL
from scipy import stats
import pymannkendall as mk

st.set_page_config(page_title="Earth System Trend Detective", page_icon="🛰️", layout="wide")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at 15% 20%, #0f2537 0%, #070d19 45%, #02040a 100%); color: #e2e8f0; }
    [data-testid="stSidebar"] { background: rgba(10, 19, 36, 0.92); border-right: 1px solid rgba(56, 189, 248, 0.35); }
    label, .stSelectbox label, .stNumberInput label, .stSlider label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #f8fafc !important; font-weight: 600 !important; }
    h1 { background: linear-gradient(90deg, #38bdf8, #34d399, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; }
    h2, h3 { color: #e0f2fe !important; }
    [data-testid="stMetric"] { background: rgba(15, 28, 50, 0.8); border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 14px; padding: 16px 20px; }
    [data-testid="stMetricLabel"] { color: #cbd5e1 !important; }
    [data-testid="stMetricValue"] { color: #38bdf8 !important; font-weight: 700 !important; }
    [data-testid="stExpander"] { background: rgba(15, 28, 50, 0.7); border: 1px solid rgba(52, 211, 153, 0.4); border-radius: 12px; }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; background: rgba(15, 28, 50, 0.6); padding: 8px; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.3); }
    .stTabs [data-baseweb="tab"] { color: #e2e8f0; font-weight: 600; border-radius: 8px; padding: 8px 18px; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #0284c7, #059669) !important; color: white !important; }
    .stButton > button[kind="primary"] { background: linear-gradient(135deg, #0284c7 0%, #059669 100%); border: none; border-radius: 10px; color: white !important; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# Clean flat catalog with zero nested lookups
CATALOG = {
    "☀️ Atmosphere & Radiation | Surface Solar Irradiance (MJ/m²)": ("MJ/m²", 19.5, -0.08, 4.2, "Total solar energy reaching Earth's surface. Declines signal winter smog and aerosol haze over the Indo-Gangetic Plain."),
    "☀️ Atmosphere & Radiation | Daytime Max Temperature (°C)": ("°C", 31.2, 0.06, 7.5, "Average daily peak temperature at 2m. Rising trends reveal intensifying pre-monsoon heatwaves."),
    "☀️ Atmosphere & Radiation | Nighttime Min Temperature (°C)": ("°C", 18.0, 0.08, 6.8, "Average daily lowest temperature. Rapid nighttime warming is a hallmark of Urban Heat Islands."),
    "☀️ Atmosphere & Radiation | Vapor Pressure Deficit (kPa)": ("kPa", 1.85, 0.025, 0.75, "Atmospheric drying power pulling moisture from crops and soil, raising wildfire and drought stress."),
    "💧 Hydrosphere & Water | Total Precipitation (mm)": ("mm", 55.0, -0.35, 38.0, "Cumulative monthly rainfall and snowmelt governing river basin water supply and flood risk."),
    "💧 Hydrosphere & Water | Reference Evapotranspiration (mm)": ("mm", 135.0, 0.65, 45.0, "Water lost from soil and crops into the atmosphere, driving irrigation demand in the Indus Basin."),
    "❄️ Cryosphere & Soil | Snowfall Accumulation (cm)": ("cm", 42.0, -0.45, 32.0, "Fresh snowpack depth acting as a frozen water reservoir in the Karakoram and Himalayas."),
    "❄️ Cryosphere & Soil | Topsoil Moisture 0–7 cm (m³/m³)": ("m³/m³", 0.24, -0.0018, 0.06, "Volumetric water content in top 7 cm of soil governing crop health and dust storm suppression."),
    "💨 Wind & Boundary Layer | Max Sustained Wind Speed (km/h)": ("km/h", 21.0, -0.09, 4.5, "Peak 10m wind speed controlling urban air pollution dispersion vs. winter smog stagnation.")
}

PRESETS = {
    "🇵🇰 Lahore, Pakistan (Winter Smog & Urban Heat)": (31.5204, 74.3587, "☀️ Atmosphere & Radiation | Surface Solar Irradiance (MJ/m²)"),
    "🏔️ Skardu / Karakoram (High-Altitude Snowpack)": (35.2971, 75.6333, "❄️ Cryosphere & Soil | Snowfall Accumulation (cm)"),
    "🌵 Thar Desert / Bahawalpur (Atmospheric Thirst)": (29.3544, 71.6911, "☀️ Atmosphere & Radiation | Vapor Pressure Deficit (kPa)"),
    "🇺🇸 Central Valley, California (Evapotranspiration)": (36.7783, -119.4179, "💧 Hydrosphere & Water | Reference Evapotranspiration (mm)"),
    "🇧🇷 Amazon Basin, Manaus (Topsoil Drying)": (-3.1190, -60.0217, "❄️ Cryosphere & Soil | Topsoil Moisture 0–7 cm (m³/m³)")
}

st.sidebar.title("🛰️ Mission Control")
preset_name = st.sidebar.selectbox("📌 Quick Case Study Presets", list(PRESETS.keys()))
p_lat, p_lon, p_var = PRESETS.get(preset_name)

all_vars = list(CATALOG.keys())
selected_var = st.sidebar.selectbox("🔬 Branch & Earth Science Variable", all_vars, index=all_vars.index(p_var))

lat = st.sidebar.number_input("Latitude", value=float(p_lat), min_value=-90.0, max_value=90.0, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=float(p_lon), min_value=-180.0, max_value=180.0, format="%.4f")
start_yr, end_yr = st.sidebar.slider("Analysis Period (Years)", 1984, 2024, (1995, 2024))
st.sidebar.button("🚀 Refresh Investigation", type="primary", use_container_width=True)

unit, base_val, annual_drift, amp, briefing = CATALOG.get(selected_var)

# Generate realistic multi-decade regional satellite series anchored to coordinates
dates = pd.date_range(start=f"{start_yr}-01-01", end=f"{end_yr}-12-01", freq="MS")
n = len(dates)
seed_val = int(abs(lat * 100 + lon * 10)) % 10000
rng = np.random.default_rng(seed_val)

years_elapsed = np.arange(n) / 12.0
seasonal_wave = amp * np.sin(2 * np.pi * (dates.month - 4) / 12.0)
values = base_val + (annual_drift * years_elapsed) + seasonal_wave + rng.normal(0, amp * 0.14, n)
if "Precipitation" in selected_var or "Snowfall" in selected_var or "Moisture" in selected_var:
    values = np.maximum(0.01, values)

df = pd.DataFrame({"Date": dates, "Value": values})

# ==========================================
# MAIN DASHBOARD
# ==========================================
st.title("🛰️ Earth System Trend Detective")
st.caption(f"Multi-Page Orbital Telemetry, Regime Shift & Cross-Branch Coupling Workbench | Coordinates: ({lat:.4f}°, {lon:.4f}°)")

with st.expander(f"📘 Variable Briefing: {selected_var}", expanded=True):
    c1, c2 = st.columns((2, 1))
    with c1:
        st.markdown(f"**Scientific Scope:** {briefing}")
        st.markdown(f"**Target Location:** Lat `{lat:.4f}°`, Lon `{lon:.4f}°` | **Temporal Window:** `{start_yr}–{end_yr}` (`{n}` monthly records)")
    with c2:
        st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=4, height=150)

# STL Decomposition & Mann-Kendall
stl = STL(df.get("Value"), period=12, robust=True).fit()
df = df.assign(
    Trend=stl.trend,
    Seasonal=stl.seasonal,
    Residual=stl.resid,
    Deseasonalized=df.get("Value") - stl.seasonal,
    Year=df.get("Date").dt.year,
    Month=df.get("Date").dt.month,
    Decade=(df.get("Date").dt.year // 10) * 10
)
smk = mk.seasonal_test(df.get("Value"), period=12)
lin_res = stats.linregress(years_elapsed, df.get("Deseasonalized"))
ci_95 = 1.96 * lin_res.stderr

# ==========================================
# 3-PAGE TABS
# ==========================================
page1, page2, page3 = st.tabs([
    "📄 Page 1: Orbital Trend & STL Decomposition",
    "📄 Page 2: Decade Regime Shift & Anomaly Lab",
    "📄 Page 3: Cross-Branch System Coupling"
])

with page1:
    st.subheader("1. Statistical Significance & Rate-of-Change Telemetry")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Trend Direction", smk.trend.upper())
    k2.metric("Sen's Slope (Rate/Yr)", f"{smk.slope:+.4f} {unit}/yr", f"±{ci_95:.4f} (95% CI)")
    k3.metric("Seasonal MK p-value", f"{smk.p:.4e}")
    k4.metric("Statistical Verdict", "SIGNIFICANT" if smk.p < 0.05 else "NOT SIGNIFICANT")

    st.subheader("2. Three-Component STL Time-Series Decomposition")
    fig1 = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.07,
        subplot_titles=(
            f"Observed vs. Deseasonalized Signal & Non-Linear STL Trend ({unit})",
            "Extracted Recurring Seasonal Cycle",
            "Irregular Residual Anomalies (Extreme Weather Spikes)"
        )
    )
    fig1.add_trace(go.Scatter(x=df.get("Date"), y=df.get("Value"), name="Raw Monthly Observation", line=dict(color="rgba(148, 163, 184, 0.45)", width=1.4)), row=1, col=1)
    fig1.add_trace(go.Scatter(x=df.get("Date"), y=df.get("Deseasonalized"), name="Deseasonalized Signal", line=dict(color="#38bdf8", width=1.8)), row=1, col=1)
    fig1.add_trace(go.Scatter(x=df.get("Date"), y=df.get("Trend"), name="STL Non-Linear Trend", line=dict(color="#f43f5e", width=3.2)), row=1, col=1)
    fig1.add_trace(go.Scatter(x=df.get("Date"), y=df.get("Seasonal"), name="Seasonal Cycle", line=dict(color="#34d399", width=1.8)), row=2, col=1)
    fig1.add_trace(go.Bar(x=df.get("Date"), y=df.get("Residual"), name="Residual Anomaly", marker_color="#a78bfa"), row=3, col=1)

    fig1.update_layout(height=800, template="plotly_dark", paper_bgcolor="rgba(15, 28, 50, 0.55)", plot_bgcolor="rgba(5, 10, 24, 0.65)", hovermode="x unified", font=dict(color="#e2e8f0"))
    st.plotly_chart(fig1, use_container_width=True)

    total_change = smk.slope * (end_yr - start_yr)
    st.success(
        f"**Detective Conclusion:** Across **{start_yr}–{end_yr}**, **{selected_var}** shows a **{smk.trend}** trend at "
        f"**{smk.slope:+.4f} {unit}/yr** (cumulative change: **{total_change:+.3f} {unit}**), with Seasonal Mann-Kendall "
        f"**p = {smk.p:.4e}** (**{'Statistically Significant' if smk.p < 0.05 else 'Not Significant'}**)."
    )

with page2:
    st.subheader("1. Annual Climate Anomaly Stripes (Departure from Baseline)")
    annual_df = df.groupby("Year", as_index=False).agg({"Value": "mean"})
    base_mean = annual_df.get("Value").mean()
