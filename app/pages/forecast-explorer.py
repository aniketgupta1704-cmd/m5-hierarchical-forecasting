"""Page 2 — Forecast explorer: probabilistic forecasts per series."""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils import load_forecasts
from diagrams import HIERARCHY_SVG
import streamlit.components.v1 as components

st.title("Forecast Explorer")
st.markdown("Probabilistic 28-day forecasts (P10 / P50 / P90) for individual series.")
st.caption(
    "Showing the **top 500 series by sales volume** (of 30,490 total) for a "
    "responsive dashboard. Forecasts were generated for all series; this subset "
    "keeps the app fast to load. Use the filters below to narrow the list."
)

fc = load_forecasts()

# ---- filters ----
c1, c2, c3 = st.columns(3)
state = c1.selectbox("State", ["All"] + sorted(fc["state_id"].dropna().unique().tolist()))
f = fc if state == "All" else fc[fc["state_id"] == state]
cat = c2.selectbox("Category", ["All"] + sorted(f["cat_id"].dropna().unique().tolist()))
f = f if cat == "All" else f[f["cat_id"] == cat]
series = c3.selectbox("Series", sorted(f["id"].unique().tolist()))

s = fc[fc["id"] == series].sort_values("date").copy()
s["date"] = pd.to_datetime(s["date"])

# ---- fan chart ----
import altair as alt
band = alt.Chart(s).mark_area(opacity=0.25, color="#4C78A8").encode(
    x=alt.X("date:T", title="Date"),
    y=alt.Y("p10:Q", title="Units"),
    y2="p90:Q",
)
median = alt.Chart(s).mark_line(color="#1f4e8c", point=True).encode(
    x="date:T", y="p50:Q")
actual = alt.Chart(s).mark_line(color="#d62728", strokeDash=[4, 3]).encode(
    x="date:T", y=alt.Y("sales:Q", title="Units"))
st.altair_chart((band + median + actual).properties(height=380),
                use_container_width=True)
st.caption("Shaded = P10–P90 interval · solid blue = P50 · dashed red = actual sales")

# ---- summary ----
c1, c2, c3, c4 = st.columns(4)
c1.metric("Mean P50", f"{s['p50'].mean():.2f}")
c2.metric("Mean actual", f"{s['sales'].mean():.2f}")
cov = ((s["sales"] >= s["p10"]) & (s["sales"] <= s["p90"])).mean()
c3.metric("Interval coverage", f"{cov:.0%}", help="Target ~80%")
c4.metric("Sell price", f"${s['sell_price'].iloc[0]:.2f}")

with st.expander("Raw forecast data"):
    st.dataframe(s[["date", "p10", "p50", "p90", "sales"]],
                 use_container_width=True, hide_index=True)

st.divider()
st.subheader("Where this series sits in the hierarchy")
st.markdown(
    "M5 has five aggregation levels. **Prophet** forecasts the smooth "
    "**store × category** level (30 series); **LightGBM** forecasts the "
    "**item × store leaves** (30,490 series). **MinT reconciliation** ties every "
    "level together so forecasts sum coherently up the pyramid."
)
components.html(
    f'<div style="width:100%;overflow:visible">{HIERARCHY_SVG}</div>',
    height=520, scrolling=False)