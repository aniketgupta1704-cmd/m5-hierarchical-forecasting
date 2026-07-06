"""Newsvendor inventory optimization from probabilistic forecasts."""
import numpy as np
import pandas as pd
from scipy import stats


def critical_ratio(unit_margin, unit_holding_cost):
    """CR = Cu / (Cu + Co). The optimal service level (fractile)."""
    return unit_margin / (unit_margin + unit_holding_cost)


def optimal_order_from_quantiles(p10, p50, p90, cr):
    """Interpolate the optimal order quantity from three known quantiles.
    Fits a normal via P50 (mean) and (P90-P10)/(2*1.2816) (sigma), then
    reads the CR-th quantile. Robust when only 3 quantiles are available."""
    sigma = (p90 - p10) / (2 * 1.2816)          # 1.2816 = z(0.9)
    sigma = np.maximum(sigma, 1e-6)
    z = stats.norm.ppf(np.clip(cr, 1e-4, 1 - 1e-4))
    return np.maximum(p50 + z * sigma, 0)


def newsvendor_cost(order_qty, actual_demand, unit_margin, unit_holding_cost):
    """Realized cost: lost margin on stockouts + holding cost on overage."""
    understock = np.maximum(actual_demand - order_qty, 0) * unit_margin
    overstock = np.maximum(order_qty - actual_demand, 0) * unit_holding_cost
    return understock + overstock


def compare_policies(fc_df, unit_margin, unit_holding_cost,
                     truth_col="sales"):
    """Compare ordering at P50 vs newsvendor-optimal against realized cost.
    fc_df: [id, date, p10, p50, p90, sales]. Returns summary dict."""
    cr = critical_ratio(unit_margin, unit_holding_cost)
    opt_order = optimal_order_from_quantiles(
        fc_df["p10"].values, fc_df["p50"].values, fc_df["p90"].values, cr)

    cost_p50 = newsvendor_cost(fc_df["p50"].values, fc_df[truth_col].values,
                               unit_margin, unit_holding_cost)
    cost_opt = newsvendor_cost(opt_order, fc_df[truth_col].values,
                               unit_margin, unit_holding_cost)
    return {
        "critical_ratio": round(cr, 3),
        "total_cost_p50": float(cost_p50.sum()),
        "total_cost_newsvendor": float(cost_opt.sum()),
        "savings": float(cost_p50.sum() - cost_opt.sum()),
        "savings_pct": round(100 * (cost_p50.sum() - cost_opt.sum())
                             / max(cost_p50.sum(), 1e-9), 2),
    }
