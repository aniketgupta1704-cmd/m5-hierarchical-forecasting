"""Shared utilities for the M5 forecasting dashboard."""
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


@st.cache_data
def load_forecasts():
    return pd.read_parquet(DATA_DIR / "app_forecasts.parquet")


@st.cache_data
def load_csv(name):
    return pd.read_csv(DATA_DIR / name)


# ---------- newsvendor math (runs live) ----------
def critical_ratio(unit_margin, unit_holding_cost):
    return unit_margin / (unit_margin + unit_holding_cost)


def optimal_order_from_quantiles(p10, p50, p90, cr):
    sigma = np.maximum((p90 - p10) / (2 * 1.2816), 1e-6)
    z = stats.norm.ppf(np.clip(cr, 1e-4, 1 - 1e-4))
    return np.maximum(p50 + z * sigma, 0)


def newsvendor_cost(order_qty, actual_demand, unit_margin, unit_holding_cost):
    understock = np.maximum(actual_demand - order_qty, 0) * unit_margin
    overstock = np.maximum(order_qty - actual_demand, 0) * unit_holding_cost
    return understock + overstock