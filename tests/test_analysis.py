import numpy as np
import pandas as pd
import pytest

from empirical_finance.analysis import calendar_wald, factor_regressions, hac_fit
from empirical_finance.data import INDUSTRIES


def test_ols_alpha_and_hac_se():
    x = np.arange(120, dtype=float) / 120.0
    y = 0.03 + 1.4 * x + 0.002 * np.sin(4.0 * np.pi * x)
    fit = hac_fit(y, x, lags=6)
    assert fit.params[0] == pytest.approx(0.03, abs=0.002)
    assert fit.params[1] == pytest.approx(1.4, abs=0.02)
    assert fit.bse[0] > 0


def make_factor_sample():
    rng = np.random.default_rng(4)
    index = pd.period_range("2000-01", periods=180, freq="M")
    f = rng.normal(0.005, 0.04, 180)
    values = {
        "Mkt-RF": f,
        "SMB": rng.normal(0, 0.02, 180),
        "HML": rng.normal(0, 0.02, 180),
        "RMW": rng.normal(0, 0.02, 180),
        "CMA": rng.normal(0, 0.02, 180),
        "RF": np.full(180, 0.001),
        "Mom": rng.normal(0.008, 0.03, 180),
    }
    for i, industry in enumerate(INDUSTRIES):
        values[industry] = 0.001 + values["RF"] + (0.8 + i / 10) * f + rng.normal(0, .015, 180)
    return pd.DataFrame(values, index=index)


def test_factor_regressions_holm_and_momentum():
    results, momentum = factor_regressions(make_factor_sample(), lags=6)
    assert len(results) == 10
    assert len(momentum) == 2
    assert set(results["model"]) == {"CAPM", "FF5"}
    assert (results["alpha_p_holm"] + 1e-12 >= results["alpha_p_hac"]).all()
    assert (results["adj_r2"] < 1).all()


def test_calendar_joint_wald_uses_eleven_dummies():
    sample = make_factor_sample()[list(INDUSTRIES)]
    result = calendar_wald(sample, lags=6)
    assert len(result) == 5
    assert np.isfinite(result["wald_chi2"]).all()
    assert result["joint_p_holm"].between(0, 1).all()
