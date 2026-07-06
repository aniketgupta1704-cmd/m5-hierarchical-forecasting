# Limitations & Honest Caveats

Every shortcut here was a compute-budget decision, not a methodological one — each
is a straightforward scale-up given more RAM/GPU. Documented for transparency.

## Data scope
- **730-day window** (last 2 years) instead of full M5 history. Recent data
  dominates a 28-day-horizon forecast, so the accuracy impact is small, but older
  seasonal patterns are excluded.

## Training compute
- **LightGBM trained on a 50% row subsample** for Colab memory. Full-data training
  is a direct scale-up and would modestly improve leaf accuracy.
- **N-BEATS trained on a 1,500-series stratified subset**, locally on Apple Silicon
  (MPS), because Darts/PyTorch/Colab version conflicts made cloud training
  impractical. Its WRMSSE (0.876) is therefore on a subset, not the full 30,490.
- **Backtest on a 2,000-series stratified sample** across 3 windows — enough to
  demonstrate temporal stability without retraining on all series three times.

## Modeling
- **Prophet fit at store×cat only** (30 series), not per-item — Prophet doesn't
  scale to 30,490 series in-session, and its role is the smooth aggregate anyway.
- **MinT is structural (WLS)**, not full-covariance (which needs a 30,490²
  covariance estimate). Structural weighting is the standard robust choice at scale.

## Business layer
- **Margins are assumed** (30% gross, 15% holding by default) — M5 ships no cost
  data. The *method* and the *shape* of the sensitivity curve are the transferable
  findings, not the specific dollar figures.

## Dashboard
- Interactive pages show the **top 500 series by volume** (of 30,490) for
  responsiveness. Forecasts exist for all series; the subset is a display choice.
- The app uses **precomputed forecasts** (hybrid design) — it does not load models
  live, which keeps the deploy fast and memory-safe.