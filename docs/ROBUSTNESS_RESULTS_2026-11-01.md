# Additional results — 1 November 2026

These figures come from the public Python code. Some repeat parts of the [paper](Empirical_finance.pdf); others are later checks.

## Calendar effects by period

Holm-adjusted p-values from joint HAC(24) tests:

| Industry | 1927–1959 | 1960–1992 | 1993–2025 |
| --- | ---: | ---: | ---: |
| Oil | **0.0481** | 0.1586 | 0.1263 |
| Banks | 0.5541 | 0.1586 | 0.0684 |
| Textiles | **0.0006** | **0.0004** | **0.0045** |
| Toys | 0.5541 | 0.1586 | **0.0263** |
| Retail | 0.5541 | 0.1586 | **0.0003** |

Only Textiles is significant in all three periods. This matches the main finding in the paper's subperiod analysis.

## Factor-model inference

At HAC(24), the Holm-adjusted p-values for FF5 industry alphas are **0.1349 for Banks**, **0.0076 for Textiles** and **0.0348 for Toys**. Textiles and Toys also remain significant across the tested HAC bandwidths of 6, 12, 24 and 36.

The reported group paper uses different factor-regression inference conventions, so these p-values should not be presented as its original results.

## GMM sensitivity

Changing the Newey–West lag from 0 to 6 to 12 (without centering) gives Hansen J p-values of **0.1704**, **0.3108** and **0.3519**. None rejects at 5%.

The approximate conditional slope check gives p = **0.4103**. This is not the paper's slope-restriction p = **0.456**, because the calculation handles the market variance differently.

## Lagged-factor forecasts

Out-of-sample R² relative to an expanding historical-mean forecast, July 1983–June 2026:

| Oil | Banks | Textiles | Toys | Retail |
| ---: | ---: | ---: | ---: | ---: |
| −1.37% | −1.90% | +0.52% | −1.91% | −0.96% |

Four industries do worse than the mean forecast. Textiles improves slightly, but this is not enough to claim useful predictability. The factor data are not verified point-in-time, and no trading costs are included.

The code can regenerate the full CSV and JSON outputs with `python -m empirical_finance.cli --robustness`.
