"""M5 Hierarchical Demand Forecasting - Dashboard entry point.

Run with:  streamlit run app/app.py
"""
import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from diagrams import PIPELINE_SVG
import streamlit.components.v1 as components

st.set_page_config(
    page_title="M5 Demand Forecasting",
    page_icon="📦",
    layout="wide",
)

st.title("📦 M5 Hierarchical Demand Forecasting System")
st.markdown(
    "An end-to-end **probabilistic, hierarchically-coherent** demand forecasting "
    "system on the **M5 Walmart** dataset — 30,490 series across 3 states, 10 "
    "stores, and 3,049 items."
)

# ---- lead with the architecture picture ----
components.html(PIPELINE_SVG, height=320)

st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("Series forecast", "30,490")
col2.metric("Best leaf WRMSSE", "0.841", help="LightGBM, beats seasonal-naive (1.0)")
col3.metric("Forecast horizon", "28 days")

st.markdown(
    """
**Explore the dashboard** (see the sidebar):
- **Overview** — the challenge, the approach, and headline results
- **Forecast Explorer** — probabilistic (P10/P50/P90) forecasts per series
- **Model Comparison** — WRMSSE across all four models, with backtest stability
- **Inventory Calculator** — a live newsvendor optimizer turning forecasts into
  order decisions and dollar savings
"""
)

st.caption(
    "All forecasts are precomputed for speed; the inventory calculator runs live "
    "on the selected series. Interactive pages show a representative subset of "
    "series for responsiveness; evaluation metrics state their scope (full 30,490 "
    "leaves vs. sampled) on each page."
)