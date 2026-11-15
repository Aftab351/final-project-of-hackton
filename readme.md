# 🛰️ Earth System Trend Detective
**NASA Space Apps Challenge — Be An Earth System Trend Detective**

## 🔗 Project Links
* **Live Interactive Web App:** [https://streamlit.app](https://streamlit.app)
* **Source Code Repository:** [https://github.com](https://github.com)

---

## 📌 High-Level Summary
**Earth System Trend Detective** is an interactive, multi-page Earth observation and statistical analysis workbench designed for students, researchers, and citizen scientists. Users select any global coordinate and investigate multi-decade trends across four Earth science branches—**Atmosphere & Radiation**, **Hydrosphere & Water Balance**, **Cryosphere & Soil Systems**, and **Wind & Boundary Layer**—using seasonal time-series decomposition, Sen's slope estimation, and Seasonal Mann-Kendall significance testing ($p < 0.05$).

---

## 🎯 Challenge Objective & How We Solved It
The **Be An Earth System Trend Detective** challenge requires connecting regional Earth science variables to time-series visualizations and rigorous statistical significance tests while keeping concepts accessible to high school and college students.

Our solution fulfills every requirement through a **3-Page Scientific Workbench**:
1. **Plain-Language Variable Briefings & Regional Presets:** Provides clear scientific definitions and one-click real-world detective case studies (such as *Winter Solar Dimming & Urban Heat in Lahore*, *High-Altitude Snowpack in the Karakoram*, *Atmospheric Thirst in the Thar Desert*, and *Topsoil Drying in the Amazon*).
2. **Page 1 — Orbital Trend & Seasonal Decomposition:**
   * Separates raw monthly observations into **Deseasonalized Signal**, **Rolling Long-Term Trend**, **Recurring Seasonal Cycle**, and **Irregular Residual Anomalies** so seasonal oscillations do not mask underlying linear trends.
   * Computes **Sen's Slope** (annual rate of change with 95% confidence intervals) and runs a non-parametric **Seasonal Mann-Kendall Test** ($p$-value threshold $< 0.05$) with an automated plain-English detective conclusion.
3. **Page 2 — Decade Regime Shift & Anomaly Lab:**
   * Visualizes annual departures from the long-term baseline, decade-by-decade distribution shifts (mean, median, min, max), and month-by-year climatology profiles.
4. **Page 3 — Cross-Branch System Coupling:**
   * Examines physical interactions across Earth system branches using a **Pearson Correlation Matrix ($r$)** and interactive driver-vs.-response scatter plots (e.g., how rising daytime temperatures drive topsoil moisture loss), plus one-click **CSV telemetry export**.

---

## 🛠️ Technology Stack & Methodology
* **Frontend & Visualization:** Python, Streamlit (Custom Orbital Glassmorphism Dark Theme), interactive native charting & geospatial mapping.
* **Statistical & Mathematical Engine:** NumPy, Pandas, Classical Additive Seasonal Decomposition, Ordinary Least Squares (OLS) 95% Confidence Intervals, and Seasonal Mann-Kendall Non-Parametric Trend Testing.
* **Earth Science Variables Covered (9 Metrics across 4 Branches):**
  * *Atmosphere & Radiation:* Surface Solar Irradiance ($\text{MJ/m}^2$), Daytime Max Temperature ($^\circ\text{C}$), Nighttime Min Temperature ($^\circ\text{C}$), Vapor Pressure Deficit ($\text{kPa}$).
  * *Hydrosphere & Water Balance:* Total Precipitation ($\text{mm}$), Reference Evapotranspiration ($\text{mm}$).
  * *Cryosphere & Soil Systems:* Snowfall Accumulation ($\text{cm}$), Topsoil Moisture 0–7 cm ($\text{m}^3/\text{m}^3$).
  * *Wind & Boundary Layer:* Maximum Sustained Wind Speed ($\text{km/h}$).

---

## 🌍 NASA & Open Earth Science Resources Referenced
* **NASA Earth Science Division & Earthdata:** Variable definitions, atmospheric aerosol/irradiance concepts, and regional Earth system monitoring frameworks.
* **NASA POWER & Global Reanalysis Architectures:** Temporal resolution standards (monthly aggregation over multi-decade baselines from 1984–2024).
* **Consortium of Universities for the Advancement of Hydrologic Science, Inc. (CUAHSI):** Hydrological time-series analysis and water-balance framing.
