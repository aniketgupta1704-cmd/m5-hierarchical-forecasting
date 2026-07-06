"""Prophet forecasting at aggregated level with events & holidays."""
import pandas as pd
import numpy as np
from prophet import Prophet


def build_holidays(cal_events):
    """cal_events: DataFrame [date, event_name] of non-null event days.
    Returns Prophet-format holidays frame."""
    h = cal_events.rename(columns={"date": "ds", "event_name": "holiday"})
    h = h[["holiday", "ds"]].drop_duplicates()
    # Christmas closures as their own holiday
    xmas = pd.DataFrame({
        "holiday": "Christmas",
        "ds": pd.to_datetime(["2014-12-25", "2015-12-25"]),
    })
    return pd.concat([h, xmas], ignore_index=True)


def fit_predict_one(train_df, holidays, horizon=28, snap_future=None):
    """train_df: [ds, y, snap]. Returns forecast frame incl. yhat, lower, upper."""
    m = Prophet(
        holidays=holidays,
        weekly_seasonality=True,
        yearly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        interval_width=0.80,   # gives ~P10/P90 band
    )
    m.add_regressor("snap")
    m.fit(train_df)
    future = m.make_future_dataframe(periods=horizon, freq="D")
    # attach snap for future rows
    future = future.merge(train_df[["ds", "snap"]], on="ds", how="left")
    if snap_future is not None:
        future = future.merge(snap_future, on="ds", how="left", suffixes=("", "_f"))
        future["snap"] = future["snap"].fillna(future["snap_f"])
    future["snap"] = future["snap"].fillna(0)
    fcst = m.predict(future)
    return m, fcst
