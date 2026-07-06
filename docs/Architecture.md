# Architecture

## Pipeline
```
Raw M5 sales (wide)
      │  melt + join calendar/prices
      ▼
sales_long.parquet ──► feature engineering ──► features.parquet
      │                                              │
      │                                              ▼
      │                        ┌─────────────────────────────────┐
      │                        │  Models (28-day horizon)         │
      │                        │  • seasonal naive (baseline)     │
      │                        │  • Prophet    (store×cat)        │
      │                        │  • LightGBM   (leaves, P10/50/90)│
      │                        │  • N-BEATS    (1,500 subset)     │
      │                        └─────────────────────────────────┘
      │                                              │
      ▼                                              ▼
hierarchical_map.csv ──► MinT reconciliation ──► forecasts_reconciled.parquet
                                                     │
                          WRMSSE / calibration / backtest
                                                     │
                                                     ▼
                          newsvendor inventory optimizer
                                                     │
                                                     ▼
                          Streamlit dashboard (4 pages)
```

## Repo layout
```
m5-hierarchical-forecasting/
├── notebooks/     01–07: EDA → features → models → reconciliation → business
├── src/           data_prep, features, models/, reconciliation, evaluation, inventory_optimizer
├── app/           Streamlit app (app.py, pages/, utils, diagrams, data/)
├── models/        saved model artifacts (git-ignored)
├── data/          raw (ignored) + processed (ignored, except app/data)
├── reports/       calibration_report.html, model_comparison.pdf
└── docs/          architecture, methodology, limitations, images
```

## Design choices
- **Hybrid dashboard:** precomputed forecasts (fast, deploy-safe) + live newsvendor
  math (interactive). No models loaded at runtime.
- **Block-wise MinT:** exploits M5's per-store block-diagonal hierarchy for tractable
  reconciliation at 30,490-series scale.
- **Quantile-first:** P10/P50/P90 throughout, because 69% of series are intermittent
  and point forecasts are inadequate.