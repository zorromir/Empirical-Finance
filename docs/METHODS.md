# Methods and interpretation

This is a **new, independently written** public-data implementation motivated by a five-person Empirical Finance group study at Tilburg University (September 2026). It is not the group's original source archive or a transcription of unpublished coursework.

## Data selection

Three datasets are downloaded from [Kenneth French's Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html):
- Monthly **49 Industry Portfolios** (value-weighted return section).
- Monthly **Fama/French Five Factors (2×3)**.
- Monthly **Momentum Factor (Mom)**.

The 49-industry columns used are `Oil`, `Banks`, `Txtls` (Textiles), `Toys`, and `Rtail` (Retail). All date windows are *inclusive*: 1927-01 to 2025-12 for seasonality; 1963-07 to 2026-06 for factor regressions and GMM. The code fails on missing dates instead of silently taking a shorter sample.

All returns and factors are converted from **percentage points to decimals** at ingestion. Consequently an alpha of `0.0075` means **0.75 percent per month**, not 0.0075 percent. No sentinel observations (`-99.99`, `-999`) are treated as valid returns.

## Month-of-year tests

For industry i, estimate `R_it = a + sum_{m=2}^{12} b_m 1{month(t)=m} + e_it`. Test eleven restrictions `b_m=0` jointly with a chi-squared Wald test. Use Newey–West/Bartlett HAC standard errors with **24 monthly lags** and Holm correction across **five** industry p-values. This tests calendar-mean equality, not profitable predictability. The dependent variable is the *raw* monthly industry return.

## CAPM and five-factor OLS

For each industry, regress `R_it - RF_t` on the CAPM factor `Mkt-RF` or FF5 factors `Mkt-RF, SMB, HML, RMW, CMA`, always including an intercept. Use the **same 756 months** under both specifications. Point estimates are OLS, while alpha t- and p-values use Bartlett HAC with **24 lags**, without finite-sample correction. Correct the five industry-alpha p-values **within each model** using Holm. Report adjusted R-squared separately from pricing errors. Better fit does *not* imply smaller alpha.

## Momentum

The French momentum factor is a **self-financing long–short factor**. Regress **Mom itself**, *not* `Mom - RF`, on CAPM and FF5 factors. Its estimated intercept is a sample model-pricing discrepancy, not a realized trading profit net of costs.

## Two-step GMM: normalized CAPM stochastic discount factor

Define the market excess return `f_t`, five industry excess returns `e_it`, and two parameters `theta = (mu, c)`.

`m_t = 1 - c(f_t - mu)`.

The six sample moment conditions are:
- Five pricing moments `E[m_t e_it] = 0`.
- One normalization/identification moment `E[f_t - mu] = 0`.

First minimize the quadratic average moment norm with identity weighting. At that estimate, compute the **six-lag Bartlett long-run covariance** of the moments (uncentered autocovariances by default) and use its pseudoinverse in step two. For final moment mean `gbar` and second-step weighting `W`, report `J = T gbar' W gbar` and an asymptotic chi-square p-value with **6 - 2 = 4 degrees of freedom**. The `se_mu` and `se_c` numbers use a conventional efficient-GMM asymptotic covariance estimate; finite-sample properties and model misspecification require caution.

The method does **not** implement the archived report's additional restriction-on-c test. It also excludes momentum from the six moment conditions. Not rejecting J is **not** evidence that the SDF is true.

## Vintage, authorship and reproduction caveats

Kenneth French's historical datasets are revised and CRSP's underlying data methodology has changed. A fresh download on a later date may not exactly match the files used for the 2026 MSc group report. Each run saves SHA-256 hashes of the exact ZIP inputs in `outputs/manifest.json`. Retain these hashes when comparing historical results, and do not claim to have reproduced particular group numbers without a documented comparison.

There is **no strategy simulation**, out-of-sample test, estimated transaction-cost model, portfolio optimization or recommendation to trade. No private coursework data, original group code or report PDF is committed. All original empirical-finance group findings should be credited to all five co-authors.
