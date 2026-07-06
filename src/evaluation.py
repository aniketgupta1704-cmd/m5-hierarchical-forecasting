"""M5 evaluation: WRMSSE, RMSSE, pinball, calibration."""
import numpy as np
import pandas as pd


def rmsse(y_true, y_pred, y_train, season=1):
    """Root Mean Squared Scaled Error for one series.
    Denominator: naive (1-step, or seasonal) forecast MSE on training."""
    num = np.mean((y_true - y_pred) ** 2)
    denom = np.mean(np.diff(y_train, n=season) ** 2)
    if denom == 0:
        return np.nan
    return np.sqrt(num / denom)


def wrmsse(fc_df, train_hist, weights, id_col="id",
           truth_col="sales", pred_col="p50"):
    """Weighted RMSSE across all series.
    fc_df: [id, date, sales, p50] test rows.
    train_hist: dict id -> training sales array (for scaling denom).
    weights: dict id -> dollar-sales weight (sums to 1)."""
    scores, ws = [], []
    for sid, g in fc_df.groupby(id_col, observed=True):
        yt = g[truth_col].values
        yp = g[pred_col].values
        hist = train_hist.get(sid)
        if hist is None or len(hist) < 2:
            continue
        s = rmsse(yt, yp, hist)
        if np.isnan(s):
            continue
        scores.append(s)
        ws.append(weights.get(sid, 0.0))
    scores, ws = np.array(scores), np.array(ws)
    if ws.sum() == 0:
        return np.nan, scores
    ws = ws / ws.sum()
    return float(np.sum(scores * ws)), scores


def pinball_loss(y_true, y_pred, alpha):
    diff = y_true - y_pred
    return np.mean(np.maximum(alpha * diff, (alpha - 1) * diff))


def calibration_curve(fc_df, quantile_cols=(("p10",0.1),("p90",0.9))):
    """Empirical coverage per nominal quantile."""
    out = {}
    for col, q in quantile_cols:
        emp = (fc_df["sales"] <= fc_df[col]).mean()
        out[col] = {"nominal": q, "empirical": float(emp)}
    return out
