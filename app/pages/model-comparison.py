"""Page 3 - Model comparison: WRMSSE, backtest stability, and model roles."""
import streamlit as st
import pandas as pd
import altair as alt
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils import load_csv
from diagrams import MODEL_WINS_SVG
import streamlit.components.v1 as components

st.title("Model Comparison")
st.markdown(
    "Four approaches compared with **WRMSSE** (the official M5 metric). "
    "WRMSSE < 1.0 beats the seasonal-naive baseline."
)
st.caption(
    "Scope note: leaf-level WRMSSE for LightGBM covers all 30,490 series; the "
    "deep N-BEATS model was trained on a 1,500-series subset (see the results "
    "table's *n_series* / *level* columns). Aggregate RMSE is at the store × "
    "category level (30 series)."
)

try:
    res = load_csv("evaluation_results.csv")
except Exception:
    st.error("evaluation_results.csv not found in app/data/")
    st.stop()

# ---- which model wins where ----
st.subheader("Which model wins where")
components.html(MODEL_WINS_SVG, height=220)

st.divider()

# ---- leaf-level WRMSSE ----
leaf = res[res["metric"].str.contains("WRMSSE", na=False)].copy()
if not leaf.empty:
    st.subheader("Leaf-level WRMSSE (lower is better)")
    bars = alt.Chart(leaf).mark_bar(color="#4C78A8").encode(
        x=alt.X("value:Q", title="WRMSSE", scale=alt.Scale(domain=[0, 1.05])),
        y=alt.Y("model:N", sort="-x", title=None),
        tooltip=["level", "model", "value"],
    ).properties(height=200)
    rule = alt.Chart(pd.DataFrame({"v": [1.0]})).mark_rule(
        color="#d62728", strokeDash=[4, 3], size=2).encode(x="v:Q")
    st.altair_chart(bars + rule, use_container_width=True)
    st.caption("Red line = seasonal-naive baseline (1.0). Every model beats it.")

# ---- aggregate-level RMSE ----
agg = res[res["metric"] == "RMSE"].copy()
if not agg.empty:
    st.subheader("Aggregate-level RMSE (store × category)")
    bars2 = alt.Chart(agg).mark_bar(color="#0F6E56").encode(
        x=alt.X("value:Q", title="RMSE"),
        y=alt.Y("model:N", sort="-x", title=None),
        tooltip=["model", "value"],
    ).properties(height=150)
    st.altair_chart(bars2, use_container_width=True)
    st.caption(
        "Prophet (fit on the smooth aggregate) far outperforms summing intermittent "
        "leaves. MinT recovers Prophet's accuracy while guaranteeing coherence."
    )

st.divider()

# ---- backtest stability ----
st.subheader("Backtest: stability across time")
st.markdown(
    "*Scope: LightGBM P50 retrained on a **2,000-series stratified sample** "
    "(across store × category), evaluated on three rolling 28-day windows. "
    "The subset keeps the backtest tractable while remaining representative.*"
)
bt = pd.DataFrame({
    "window": ["W1\n(Apr-May)", "W2\n(Mar-Apr)", "W3\n(Feb-Mar)"],
    "wrmsse": [0.8186, 0.8835, 0.8282],
})
mean_w = bt["wrmsse"].mean()
pts = alt.Chart(bt).mark_point(size=140, color="#4C78A8", filled=True).encode(
    x=alt.X("window:N", title=None),
    y=alt.Y("wrmsse:Q", title="WRMSSE", scale=alt.Scale(domain=[0.75, 0.95])),
    tooltip=["window", "wrmsse"],
)
line = alt.Chart(bt).mark_line(color="#4C78A8", strokeWidth=2).encode(
    x="window:N", y="wrmsse:Q")
meanline = alt.Chart(pd.DataFrame({"m": [mean_w]})).mark_rule(
    color="#888", strokeDash=[4, 3]).encode(y="m:Q")
st.altair_chart((line + pts + meanline).properties(height=260),
                use_container_width=True)
c1, c2 = st.columns(2)
c1.metric("Mean WRMSSE", f"{mean_w:.3f}")
c2.metric("Std deviation", f"{bt['wrmsse'].std():.3f}", "low = stable")
st.caption(
    "Three rolling 28-day windows across three months. Low variance (±0.035) "
    "confirms performance isn't an artifact of one test period."
)

st.divider()
st.subheader("Full results")
st.dataframe(res, use_container_width=True, hide_index=True)