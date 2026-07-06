"""Page 4 - Live newsvendor inventory calculator with distribution curve."""
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from scipy import stats
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils import (load_forecasts, load_csv, critical_ratio,
                   optimal_order_from_quantiles, newsvendor_cost)

st.title("Inventory Calculator")
st.markdown(
    """
The **newsvendor model** picks the order quantity that minimizes expected cost,
balancing **understocking** (lost margin) against **overstocking** (holding cost).
The optimal order is the demand quantile at the *critical ratio*:
"""
)
st.latex(r"Q^* = F^{-1}\!\left(\frac{C_u}{C_u + C_o}\right)"
         r"\qquad C_u=\text{margin},\; C_o=\text{holding cost}")
st.caption(
    "Series list = top 500 by volume (of 30,490). Cost and savings shown below "
    "are for the **selected series** over the 28-day test horizon, under the "
    "margin/holding assumptions you set (M5 has no cost data)."
)

fc = load_forecasts()

c1, c2 = st.columns(2)
series = c1.selectbox("Series", sorted(fc["id"].unique().tolist()))
s = fc[fc["id"] == series].sort_values("date").copy()
price = float(s["sell_price"].iloc[0])
c2.metric("Sell price", f"${price:.2f}")

c1, c2 = st.columns(2)
margin_pct = c1.slider("Gross margin (% of price)", 5, 90, 30, step=5) / 100
hold_pct = c2.slider("Holding cost (% of price / period)", 1, 40, 15, step=1) / 100

unit_margin = price * margin_pct
unit_holding = price * hold_pct
cr = critical_ratio(unit_margin, unit_holding)

p10, p50, p90 = s["p10"].mean(), s["p50"].mean(), s["p90"].mean()
mu = p50
sigma = max((p90 - p10) / (2 * 1.2816), 1e-6)
z_star = stats.norm.ppf(np.clip(cr, 1e-4, 1 - 1e-4))
q_star = max(mu + z_star * sigma, 0)

opt_order = optimal_order_from_quantiles(
    s["p10"].values, s["p50"].values, s["p90"].values, cr)
cost_p50 = newsvendor_cost(s["p50"].values, s["sales"].values,
                           unit_margin, unit_holding).sum()
cost_opt = newsvendor_cost(opt_order, s["sales"].values,
                           unit_margin, unit_holding).sum()
savings = cost_p50 - cost_opt
savings_pct = 100 * savings / cost_p50 if cost_p50 > 0 else 0

st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Critical ratio", f"{cr:.3f}")
c2.metric("Optimal order Q*", f"{q_star:.1f}", f"z = {z_star:+.2f}")
c3.metric("Cost @ P50", f"${cost_p50:,.0f}")
c4.metric("Savings", f"${savings:,.0f}", f"{savings_pct:.1f}%")

st.subheader("Demand distribution & optimal order")

xs = np.linspace(max(mu - 4 * sigma, 0), mu + 4 * sigma, 240)
pdf = stats.norm.pdf(xs, mu, sigma)
ymax = float(pdf.max())
curve_df = pd.DataFrame({"units": xs, "density": pdf})
band_df = curve_df[(curve_df["units"] >= p10) & (curve_df["units"] <= p90)]

marks_df = pd.DataFrame({
    "x": [p10, p50, p90, q_star],
    "label": [f"P10 {p10:.0f}", f"P50 {p50:.0f}", f"P90 {p90:.0f}", f"Q* {q_star:.0f}"],
    "kind": ["quantile", "quantile", "quantile", "optimal"],
    "y": [ymax * 1.08] * 4,
})

yscale = alt.Scale(domain=[0, ymax * 1.18])

band = alt.Chart(band_df).mark_area(opacity=0.25, color="#4C78A8").encode(
    x=alt.X("units:Q", title="Demand (units)"),
    y=alt.Y("density:Q", title=None, scale=yscale, axis=None))

curve = alt.Chart(curve_df).mark_line(color="#1f4e8c", strokeWidth=2).encode(
    x=alt.X("units:Q", title="Demand (units)"),
    y=alt.Y("density:Q", scale=yscale, axis=None))

rules = alt.Chart(marks_df).mark_rule(size=2).encode(
    x="x:Q",
    color=alt.Color("kind:N",
                    scale=alt.Scale(domain=["quantile", "optimal"],
                                    range=["#999999", "#d62728"]),
                    legend=None),
    strokeDash=alt.StrokeDash("kind:N",
                              scale=alt.Scale(domain=["quantile", "optimal"],
                                              range=[[4, 3], [1, 0]]),
                              legend=None))

labels = alt.Chart(marks_df).mark_text(fontSize=11, dy=0, align="center").encode(
    x="x:Q", y=alt.Y("y:Q", scale=yscale, axis=None), text="label:N",
    color=alt.Color("kind:N",
                    scale=alt.Scale(domain=["quantile", "optimal"],
                                    range=["#666666", "#d62728"]),
                    legend=None))

chart = (band + curve + rules + labels).properties(height=300).configure_view(
    strokeWidth=0)
st.altair_chart(chart, use_container_width=True)
st.caption(
    "Blue curve = normal demand fit from P10/P50/P90. Shaded = P10-P90 (~80%). "
    "Grey dashed = quantiles. Red = optimal order Q*, which moves right as margin "
    "rises (higher critical ratio -> order more to avoid stockouts)."
)

s2 = s.copy()
s2["optimal_order"] = np.round(opt_order, 1)
s2["date"] = pd.to_datetime(s2["date"]).dt.date
with st.expander("Day-by-day order plan"):
    st.dataframe(s2[["date", "p10", "p50", "p90", "optimal_order", "sales"]],
                 use_container_width=True, hide_index=True)

st.divider()
st.subheader("Sensitivity: savings scale with margin structure")
try:
    sens = load_csv("sensitivity_analysis.csv")
    st.dataframe(sens, use_container_width=True, hide_index=True)
except Exception:
    st.caption("sensitivity_analysis.csv not found.")