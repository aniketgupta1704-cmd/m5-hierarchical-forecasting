# Methodology

## Data
- **Source:** M5 Forecasting – Accuracy (Kaggle). Walmart daily unit sales.
- **Scale:** 30,490 leaf series = 3,049 items × 10 stores, across 3 states.
- **Window:** last 730 days (2014-05-24 → 2016-05-22) of the full history, to fit
  a Colab compute budget. Older history excluded (see limitations).
- **Hierarchy:** Total → State → Store → Category → Department → Item×Store.

## Feature engineering
Per-series (grouped by `id`) to prevent cross-series leakage:
- **Lags:** 1, 7, 28
- **Rolling stats:** mean & std over 7/14/28/56, all computed on `sales.shift(1)`
  (no same-day leakage)
- **Intermittency:** trailing zero-fraction over 28/56
- **Calendar:** day-of-week, day-of-month, cyclical sin/cos, is_weekend
- **Events:** SNAP flags, holiday/event indicators, Christmas closure flag
- **Price:** lag, % change, price vs item mean (promo signal), 28-day momentum

**Anti-leakage rule:** shift before rolling; verified that series-start `lag_1`
is null (no bleed across item boundaries).

## Models
| Model | Level | Role |
|-------|-------|------|
| Seasonal naive | all | baseline (WRMSSE denominator) |
| Prophet | store×cat (30) | smooth aggregate, holidays + SNAP |
| LightGBM (quantile) | leaves (30,490) | P10/P50/P90, main workhorse |
| N-BEATS (Darts) | 1,500-series subset | deep-learning comparison |

## Probabilistic forecasting
- Quantile regression (LightGBM `objective="quantile"`, α = 0.1/0.5/0.9)
- Predictions clipped ≥ 0 and row-sorted to prevent quantile crossing
- Evaluated with pinball loss per quantile + empirical coverage

## Hierarchical reconciliation
- **Bottom-up:** sum leaves to parents (coherent by construction)
- **MinT (structural):** block-wise per store, exploiting M5's block-diagonal
  hierarchy (ten ~3,049² inversions instead of one 30,490²)
- Cross-level MinT combining Prophet (aggregate) + LightGBM (leaves) demonstrates
  where reconciliation adds value

## Evaluation
- **WRMSSE** — the official M5 metric (dollar-weighted RMSSE)
- **Calibration** — empirical vs nominal coverage per quantile
- **Backtest** — 3 rolling 28-day windows on a 2,000-series stratified sample

## Business layer
- **Newsvendor model:** optimal order = demand quantile at critical ratio
  CR = Cu / (Cu + Co)
- **Cost-of-error:** realized cost of ordering at P50 vs newsvendor-optimal
- **Sensitivity:** savings scale with margin structure (0% at CR=0.5 → 55% at CR=0.93)