"""Feature engineering for M5 forecasting. All temporal features are
computed per-series (groupby id) to prevent leakage across series boundaries."""
import pandas as pd
import numpy as np


def add_lags(df, lags=(1, 7, 28)):
    g = df.groupby("id", observed=True)["sales"]
    for l in lags:
        df[f"lag_{l}"] = g.shift(l).astype("float32")
    return df


def add_rolling(df, windows=(7, 14, 28, 56), base_shift=1):
    """Rolling stats on shifted sales (no same-day leakage)."""
    shifted = df.groupby("id", observed=True)["sales"].shift(base_shift)
    df["_shifted"] = shifted
    g = df.groupby("id", observed=True)["_shifted"]
    for w in windows:
        df[f"roll_mean_{w}"] = g.transform(lambda s: s.rolling(w, min_periods=1).mean()).astype("float32")
        df[f"roll_std_{w}"]  = g.transform(lambda s: s.rolling(w, min_periods=1).std()).astype("float32")
    # zero-demand density: fraction of zero days in trailing window (intermittency signal)
    for w in (28, 56):
        df[f"roll_zero_frac_{w}"] = g.transform(
            lambda s: s.eq(0).rolling(w, min_periods=1).mean()
        ).astype("float32")
    return df.drop(columns=["_shifted"])


def add_calendar(df):
    df["dow"] = df["date"].dt.dayofweek.astype("int8")
    df["dom"] = df["date"].dt.day.astype("int8")
    df["week"] = df["date"].dt.isocalendar().week.astype("int8")
    # cyclical encodings
    df["dow_sin"] = np.sin(2 * np.pi * df["dow"] / 7).astype("float32")
    df["dow_cos"] = np.cos(2 * np.pi * df["dow"] / 7).astype("float32")
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12).astype("float32")
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12).astype("float32")
    df["is_weekend"] = df["dow"].isin([5, 6]).astype("int8")
    return df


def add_events(df):
    df["is_event"] = df["event_name_1"].notna().astype("int8")
    # Christmas: the chain-wide closure days
    df["is_christmas"] = ((df["month"] == 12) & (df["dom"] == 25)).astype("int8")
    # snap already present as int8
    return df


def add_price_features(df):
    g = df.groupby("id", observed=True)["sell_price"]
    df["price_lag_1"] = g.shift(1).astype("float32")
    df["price_change"] = (df["sell_price"] / df["price_lag_1"] - 1).astype("float32")
    # price vs each item's own historical mean (promo signal)
    df["price_rel_mean"] = (df["sell_price"] / g.transform("mean")).astype("float32")
    df["price_momentum"] = g.transform(
        lambda s: s.shift(1).rolling(28, min_periods=1).mean()
    ).astype("float32")
    return df


def build_features(df):
    df = df.sort_values(["id", "date"]).reset_index(drop=True)
    df = add_lags(df)
    df = add_rolling(df)
    df = add_calendar(df)
    df = add_events(df)
    df = add_price_features(df)
    return df
