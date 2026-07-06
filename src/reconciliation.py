"""Hierarchical reconciliation: bottom-up, top-down, MinT."""
import numpy as np
import pandas as pd


def build_hierarchy_matrix(leaf_ids, mapping):
    m = mapping.set_index("id").loc[leaf_ids]
    levels = {
        "total": lambda r: "Total",
        "state": lambda r: r["state_id"],
        "store": lambda r: r["store_id"],
        "cat":   lambda r: r["cat_id"],
        "state_cat": lambda r: f"{r['state_id']}_{r['cat_id']}",
        "store_cat": lambda r: f"{r['store_id']}_{r['cat_id']}",
    }
    agg_rows, agg_names = [], []
    for lvl, fn in levels.items():
        keys = m.apply(fn, axis=1)
        for val in keys.unique():
            agg_rows.append((keys == val).astype(float).values)
            agg_names.append(f"{lvl}::{val}")
    S_agg = np.vstack(agg_rows) if agg_rows else np.empty((0, len(leaf_ids)))
    return S_agg, agg_names


def bottom_up(leaf_fc, S_agg):
    return S_agg @ leaf_fc


def top_down(total_fc, proportions):
    return np.outer(proportions, total_fc)


def reconcile_mint_by_store(leaf_fc, leaf_ids, mapping, store_col="store_id"):
    """Block-wise structural MinT: reconcile within each store independently.
    Exploits M5's block-diagonal hierarchy — items roll up only within their
    own store, so the 30,490-wide MinT inversion decomposes into ten
    independent ~3,049-wide problems."""
    m = mapping.set_index("id").loc[leaf_ids]
    stores = m[store_col].values
    recon = np.zeros_like(leaf_fc)

    for store in pd.unique(stores):
        idx = np.where(stores == store)[0]
        sub_ids = [leaf_ids[i] for i in idx]
        sub_leaf = leaf_fc[idx]
        sm = mapping[mapping["id"].isin(sub_ids)].set_index("id").loc[sub_ids]

        level_fns = [
            lambda r: "store_total",
            lambda r: r["cat_id"],
            lambda r: r["dept_id"],
        ]
        agg_rows = []
        for fn in level_fns:
            keys = sm.apply(fn, axis=1)
            for val in keys.unique():
                agg_rows.append((keys == val).astype(float).values)
        S_sub = np.vstack(agg_rows)

        base_agg = S_sub @ sub_leaf
        n = sub_leaf.shape[0]
        S = np.vstack([S_sub, np.eye(n)])
        y = np.vstack([base_agg, sub_leaf])
        w = S.sum(axis=1)
        Winv = np.diag(1.0 / w)
        StWinv = S.T @ Winv
        P = np.linalg.inv(StWinv @ S) @ StWinv
        recon[idx] = np.clip(P @ y, 0, None)

    return recon
