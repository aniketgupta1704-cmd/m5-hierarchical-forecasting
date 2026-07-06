"""Page 1 - Project overview: architecture first, then the story, then results."""
import streamlit as st
import pandas as pd
import altair as alt
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils import load_csv
import streamlit.components.v1 as components

st.title("M5 Demand Forecasting System")
st.markdown(
    "An end-to-end **probabilistic, hierarchically-coherent** demand forecasting "
    "system on the M5 Walmart dataset — from raw sales to inventory decisions."
)

st.divider()

# ---- THE STORY: why before what ----
st.subheader("The core challenge")

left, right = st.columns([1.1, 1])

with left:
    st.markdown(
        """
**69% of products have zero sales on more than half of all days.**

&darr;

**Traditional point forecasting struggles** — predicting "3.2 units" for an
item that sells 0 most days is meaningless, and independent forecasts don't
sum correctly across the store &rarr; state &rarr; national hierarchy.

&darr;

**So this system uses:**
- **Quantile forecasting** (P10/P50/P90) to capture uncertainty, not just a mean
- **Hierarchical reconciliation** (MinT) so forecasts stay coherent across levels
- **A newsvendor inventory layer** that turns uncertainty into optimal order decisions
"""
    )

with right:
    st.write("")
    st.write("")
    donut_df = pd.DataFrame({
        "type": ["Intermittent", "Dense"],
        "pct": [69.4, 30.6],
    })
    donut = alt.Chart(donut_df).mark_arc(innerRadius=60).encode(
        theta=alt.Theta("pct:Q"),
        color=alt.Color("type:N",
                        scale=alt.Scale(domain=["Intermittent", "Dense"],
                                        range=["#D85A30", "#4C78A8"]),
                        legend=alt.Legend(orient="bottom", title=None)),
        tooltip=["type:N", "pct:Q"],
    ).properties(height=280)
    st.altair_chart(donut, use_container_width=True)
    st.caption("Intermittent = >50% zero-sales days")

st.divider()

# ---- 3. RESULTS: the payoff ----
st.subheader("Results at a glance")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Series forecast", "30,490")
c2.metric("Best leaf WRMSSE", "0.841", "beats naive (1.0)")
c3.metric("Backtest stability", "±0.035", "across 3 windows")
c4.metric("Inventory savings", "up to 55%", "vs point forecast")

try:
    res = load_csv("evaluation_results.csv")
    with st.expander("Full evaluation results"):
        st.dataframe(res, use_container_width=True, hide_index=True)
except Exception:
    st.warning("evaluation_results.csv not found in app/data/")

st.info(
    "**Core finding:** no single model wins everywhere. LightGBM wins at the "
    "leaves, Prophet at the aggregates — so the hierarchy is necessary, tied "
    "together by MinT reconciliation. See the Model Comparison page.",
    icon="💡",
)