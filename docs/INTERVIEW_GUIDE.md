# Quantitative research interview guide — actual published methods

These are methodological explanations for the portfolio's three research projects. The best answer is one you can derive, implement and explain independently. Do not memorize unsupported performance figures or attribute group contributions exclusively to yourself.

## Five-minute project summary

- **Industrial modelling:** A six-month company project adapting published flow and uncertainty models to a specific production problem. The public [pipeline demonstration](https://github.com/zorromir/pipeline-flow-modelling) is a separate, partly AI-assisted, synthetic reconstruction. It verifies equations and conservation, **not** employer-measured predictive accuracy.
- **Fractional oscillator:** An academic BSc mathematics thesis investigating noninteger Caputo derivatives, Mittag-Leffler solutions and numerical approximations. The [reusable package](https://github.com/zorromir/fractional-harmonic-oscillator) is a later code remake with original thesis scripts archived.
- **Empirical asset pricing:** The original study was a **five-person** MSc group project. This repo is an independently written public-data reproduction of selected estimates; the notebook-like original source, individual student information and group report are not published.

## Technical questions and expected reasoning

### 1. Why use HAC standard errors instead of ordinary OLS standard errors?

OLS minimizes residual sum of squares and point estimates can remain consistent with suitable orthogonality and rank assumptions. Conventional OLS covariance assumes restrictions on conditional errors such as homoskedasticity and no serial correlation. Under dependent/heteroskedastic errors, the long-run covariance of the score depends on autocovariances. Newey–West estimates that long-run covariance by adding lagged score products with Bartlett weights. Its truncation lag is a **sensitivity choice** rather than a universally correct value.

### 2. Why does improved adjusted R² not imply smaller pricing errors?

R² is a measure of time-series variation explained; pricing error is the factor regression intercept. Under matched samples, the OLS intercept obeys `alpha_hat = mean(y) - beta_hat' mean(f)`. Adding factors can increase explained variation yet shift the intercept away from zero if factor sample means/exposures interact differently. Statistical significance additionally depends on the HAC standard error.

### 3. Why use Holm across five industry tests?

For m hypotheses ordered by increasing p-value `p_(1),...,p_(m)`, Holm sequentially compares `p_(i)` against `alpha/(m-i+1)`. The family-wise Type I error rate is controlled under arbitrary dependence if underlying tests have valid p-values. The rule applies to a **specified family** (here five industry tests within one model); it does not adjust every statistic from all research stages automatically.

### 4. What is the economic interpretation of alpha?

Alpha is a sample conditional-mean intercept relative to chosen factors and dates. It is neither automatically a market anomaly nor a portfolio you can trade. Positive monthly momentum-factor alpha is **not** a realized after-cost P&L. The French momentum factor is already a long–short return, so subtracting the risk-free rate again is incorrect.

### 5. What does a Hansen J non-rejection imply?

For six moment conditions and two identified parameters, `J = T * gbar' W gbar` has an asymptotic chi-squared reference with four degrees of freedom under appropriate regularity and correct specification. Non-rejection means evidence is insufficient to reject **these selected moments**; it does not establish that the CAPM SDF is correct, especially when the test assets have similar factor exposures.

### 6. What is two-step GMM?

Choose parameters minimizing the quadratic sample-moment distance under an initial weighting matrix (identity here). Estimate a Bartlett HAC covariance of the moment series at step one, invert/pseudoinvert it, then estimate again under this weighting matrix. The moment-covariance bandwidth and centering conventions can affect finite-sample results. Make sure the parameters are identified, the matrix is well conditioned and the moments correspond to the intended assets.

### 7. How would you check robustness of month-of-year effects?

Predefine the calendar dummy specification and the five-industry testing family. Compare distinct equal-length subsamples rather than cherry-picking the most significant period. Vary reasonable HAC bandwidths, inspect effect sizes, account for multiple testing and avoid inferring tradable strategies solely from calendar tests.

### 8. Why is a higher in-sample adjusted R² not an out-of-sample forecast?

The original CAPM/FF5 regressions use **contemporaneously realized factor returns** to explain the same month's industry returns. Those factor realizations are not known beforehand. True one-step-ahead evaluation must use only information dated t−1 or earlier, train on earlier observations and compare against a simple feasible benchmark. See the lagged-factor expanding-window diagnostic; it is **not** a trading strategy.

### 9. How do you avoid look-ahead leakage?

Build `X_{t-1}` to predict `y_t`; fit on target months strictly earlier than t. Recompute every historical-mean benchmark using only past returns. A test deliberately changes a future return and a same-month predictor and verifies that predictions up to that month are unchanged.

### 10. How do you distinguish Monte Carlo from Sobol sensitivity indices?

Monte Carlo uses randomized input draws to propagate uncertainty; a scrambled Sobol sequence is a quasi-Monte Carlo design to cover the assumed input domain. Neither is, by itself, an estimate of **Sobol variance-based sensitivity indices**. The industrial public example uses QMC scenarios, not experimentally fitted input distributions.

### 11. What makes a fractional derivative different from an ordinary derivative?

For Caputo order 1 < alpha < 2, the derivative integrates earlier acceleration against a power-law kernel proportional to `(t-s)^(1-alpha)`. The evolution is nonlocal, so position and velocity by themselves need not form a complete Markovian state. For the linear oscillator, Mittag-Leffler functions generalize the cosine/sine solution; the alpha=2 limit recovers classical motion.

### 12. What would you do before claiming investment relevance?

Specify the economic hypothesis and information set, use true ex-ante features and a walk-forward evaluation with an untouched test period. Study multiple-testing/data-snooping, transaction costs, turnover, capacity, stability across samples and whether performance survives a simple benchmark. A negative OOS R² is not a reason to conceal the model; it is evidence of limitations.

## What is still open

The public study does not contain a live trading strategy, a complete reproduction of the original group report, or validated real-world pipeline accuracy. The GMM `c=mu/Var(f)` diagnostic treats sample variance as fixed and is **not the exact original restriction test**. A recruiting interviewer may reasonably ask for further derivations, a complete live coding run or a comparison with independently verified measurements.
