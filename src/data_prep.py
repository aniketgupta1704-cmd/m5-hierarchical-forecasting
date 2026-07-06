
"""Data preparation for M5 hierarchical forecasting."""
import pandas as pd
import numpy as np


def load_raw(raw_dir="data/raw"):
    sales = pd.read_csv(f"{raw_dir}/sales_train_evaluation.csv")
    calendar = pd.read_csv(f"{raw_dir}/calendar.csv")
    prices = pd.read_csv(f"{raw_dir}/sell_prices.csv")
    return sales, calendar, prices

def melt_sales(sales, last_n_days=730):
    """Wide (d_1..d_N columns) -> long. Optionally keep only last N days."""
    id_cols = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]
    day_cols = [c for c in sales.columns if c.startswith("d_")]
    if last_n_days is not None:
        day_cols = day_cols[-last_n_days:]
    long = sales.melt(
        id_vars=id_cols, value_vars=day_cols,
        var_name="d", value_name="sales"
    )
    long["sales"] = long["sales"].astype(np.int32)
    # downcast ID strings to categoricals (major memory saving)
    for c in id_cols:
        long[c] = long[c].astype("category")
    return long

def attach_calendar(long, calendar):
    cal = calendar[[
        "d", "date", "wm_yr_wk", "weekday", "wday", "month", "year",
        "event_name_1", "event_type_1", "event_name_2", "event_type_2",
        "snap_CA", "snap_TX", "snap_WI"
    ]].copy()
    long = long.merge(cal, on="d", how="left")
    long["date"] = pd.to_datetime(long["date"])
    return long


def attach_snap(long):
    """Pick the SNAP flag matching each row's state."""
    state = long["state_id"].values
    long["snap"] = np.select(
        [state == "CA", state == "TX", state == "WI"],
        [long["snap_CA"], long["snap_TX"], long["snap_WI"]],
        default=0
    ).astype(np.int8)
    return long.drop(columns=["snap_CA", "snap_TX", "snap_WI"])


def attach_prices(long, prices):
    long = long.merge(prices, on=["store_id", "item_id", "wm_yr_wk"], how="left")
    return long


def build_sales_long(raw_dir="data/raw", last_n_days=730):
    sales, calendar, prices = load_raw(raw_dir)
    long = melt_sales(sales, last_n_days=last_n_days)
    long = attach_calendar(long, calendar)
    long = attach_snap(long)
    long = attach_prices(long, prices)
    # downcast event columns
    for c in ["event_name_1", "event_type_1", "event_name_2", "event_type_2", "weekday"]:
        long[c] = long[c].astype("category")
    for c in ["wday", "month"]:
        long[c] = long[c].astype("int8")
    long["year"] = long["year"].astype("int16")
    return long


def build_hierarchical_map(sales):
    """The 12 M5 aggregation levels reference table (per-item leaf mapping)."""
    hmap = sales[[
        "id", "item_id", "dept_id", "cat_id", "store_id", "state_id"
    ]].drop_duplicates().reset_index(drop=True)
    hmap["total"] = "Total"
    return hmap
