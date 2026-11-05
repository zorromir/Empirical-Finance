# Methods

[Paper (PDF)](Empirical_finance.pdf) · [Public-data results](RESULTS_2026-11-01.md)

The paper uses returns from five value-weighted US industry portfolios: Oil, Banks, Textiles, Toys and Retail. The data and factors come from Kenneth French's Data Library.

## In the paper

| Section | Method |
| --- | --- |
| Setting the stage | Descriptive statistics and return distributions |
| Predictability | Monthly dummies, HAC(24) Wald tests, Holm correction, and three subperiods |
| Factor models | CAPM and FF5 regressions for five industries and momentum; momentum-sorted portfolios |
| Stochastic discount factors | Two-step GMM for the CAPM SDF, Hansen J test and slope restriction |

The calendar sample covers **1927–2025** (1,188 months). The factor and GMM sample covers **July 1963–June 2026** (756 months).

## What the public code reproduces

The package estimates the calendar-month tests, CAPM/FF5 regressions, momentum-factor alphas and the six-moment CAPM SDF. It also has separate scripts for subsample checks and simple forecasting exercises.

A few differences matter:

- **Factor regressions:** the paper's appendix uses HAC with 4 lags. The public package uses 24 lags by default and also applies Holm correction to the five industry-alpha p-values. As a result, significance can differ, particularly for Banks.
- **Momentum portfolios:** the report includes the decile comparison in Figure 5. The public package tests the French long–short momentum factor but does not recreate that figure.
- **SDF restriction:** the public code computes the Hansen J test. Its later slope-restriction check treats sample factor variance as fixed, so it is not the same test as in the paper.
- **Descriptive statistics:** the initial daily-return tables and figures are not part of this package.

For the GMM step, the normalized SDF is

`m_t = 1 - c(f_t - mu)`,

with five industry pricing moments `E[m_t(R_it - RF_t)] = 0` and one market-mean moment `E[f_t - mu] = 0`. With six moments and two parameters, the J test uses four degrees of freedom.

The public datasets may be revised after the original report's submission. Each run records the downloaded file hashes in `outputs/manifest.json`. Numerical checks do not establish trading profitability or prove that the CAPM holds.
