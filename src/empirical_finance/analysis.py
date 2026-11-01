"""CAPM/FF5 time-series regressions and calendar-month hypothesis tests."""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from .data import INDUSTRIES

HAC_LAGS = 24
FF5 = ["Mkt-RF", "SMB", "HML", "RMW", "CMA"]
CAPM = ["Mkt-RF"]


def hac_fit(y: np.ndarray, x: np.ndarray, *, lags: int = HAC_LAGS):
    """OLS coefficients with Bartlett HAC standard errors.

    Inputs must be in decimal returns. Statsmodels fits an intercept explicitly.
    """
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x[:, None]
    if not (len(y) == len(x) and np.isfinite(y).all() and np.isfinite(x).all()):
        raise ValueError("Nonmatching lengths or non-finite regression inputs")
    if len(y) <= x.shape[1] + 1:
        raise ValueError("Too few observations for regression")
    design = sm.add_constant(x, has_constant="add")
    return sm.OLS(y, design).fit(cov_type="HAC", cov_kwds={
        "maxlags": int(lags), "kernel": "bartlett", "use_correction": False
    })


def factor_regressions(sample: pd.DataFrame, lags: int = HAC_LAGS
                       ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Five industry regressions plus separately treated momentum long-short."""
    rows = []
    for model_name, predictors in [("CAPM", CAPM), ("FF5", FF5)]:
        x = sample[predictors].to_numpy(dtype=float)
        for industry in INDUSTRIES:
            y = (sample[industry] - sample["RF"]).to_numpy(dtype=float)
            fit = hac_fit(y, x, lags=lags)
            rows.append({
                "model": model_name, "industry": industry, "nobs": int(fit.nobs),
                "alpha_monthly": float(fit.params[0]),
                "alpha_t_hac": float(fit.tvalues[0]),
                "alpha_p_hac": float(fit.pvalues[0]),
                "adj_r2": float(fit.rsquared_adj),
            })
    result = pd.DataFrame(rows)
    result["alpha_p_holm"] = np.nan
    for model in ("CAPM", "FF5"):
        mask = result["model"].eq(model)
        result.loc[mask, "alpha_p_holm"] = multipletests(
            result.loc[mask, "alpha_p_hac"].to_numpy(), method="holm"
        )[1]

    # The momentum factor is already a long-short return, NOT Mom minus RF.
    momentum_rows = []
    for name, predictors in [("CAPM", CAPM), ("FF5", FF5)]:
        fit = hac_fit(sample["Mom"].to_numpy(), sample[predictors].to_numpy(), lags=lags)
        momentum_rows.append({
            "model": name, "nobs": int(fit.nobs),
            "alpha_monthly": float(fit.params[0]),
            "alpha_t_hac": float(fit.tvalues[0]),
            "alpha_p_hac": float(fit.pvalues[0]),
            "adj_r2": float(fit.rsquared_adj),
        })
    return result, pd.DataFrame(momentum_rows)


def calendar_wald(sample: pd.DataFrame, lags: int = HAC_LAGS) -> pd.DataFrame:
    """Joint HAC Wald tests of eleven monthly dummy coefficients.

    Null: all calendar-month means are equal. Uses *raw* industry returns.
    January is the omitted reference, and Holm adjusts five joint-test p-values.
    """
    months = np.asarray(sample.index.month)
    x = np.column_stack([np.ones(len(sample))]
                        + [(months == m).astype(float) for m in range(2, 13)])
    restrictions = np.column_stack([np.zeros(11), np.eye(11)])
    rows = []
    for industry in INDUSTRIES:
        fit = sm.OLS(sample[industry].to_numpy(), x).fit(
            cov_type="HAC", cov_kwds={
                "maxlags": int(lags), "kernel": "bartlett", "use_correction": False
            })
        wald = fit.wald_test(restrictions, scalar=True)
        rows.append({
            "industry": industry, "nobs": int(fit.nobs),
            "wald_chi2": float(wald.statistic),
            "joint_p_hac": float(wald.pvalue),
            "r2": float(fit.rsquared),
        })
    result = pd.DataFrame(rows)
    result["joint_p_holm"] = multipletests(
        result["joint_p_hac"].to_numpy(), method="holm"
    )[1]
    return result
