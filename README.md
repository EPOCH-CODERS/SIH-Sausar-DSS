# SIH26009: MOIL Manganese Decision Support System

A Two-Tiered Decision Support System (DSS) developed for MOIL and the Ministry of Steel to identify manganese reserves and overcome production shortfalls using AI/ML and Space Technology.

## 📖 Overview

Manganese is a critical mineral irreplaceable in steel making, and eliminating import dependence is an urgent national priority. MOIL operates 10 mines (7 Underground, 3 Opencast) in Maharashtra and Madhya Pradesh, producing ~19.07 Lakh Metric Tonnes annually. This repository contains a decoupled DSS that bridges the gap between multi-year geological exploration and weekly operational fleet management.

## 🏗️ System Architecture

Our solution is divided into three decoupled components to maintain physical timescale integrity:

### Component 1: Mineral Prospectivity Mapping (MPM)

* **Objective:** Prioritize capital exploration by highlighting high-probability geochemical anomalies on the surface.


* **Methodology:** Uses Sentinel-2 L2A multispectral data and Copernicus 30m Global DEM.


* **Science:** Direct satellite detection of manganese is scientifically impossible due to its flat reflectance. The model detects pathfinder minerals (Iron Oxides, Ferrous Silicates, Hydroxyl Clays) that physically co-occur with manganese in the Sausar Belt.


* **Model:** Random Forest classifier predicting coarse prospectivity bands (High / Medium / Low) with tree-agreement uncertainty shading. Validated via Leave-One-Mine-Out Spatial CV (LOOCV) to prevent spatial data leakage.



### Component 2: Production Forecasting

* **Objective:** Forecast continuous weekly production (tonnes/week) for each of MOIL's 10 mines to catch shortfalls early.


* **Inputs:** Autoregressive production lags, Indian Meteorological Department (IMD) real-time/forecasted rainfall, and equipment active uptime percentages.


* **Model:** XGBoost Regressor, chosen for its ability to handle tabular missingness and non-linear interactions without the overfitting risks associated with LSTMs on sparse mining data. Evaluated via strict chronological train/test splits.



### Component 3: Two-Tiered Decision Engine

Separates strategic exploration from immediate operational response.

* **Tier 1 (Immediate Fleet Reallocation - Days/Weeks):** Uses an Integer Linear Programming (ILP) solver via Python's PuLP library. It maximizes recovered ore using a 1.5x grade multiplier for high-grade ore. **Hard Constraint:** Enforces a strict boundary where underground equipment cannot enter opencast pits, and vice versa.


* **Tier 2 (Strategic Exploration - Months/Years):** Uses an Infrastructure-Proximity Priority Heuristic formula to rank high-prospectivity zones based on proximity to existing MOIL infrastructure.


* **Governance:** Includes a Human-in-the-Loop approval gate where a Senior Mine Planner must [Accept], [Modify], or [Reject] recommendations.



## 💻 Tech Stack & Data Provenance

* **Languages & Libraries:** Python 3.10+, GeoPandas, Rasterio, scikit-learn, XGBoost, PuLP (CBC Solver), DuckDB/SQLite.


* **Frontend UI:** Streamlit.


* **Satellite Data:** Sentinel-2 L2A (Copernicus Open Access Hub) and Copernicus Global DEM (Free & Open).


* **Boundaries:** IBM MCDR lease polygons (Public Domain).



## 🚀 Dashboard Interface (Streamlit)

1. **Prospectivity Explorer:** Interactive Folium map displaying High/Medium/Low prospectivity zones with uncertainty opacity.


2. **Production Tracker:** Multi-mine time-series chart of forecasted vs. target production featuring automated deficit alerts.


3. **Decision Console:** Reallocation schedules and ranked exploration targets with manual override controls.



## ⚙️ Installation & Setup (Local Prototype)

(Provide standard git clone, pip install -r requirements.txt, and python -m streamlit run app.py commands here. Note: The local prototype runs offline utilizing pre-cached tiles to ensure zero-cloud resilience.)

## 🛡️ Enterprise Vision

While this repository houses the local prototype, the enterprise deployment architecture utilizes AWS S3 & EC2 GPU, PostgreSQL + PostGIS, a FastAPI backend, AES-256 encryption, and RBAC to protect confidential MOIL intellectual property.

---

**Disclaimer:** Operational production and maintenance records used in this prototype are synthetic representations based on the MOIL schema, as actual production logs are confidential corporate IP.
