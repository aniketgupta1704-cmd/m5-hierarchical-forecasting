"""Local N-BEATS training for M5 deep model (Apple Silicon / MPS or CPU).

Run from the project root (same level as data/ and models/):
    python run_deep_local.py

Caches the trained model to models/deep_model.pt -- reruns skip training and
go straight to prediction. Delete that file to force a retrain.

Requires: pip install "u8darts[torch]" pandas pyarrow numpy
"""
import os
import gc
import numpy as np
import pandas as pd
import torch
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from darts.models import NBEATSModel
from darts.utils.likelihood_models import QuantileRegression

# ---- device selection ----
accelerator = "mps" if torch.backends.mps.is_available() else "cpu"
# accelerator = "cpu"   # <- uncomment to force CPU (reliable, only a bit slower)
print("device:", accelerator)

MODEL_PATH = "models/deep_model.pt"

# ---- load & sample 1500 representative series ----
feat = pd.read_parquet(
    "data/processed/features.parquet",
    columns=["id", "store_id", "cat_id", "date", "sales"],
)
all_ids = feat[["id", "store_id", "cat_id"]].drop_duplicates()
sample_ids = (
    all_ids.groupby(["store_id", "cat_id"], observed=True)[["id"]]
    .apply(lambda d: d.sample(min(len(d), 50), random_state=42))
    .reset_index(drop=True)["id"]
)
sample_ids = sample_ids.sample(min(len(sample_ids), 1500), random_state=42).tolist()
print(len(sample_ids), "series")

sub = feat[feat["id"].isin(sample_ids)].copy()
del feat
gc.collect()

cutoff = sub["date"].max() - pd.Timedelta(days=28)
train_long = sub[sub["date"] <= cutoff]
test_long = sub[sub["date"] > cutoff]

# ---- to TimeSeries ----
series_list, kept_ids = [], []
for sid in sample_ids:
    g = train_long[train_long["id"] == sid].sort_values("date")
    if len(g) < 60:
        continue
    ts = TimeSeries.from_dataframe(g, time_col="date", value_cols="sales", freq="D")
    series_list.append(ts)
    kept_ids.append(sid)
print(len(series_list), "converted")

# ---- scale, then cast to float32 (MPS does not support float64) ----
scaler = Scaler()
series_scaled = scaler.fit_transform(series_list)
series_scaled = [s.astype(np.float32) for s in series_scaled]

# ---- train (or load cached) ----
if os.path.exists(MODEL_PATH):
    print("loading cached model...")
    model = NBEATSModel.load(MODEL_PATH)
else:
    model = NBEATSModel(
        input_chunk_length=56,
        output_chunk_length=28,
        num_stacks=10,
        num_blocks=1,
        num_layers=4,
        layer_widths=256,
        n_epochs=15,
        batch_size=512,
        likelihood=QuantileRegression(quantiles=[0.1, 0.5, 0.9]),
        random_state=42,
        pl_trainer_kwargs={
            "accelerator": accelerator,
            "devices": 1,
            "precision": "32-true",
        },
    )
    model.fit(series_scaled, verbose=True)
    print("training done")
    os.makedirs("models", exist_ok=True)
    model.save(MODEL_PATH)

# ---- probabilistic forecast ----
preds = scaler.inverse_transform(
    model.predict(n=28, series=series_scaled, num_samples=200)
)


def extract_quantiles(ts, qs=(0.1, 0.5, 0.9)):
    """Version-robust quantile extraction from a probabilistic TimeSeries."""
    if hasattr(ts, "quantiles_df"):
        df = ts.quantiles_df(list(qs)).reset_index()
        df.columns = ["date"] + [f"q{int(q * 100)}" for q in qs]
        return df
    out, times = {}, None
    for q in qs:
        if hasattr(ts, "quantile_timeseries"):
            qts = ts.quantile_timeseries(q)
        else:
            qts = ts.quantile(q)
        out[f"q{int(q * 100)}"] = qts.values().flatten()
        times = qts.time_index
    df = pd.DataFrame(out)
    df.insert(0, "date", times)
    return df


rows = []
for sid, ts in zip(kept_ids, preds):
    df = extract_quantiles(ts, (0.1, 0.5, 0.9))
    df.columns = ["date", "p10", "p50", "p90"]
    df["id"] = sid
    rows.append(df)
deep_fc = pd.concat(rows, ignore_index=True)
deep_fc[["p10", "p50", "p90"]] = deep_fc[["p10", "p50", "p90"]].clip(lower=0)

os.makedirs("data/processed", exist_ok=True)
deep_fc.to_parquet("data/processed/forecasts_deep.parquet", index=False)

# ---- quick eval ----
ev = deep_fc.merge(test_long[["id", "date", "sales"]], on=["id", "date"], how="inner")


def pinball(y, p, a):
    d = y - p
    return np.mean(np.maximum(a * d, (a - 1) * d))


for n, a in [("p10", 0.1), ("p50", 0.5), ("p90", 0.9)]:
    print(f"pinball {n}: {pinball(ev['sales'].values, ev[n].values, a):.4f}")
print("P50 RMSE:", round(np.sqrt(((ev["p50"] - ev["sales"]) ** 2).mean()), 3))
cov = ((ev["sales"] >= ev["p10"]) & (ev["sales"] <= ev["p90"])).mean()
print("coverage:", round(cov, 3))
print("saved forecasts_deep.parquet + deep_model.pt")