"""Sensitivity analyses and a strictly lagged, walk-forward forecasting diagnostic.

These are checks on historical research findings, not executable trading signals.
"""
from __future__ import annotations

from dataclasses import asdict
import numpy as np
import pandas as pd
from scipy.stats import chi2
from statsmodels.stats.multitest import multipletests

from .analysis import CAPM, FF5, calendar_wald, factor_regressions
from .data import INDUSTRIES
from .gmm import estimate_sdf


def calendar_subperiods(sample: pd.DataFrame, *, lags: int = 24) -> pd.DataFrame:
    """Three non-overlapping 396-month calendar subsamples from the report."""
    windows = (("1927-01", "1959-12"), ("1960-01", "1992-12"),
               ("1993-01", "2025-12"))
    pieces = []
    for start, end in windows:
        expected = pd.period_range(start, end, freq="M")
        block = sample.reindex(expected)
        if len(block) != 396 or block.isna().any().any():
            raise ValueError(f"Incomplete calendar subsample {start}..{end}")
        tests = calendar_wald(block, lags=lags)
        tests.insert(0, "sample_start", start)
        tests.insert(1, "sample_end", end)
        pieces.append(tests)
    return pd.concat(pieces, ignore_index=True)


def alpha_bandwidth_sensitivity(sample: pd.DataFrame, *, lags=(6, 12, 24, 36)
                                ) -> pd.DataFrame:
    """Reestimate FF5/CAPM intercept tests for several HAC lag conventions."""
    if not lags or any(lag < 0 or lag >= len(sample) for lag in lags):
        raise ValueError("HAC lag specifications must be within the sample")
    pieces = []
    for lag in lags:
        results, momentum = factor_regressions(sample, lags=int(lag))
        results.insert(0, "hac_lags", int(lag))
        # Momentum is not an industry alpha; keep the two test families separate.
        pieces.append(results)
    return pd.concat(pieces, ignore_index=True)


def sdf_bandwidth_sensitivity(sample: pd.DataFrame, *, lags=(0, 6, 12),
                              center_options=(False, True)) -> pd.DataFrame:
    """Change Bartlett bandwidth and moment-centering independently."""
    rows = []
    for centered in center_options:
        for lag in lags:
            if lag < 0 or lag >= len(sample):
                raise ValueError("SDF lag outside valid sample")
            result = estimate_sdf(sample, lags=int(lag), centered=centered)
            rows.append({"nw_lags": int(lag), "centered_moments": bool(centered),
                         **asdict(result)})
    return pd.DataFrame(rows)


def lagged_walk_forward(sample: pd.DataFrame, *, min_train: int = 240) -> pd.DataFrame:
    """One-month-ahead excess-return diagnostic, refitted each month.

    Forecast y_t using factor values at t-1 only; train on (f_{s-1}, y_s)
    for s < t. Baseline is the historical mean of y through t-1. No
    current-month factor return or future sample observations enter any
    prediction. This deliberately does NOT forecast with contemporaneous FF5.
    """
    if not (isinstance(sample.index, pd.PeriodIndex)
            and sample.index.freqstr == "M" and sample.index.is_monotonic_increasing
            and sample.index.is_unique):
        raise ValueError("Expected unique, sorted monthly PeriodIndex")
    if min_train < 40 or len(sample) <= min_train:
        raise ValueError("Insufficient expanding training history")
    required = [*INDUSTRIES, "RF", *FF5]
    if any(col not in sample.columns for col in required):
        raise ValueError("Missing forecasting inputs")
    if not np.isfinite(sample[required].to_numpy()).all():
        raise ValueError("Forecasting sample contains non-finite values")
    if not sample.index.equals(pd.period_range(sample.index[0], sample.index[-1], freq="M")):
        raise ValueError("Missing calendar months")

    # Lagged predictors are public realized factor observations as of t-1.
    # The first training pair is t=1; no X_0 is invented.
    lagged = sample[FF5].shift(1).to_numpy(dtype=float)
    rows = []
    for industry in INDUSTRIES:
        excess = (sample[industry] - sample["RF"]).to_numpy(dtype=float)
        for t in range(min_train, len(sample)):
            x_train = lagged[1:t]
            y_train = excess[1:t]
            x = np.column_stack([np.ones(t - 1), x_train])
            x_next = np.r_[1.0, lagged[t]]
            beta = np.linalg.lstsq(x, y_train, rcond=None)[0]
            rows.append({
                "industry": industry, "test_month": str(sample.index[t]),
                "training_last_month": str(sample.index[t-1]),
                "training_observations": t - 1,
                "actual": float(excess[t]),
                "prediction_lagged_ff5": float(x_next @ beta),
                "prediction_historical_mean": float(excess[:t].mean()),
            })
    return pd.DataFrame(rows)


def oos_summary(forecasts: pd.DataFrame) -> pd.DataFrame:
    """OOS R² relative to sequential expanding historical-mean forecasts."""
    rows = []
    for name, g in forecasts.groupby("industry", sort=False):
        if not len(g):
            raise ValueError("Empty forecast group")
        model_sse = np.square(g["actual"] - g["prediction_lagged_ff5"]).sum()
        bench_sse = np.square(g["actual"] - g["prediction_historical_mean"]).sum()
        if bench_sse <= 0:
            raise ValueError("Historical benchmark has zero squared error")
        rows.append({
            "industry": name, "n_forecasts": int(len(g)),
            "first_test_month": g["test_month"].iloc[0],
            "last_test_month": g["test_month"].iloc[-1],
            "oos_r2_vs_historical_mean": float(1 - model_sse / bench_sse),
            "rmse_lagged_ff5": float(np.sqrt(model_sse / len(g))),
            "rmse_historical_mean": float(np.sqrt(bench_sse / len(g))),
        })
    return pd.DataFrame(rows)


def approximate_sdf_slope_restriction(sample: pd.DataFrame, *, lags: int = 6
                                       ) -> dict:
    """Approximate conditional Wald check of c=mu/Var(f).

    Treats sample market variance as fixed in the delta method; unlike a
    joint moment-system restriction test it omits variance-estimation
    uncertainty. Interpret as a diagnostic, not the exact archived test.
    """
    sdf = estimate_sdf(sample, lags=lags)
    market = sample["Mkt-RF"].to_numpy(dtype=float)
    variance = float(np.var(market, ddof=0))
    if variance <= 0:
        raise ValueError("Market variance is zero")
    gap = float(sdf.c - sdf.mu / variance)
    gradient = np.array([-1.0 / variance, 1.0])
    cov = np.array([[sdf.se_mu**2, sdf.cov_mu_c],
                    [sdf.cov_mu_c, sdf.se_c**2]])
    v = float(gradient @ cov @ gradient)
    if v <= 0:
        raise ValueError("Degenerate restriction variance")
    chi2_stat = gap**2 / v
    return {"slope_difference": gap, "conditional_wald_chi2": chi2_stat,
            "conditional_p_value": float(chi2.sf(chi2_stat, 1)),
            "important_limit": "Variance(f) treated as fixed; not exact original report test"}
