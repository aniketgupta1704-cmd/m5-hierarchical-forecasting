"""Seasonal naive baseline: forecast = value from 7 days ago (weekly season)."""
import pandas as pd
import numpy as np


def seasonal_naive_forecast(series, horizon=28, season=7):
    """series: 1D array of historical daily sales (sorted by date).
    Returns horizon-length forecast by tiling the last `season` values."""
    last_season = np.asarray(series)[-season:]
    reps = int(np.ceil(horizon / season))
    return np.tile(last_season, reps)[:horizon]


def forecast_all(agg_df, horizon=28, season=7, key="series_id"):
    """agg_df: long frame with columns [key, date, sales], sorted.
    Returns DataFrame [key, date, yhat] for the horizon after each series' last date."""
    out = []
    for sid, g in agg_df.groupby(key, observed=True):
        g = g.sort_values("date")
        yhat = seasonal_naive_forecast(g["sales"].values, horizon, season)
        future_dates = pd.date_range(g["date"].max() + pd.Timedelta(days=1),
                                     periods=horizon, freq="D")
        out.append(pd.DataFrame({key: sid, "date": future_dates, "yhat": yhat}))
    return pd.concat(out, ignore_index=True)
