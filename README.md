# An analysis of stock returns across industries

Empirical Finance group project · Tilburg University · September 2026

[Read the paper (PDF)](docs/Empirical_finance.pdf)

We studied five US industry portfolios from the Kenneth French Data Library: Oil, Banks, Textiles, Toys and Retail. We looked at calendar effects, the CAPM, the Fama–French five-factor model and a CAPM stochastic discount factor.

## Main results

- Monthly return patterns appear in all five industries, but they are not stable across the full sample. Only Textiles shows significant calendar effects in all three subperiods.
- None of the five CAPM industry alphas is significant in the paper. FF5 explains more return variation, but Banks, Textiles and Toys have significant negative alphas.
- Neither model explains the momentum factor well.
- The CAPM SDF is not rejected for these five industries (Hansen J = 4.777, p = 0.311). The industries have similar market exposures, so this is a limited test of the model.

The full results, equations and discussion are in the [paper](docs/Empirical_finance.pdf).

## Python code

The code in this repository is a **separate implementation** of selected parts of our group study using publicly available data. It covers month-of-year tests, CAPM and FF5 regressions, momentum-factor regressions and two-step GMM. Some choices differ from the submitted paper. See [methods](docs/METHODS.md) and [the public-data results](docs/RESULTS_2026-11-01.md).

Run with Python 3.10 or newer:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m empirical_finance.cli
```

For additional checks, run `python -m empirical_finance.cli --robustness`. This includes subsample tests, bandwidth comparisons and a simple lagged-factor forecast. Those results are described [here](docs/ROBUSTNESS_RESULTS_2026-11-01.md).

The code downloads Kenneth French's public CSV files when run. Data and generated output files are not stored in the repository.

**Note:** The paper was written by five students. This repository's Python package is a later public implementation, not the original group code. It does not reproduce every table or figure in the paper.
