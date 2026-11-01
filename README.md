# Empirical Asset Pricing — Public-Data Reproduction

Independent research-code companion to a **five-person MSc Empirical Finance group study** at Tilburg University (2026).

The original coursework report, co-authors' code, student data and archived numerical files are **not** included. This repository contains an independently written implementation of selected models using freely downloadable public data. A **real-data run passed on 1 November 2026** and reproduced the study's central qualitative findings and the SDF GMM J statistic to rounding. Exact numerical equivalence for every original table has **not** been established; data-vintage differences and missing subperiod/restriction tests are documented in [verified results](docs/RESULTS_2026-11-01.md).

[Research summary and previously audited findings](https://github.com/zorromir/zorromir.github.io/blob/main/projects/empirical-finance/README.md) · [Portfolio case study](https://zorromir.github.io/#projects)

## Verified run

[Public-data results, source hashes and comparison cautions](docs/RESULTS_2026-11-01.md). The full run succeeded on the 756-month factor sample, 1,188-month calendar sample and two-step GMM. GitHub Actions also runs separate, offline mathematical tests on Python 3.10 and 3.12.

## Research question

Can a factor model explain more variation in industry portfolio returns without eliminating pricing errors? How sensitive are calendar and asset-pricing results to robust inference and multiple testing? What does a CAPM SDF overidentification test actually establish?

## What this package implements

| Analysis | Public sample | Estimation |
| --- | --- | --- |
| Calendar effects | January 1927–December 2025 | 11 month indicators, HAC(24) Wald test, Holm correction |
| CAPM and FF5 | July 1963–June 2026 | Matched-sample OLS, HAC(24) alpha inference, adjusted R² |
| Momentum | July 1963–June 2026 | Long-short Mom factor on CAPM / FF5 (do not subtract RF twice) |
| CAPM SDF | July 1963–June 2026 | Two-step GMM, five pricing moments plus one market-mean moment, NW(6), Hansen J |

**Assets:** Oil, Banks, Textiles, Toys, Retail, selected from the 49 value-weighted industry portfolios. Annual and monthly tables are not mixed. No look-ahead months beyond the stated endpoints are admitted.

## Reproduce from public data

Install Python 3.10 or newer and run:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m empirical_finance.cli
```

The final command downloads the required public CSV ZIP archives from Kenneth French's Data Library into ignored `data/raw/`, reads the **monthly** sections, performs the analyses, and writes:

- `outputs/seasonality.csv`: joint month-of-year Wald tests and Holm-adjusted p-values.
- `outputs/factor_regressions.csv`: CAPM/FF5 adjusted R² and HAC/Holm alpha tests.
- `outputs/momentum.csv`: long-short momentum alpha tests.
- `outputs/manifest.json`: exact data-source URLs, SHA-256 ZIP hashes, sample windows and GMM results.

Re-run with cached data only (`--offline`) or force redownload (`--refresh`). *The first run requires internet access*. If the data provider changes filenames or availability, the code fails explicitly rather than silently using alternate data.

## Robustness and walk-forward evaluation

Use `python -m empirical_finance.cli --robustness` to add calendar subsamples, HAC bandwidth checks, SDF moment-covariance sensitivity and a lagged-factor walk-forward diagnostic. The diagnostic predicts next-month industry excess returns using *previous-month* factor values, comparing with an expanding historical-mean forecast — not a live strategy.

[Protocol and caveats](docs/ROBUSTNESS_METHODS.md) · [Technical interview guide](docs/INTERVIEW_GUIDE.md)

## Interpretation and boundaries

- All input returns and model alpha estimates use **decimals** (0.0075 = 0.75% monthly).
- Better adjusted R² does not prove better asset pricing or a trading opportunity.
- A failure to reject a Hansen J test is not confirmation that the SDF is correctly specified.
- The five industry portfolios were used for GMM, **not momentum-sorted portfolios**.
- All results are historical, in-sample and subject to source-data revisions; no trading strategy is validated.

See [Methods and limitations](docs/METHODS.md) for equations, assumptions and precise inference conventions. Tests operate on synthetic fixtures, so they verify code behaviour but **not** the numerical identity of the archived MSc results.

## Files

```text
src/empirical_finance/
  data.py       French ZIP download, monthly parsing, sample controls
  analysis.py   HAC OLS, Holm correction, monthly Wald tests
  gmm.py        Two-step normalized CAPM SDF GMM
  cli.py        Reproducible analysis command and output manifest
tests/          Offline synthetic data and numerical tests
docs/           Method definitions, scientific cautions
```

All original group study results remain attributable to the five co-authors; this independent codebase should not be presented as a solo version of that group's original report. No open-source licence has yet been selected.
