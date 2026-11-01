# Robustness and out-of-sample protocol

## Pre-specified diagnostics

1. **Calendar effects in three equal subsamples:** 1927-01..1959-12, 1960-01..1992-12, 1993-01..2025-12, each 396 months. HAC(24) joint Wald tests and Holm correction across the five industries **within each period**. Rejections in one period do not establish stability across all periods.
2. **Factor-model alpha inference:** re-estimate the original 1963-07..2026-06 regression specification with HAC bandwidths 6, 12, 24, and 36 months. All p-values are Holm-adjusted across the five industries **separately for each model/bandwidth**. This multiple-analysis comparison is a diagnostic; the original 24-month choice remains primary.
3. **SDF:** repeat the original six-moment/two-parameter GMM with Bartlett weights at NW lags 0, 6, 12 and uncentered/centered moment covariance. Any non-rejection only concerns these five assets.
4. **Approximate c restriction:** test `c=mu/Var(f)` using a conditional delta method based on estimated parameter covariance while **treating sample market variance as fixed**. This understates an important source of uncertainty; it is **not** an exact numerical reproduction of the original report's restriction procedure.
5. **Lagged-factor out-of-sample diagnostic:** for each month t, predict the industry excess return `y_t` using an intercept and realized five-factor returns at t−1. Fit the model only on earlier pairs `(f_{s-1},y_s)` with `s<t`. Start with 240 months of historical observations; expand and refit every month. Benchmark is the historical mean `mean(y_0,...,y_{t-1})`. Compute `R²_OOS=1-SSE(model)/SSE(benchmark)` and RMSE for each industry.

## Causal information set and interpretation

The lagged FF5 values are published ex-post factors and serve here as a **simplified diagnostic proxy** for information available after month t−1. The test assumes they could be observed without revisions/delays, which is not guaranteed for real-time historical trading. The benchmark is computed without current-month outcomes. There is **no trading P&L, position sizing, bid-ask spreads, costs, or genuine point-in-time vintage archive**.

There is no train/test contamination through the same-month return: an automated test changes a future target and same-month market return and checks that forecasts for that month remain unchanged. A negative R²_OOS indicates the lagged-factor specification underperformed the expanding historical-mean baseline; a positive number alone is not actionable.

## Data source and results

Run `python -m empirical_finance.cli --robustness`. This creates five additional CSV outputs plus one JSON diagnostic in the local `outputs/` directory, including historical source ZIP hashes in the existing manifest. Fresh public data may be revised after the documented run date. No output should be labeled a confirmed empirical result until the real-data integration job passes.
