import streamlit as st
import pandas as pd
import numpy as np
import math

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

# ==========================================
# PURE NUMPY SEASONAL MANN-KENDALL & SEN'S SLOPE
# ==========================================
def seasonal_mann_kendall(values, period=12):
    y = np.asarray(values, dtype=float)
    n = len(y)
    s_total = 0
    var_s = 0.0
    slopes = []

    for m in range(period):
        season_vals = y[m::period]
        ns = len(season_vals)
        if ns < 2:
            continue
        for i in range(ns - 1):
            for j in range(i + 1, ns):
                diff = season_vals[j] - season_vals[i]
                if diff > 0:
                    s_total += 1
                elif diff < 0:
                    s_total -= 1
                slopes.append(diff / (j - i))
        var_s += ns * (ns - 1) * (2 * ns + 5) / 18.0

    if var_s <= 0:
        return "no trend", 0.0, 1.0

    if s_total > 0:
        z = (s_total - 1) / math.sqrt(var_s)
    elif s_total < 0:
        z = (s_total + 1) / math.sqrt(var_s)
    else:
        z = 0.0

    p_val = math.erfc(abs(z) / math.sqrt(2.0))
    sen_slope = float(np.median(slopes)) if slopes else 0.0

    if p_val < 0.05:
        trend_dir = "increasing" if s_total > 0 else "decreasing"
    else:
        trend_dir = "no significant trend"

    return trend_dir, sen_slope, p_val

# ==========================================
# MULTI-BRANCH EARTH SCIENCE CATALOG
# ==========================================
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

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
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

# ==========================================
# DATA GENERATION & DECOMPOSITION
# ==========================================
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
df = df.assign(
    Year=df.get("Date").dt.year,
    Month=df.get("Date").dt.month,
    Decade=(df.get("Date").dt.year // 10) * 10
)

# Classical Additive Seasonal Decomposition (Pure Pandas/NumPy)
monthly_clim = df.groupby("Month")["Value"].transform("mean")
overall_mean = df["Value"].mean()
df = df.assign(
    Seasonal=monthly_clim - overall_mean,
    Deseasonalized=df["Value"] - (monthly_clim - overall_mean),
    Trend=df["Value"].rolling(window=12, center=True, min_periods=1).mean()
)
df = df.assign(Residual=df["Deseasonalized"] - df["Trend"])

trend_dir, sen_slope, p_val = seasonal_mann_kendall(df["Value"].values, period=12)

# Linear OLS slope & 95% CI
x_centered = years_elapsed - years_elapsed.mean()
y_deseas = df["Deseasonalized"].values
ols_slope = np.sum(x_centered * (y_deseas - y_deseas.mean())) / np.sum(x_centered ** 2)
y_hat = y_deseas.mean() + ols_slope * x_centered
std_err = math.sqrt(np.sum((y_deseas - y_hat) ** 2) / max(1, n - 2) / np.sum(x_centered ** 2))
ci_95 = 1.96 * std_err

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

# ==========================================
# 3-PAGE TABS
# ==========================================
page1, page2, page3 = st.tabs([
    "📄 Page 1: Orbital Trend & Decomposition",
    "📄 Page 2: Decade Regime Shift & Anomalies",
    "📄 Page 3: Cross-Branch System Coupling"
])

with page1:
    st.subheader("1. Statistical Significance & Rate-of-Change Telemetry")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Trend Direction", trend_dir.upper())
    k2.metric("Sen's Slope (Rate/Yr)", f"{sen_slope:+.4f} {unit}/yr", f"±{ci_95:.4f} (95% CI)")
    k3.metric("Seasonal MK p-value", f"{p_val:.4e}")
    k4.metric("Statistical Verdict", "SIGNIFICANT" if p_val < 0.05 else "NOT SIGNIFICANT")

    st.subheader("2. Observed Signal vs. Deseasonalized & Rolling Trend")
    chart_df1 = df.set_index("Date")[["Value", "Deseasonalized", "Trend"]]
    st.line_chart(chart_df1, color=["#64748b", "#38bdf8", "#f43f5e"], height=380)


