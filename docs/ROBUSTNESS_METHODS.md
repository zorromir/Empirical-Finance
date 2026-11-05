# Additional checks

These checks extend the [group paper](Empirical_finance.pdf). They are not all part of the submitted analysis.

- **Subperiods:** repeat month-of-year tests for 1927–1959, 1960–1992 and 1993–2025, using HAC(24) and Holm correction within each period.
- **Factor regressions:** compare alpha inference with HAC lags 6, 12, 24 and 36.
- **GMM:** vary the long-run covariance bandwidth and centering convention.
- **Slope restriction:** check `c = mu / Var(f)` using a conditional Wald calculation. It treats the estimated market variance as fixed and is not identical to the paper's test.
- **Forecasting:** regress monthly industry excess returns on the *previous month's* five factor returns. Refit with an expanding sample, starting from 240 months, and compare with a historical-mean forecast.

The forecasting exercise only checks whether this lagged specification predicts better than a simple benchmark. The public factor histories may have been revised, so this is not a point-in-time trading backtest.

Run `python -m empirical_finance.cli --robustness`. See the [results](ROBUSTNESS_RESULTS_2026-11-01.md).
