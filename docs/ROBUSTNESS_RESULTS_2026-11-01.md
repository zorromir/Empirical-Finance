# Robustness results — 1 November 2026 public-data run

These results were generated with `python -m empirical_finance.cli --robustness` from public Kenneth French CSV archives on 1 November 2026. They are **historical diagnostics, not an investable strategy**, and reuse the same data-vintage hashes documented in [the original run](RESULTS_2026-11-01.md).

The package ran successfully in GitHub Actions. The separate offline unit-test suite passed for Python 3.10 and 3.12, including leakage and sample-boundary checks. The full numerical outputs (CSV, JSON and manifest) are saved as temporary workflow artifacts; rerunning regenerates them.

## 1. Calendar subperiods — HAC(24), Holm-adjusted within period

Three **non-overlapping 396-month** samples. The p-values below are adjusted for **five industries within each period**, not also for all periods/bandwidth specifications.

| Industry | 1927–1959 | 1960–1992 | 1993–2025 |
| --- | ---: | ---: | ---: |
| Oil | **0.0481** | 0.1586 | 0.1263 |
| Banks | 0.5541 | 0.1586 | 0.0684 |
| Textiles | **0.0006** | **0.0004** | **0.0045** |
| Toys | 0.5541 | 0.1586 | **0.0263** |
| Retail | 0.5541 | 0.1586 | **0.0003** |

At 5% family-wise alpha, **only Textiles rejects in all three periods**. Oil rejects only in the first, while Toys and Retail reject in the last. The calendar effect is therefore not uniformly stable across industries or historical periods. No economic mechanism or profitable strategy is established by these tests.

## 2. FF5 industry alpha — HAC bandwidth sensitivity

The primary specification uses HAC(24); the additional bandwidths are diagnostic. P-values are Holm-adjusted across the five **FF5 industry intercepts separately for each bandwidth**.

| Industry | HAC(6) | HAC(12) | HAC(24) | HAC(36) |
| --- | ---: | ---: | ---: | ---: |
| Oil | 0.6408 | 0.7159 | 0.7408 | 0.6812 |
| Banks | 0.1071 | 0.1051 | 0.1349 | 0.1577 |
| Textiles | **0.0013** | **0.0037** | **0.0076** | **0.0120** |
| Toys | **0.0183** | **0.0294** | **0.0348** | **0.0299** |
| Retail | 0.6408 | 0.7159 | 0.7408 | 0.6812 |

**Textiles and Toys** remain significant at 5% under these particular choices; the other three do not. These are **in-sample pricing-error tests**, not forward-looking return forecasts. Inspecting several bandwidths creates an additional analyst-choice dimension not covered by the within-bandwidth Holm correction.

## 3. Two-step GMM — Newey–West bandwidth and centering

The **same six moment conditions and five industry test assets** are used in all rows. The J test has four asymptotic degrees of freedom.

| NW lag | Moment covariances | c estimate | J statistic | J-test p-value |
| --- | --- | ---: | ---: | ---: |
| 0 | Uncentered | 3.2814 | 6.4123 | 0.1704 |
| 6 | Uncentered (primary) | 3.5704 | 4.7784 | 0.3108 |
| 12 | Uncentered | 3.4519 | 4.4218 | 0.3519 |
| 0 | Centered | 3.2855 | 6.4672 | 0.1669 |
| 6 | Centered | 3.6072 | 5.0043 | 0.2869 |
| 12 | Centered | 3.5060 | 4.7880 | 0.3097 |

None rejects at 5%; the variation in slope estimates and p-values nevertheless demonstrates sensitivity to covariance estimation.

An **additional approximate slope restriction** `c=mu/Var(f)` gives a conditional Wald statistic ≈ 0.678 and p ≈ **0.4103**, treating the observed market sample variance as **fixed** in the delta method. This excludes variance-estimation uncertainty and **must not be described as reproduction of the original group's slope-restriction p ≈ 0.456**.

## 4. Walk-forward diagnostic — genuine lagged features, but not point-in-time trading data

The model predicts monthly excess industry return `y_t` using an intercept and **previous-month** FF5 factor values `f_{t−1}`. It expands the training window and refits each month; benchmark is the historical excess-return mean computed strictly using earlier observations.

**Training:** first 240 calendar months starting July 1963.  
**Out-of-sample evaluation:** July 1983–June 2026 (516 monthly forecasts per industry).

| Industry | OOS R² vs historical mean | RMSE, lagged FF5 | RMSE, historical mean |
| --- | ---: | ---: | ---: |
| Oil | −1.37% | 0.06367 | 0.06323 |
| Banks | −1.90% | 0.06249 | 0.06190 |
| Textiles | +0.52% | 0.08270 | 0.08292 |
| Toys | −1.91% | 0.07058 | 0.06992 |
| Retail | −0.96% | 0.05377 | 0.05351 |

RMSE values are in **decimal return units** (e.g. 0.05 is five percentage points). Four of five series **underperform** the expanding historical-mean benchmark. The slight positive result for Textiles is not a significant edge claim or sufficient evidence of stable predictability.

**Information-set caveat:** The historical factor series were downloaded from a *later revised vintage*; they are not proven to have been published or tradeable in real time at each forecast origin. This tests lag structure and temporal sample isolation, not a point-in-time strategy. No costs, execution, transaction restrictions, multiple-model adjustments, or model-selection holdout are included.

## Research conclusion

The factor-model in-sample fit improvement and two FF5 alpha rejections are reproducible for these selected settings; they do not imply predictive skill. Calendar effects vary sharply across subperiods. The lagged-factor specification provides little or no incremental forecasting accuracy against a simple feasible benchmark. A strong scientific claim remains limited to the **tested data, moments, assumptions and chosen samples**.

[Methods, limitations and test construction](ROBUSTNESS_METHODS.md)
