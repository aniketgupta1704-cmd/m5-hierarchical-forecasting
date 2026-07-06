"""LightGBM quantile regression for M5 item-level forecasting."""
import numpy as np
import pandas as pd
import lightgbm as lgb


# Columns that must never be used as features
DROP_COLS = {
    "id", "item_id", "dept_id", "cat_id", "store_id", "state_id",
    "d", "date", "sales", "wm_yr_wk", "weekday", "year",
    "event_name_1", "event_type_1", "event_name_2", "event_type_2",
}

CATEGORICAL = ["dow", "month", "snap", "is_weekend", "is_event", "is_christmas"]


def get_feature_cols(df):
    return [c for c in df.columns if c not in DROP_COLS]


def train_quantile(X, y, alpha, categorical, params=None):
    base = dict(
        objective="quantile", alpha=alpha, metric="quantile",
        n_estimators=400, learning_rate=0.05,
        num_leaves=127, min_child_samples=100,
        subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
        n_jobs=-1, verbosity=-1,
    )
    if params:
        base.update(params)
    model = lgb.LGBMRegressor(**base)
    model.fit(X, y, categorical_feature=categorical)
    return model


def pinball_loss(y_true, y_pred, alpha):
    diff = y_true - y_pred
    return np.mean(np.maximum(alpha * diff, (alpha - 1) * diff))
