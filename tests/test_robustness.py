import numpy as np
import pandas as pd
import pytest

from empirical_finance.data import INDUSTRIES
from empirical_finance.robustness import (
    calendar_subperiods, alpha_bandwidth_sensitivity,
    sdf_bandwidth_sensitivity, lagged_walk_forward, oos_summary,
    approximate_sdf_slope_restriction,
)


def synthetic_sample(n=300):
    rng = np.random.default_rng(1234)
    months = pd.period_range("1990-01", periods=n, freq="M")
    market = rng.normal(.007, .035, n)
    values = {
        "Mkt-RF": market, "SMB": rng.normal(0, .02, n),
        "HML": rng.normal(0, .02, n), "RMW": rng.normal(0, .02, n),
        "CMA": rng.normal(0, .02, n), "RF": np.full(n, .001),
        "Mom": rng.normal(.004, .03, n),
    }
    for k, name in enumerate(INDUSTRIES):
        values[name] = .001 + (.85 + k * .06) * market + rng.normal(0, .018, n)
    return pd.DataFrame(values, index=months)


def test_walk_forward_calendar_and_no_future_leakage():
    frame = synthetic_sample(250)
    original = lagged_walk_forward(frame, min_train=240)
    assert len(original) == 5 * 10
    assert (original.training_observations == 239).sum() == 5
    assert (original.training_last_month < original.test_month).all()
    # Perturb a future outcome and same-month factor; past forecasts stay unchanged.
    altered = frame.copy()
    target_month = frame.index[245]
    altered.loc[target_month, "Oil"] += 5.0
    altered.loc[target_month, "Mkt-RF"] += 9.0
    changed = lagged_walk_forward(altered, min_train=240)
    before = original[(original.industry == "Oil")
                      & (original.test_month <= str(target_month))]
    after = changed[(changed.industry == "Oil")
                    & (changed.test_month <= str(target_month))]
    assert np.allclose(before.prediction_lagged_ff5, after.prediction_lagged_ff5)
    assert np.allclose(before.prediction_historical_mean, after.prediction_historical_mean)
    assert np.allclose(before.training_observations, after.training_observations)
    assert np.isfinite(oos_summary(original).oos_r2_vs_historical_mean).all()


def test_walk_forward_rejects_gaps():
    frame = synthetic_sample().drop(synthetic_sample().index[100])
    with pytest.raises(ValueError, match="Missing calendar months"):
        lagged_walk_forward(frame)


def test_subperiod_calendar_windows():
    rng = np.random.default_rng(7)
    idx = pd.period_range("1927-01", "2025-12", freq="M")
    frame = pd.DataFrame({name: rng.normal(size=len(idx)) / 100
                          for name in INDUSTRIES}, index=idx)
    result = calendar_subperiods(frame, lags=6)
    assert len(result) == 15
    assert (result.nobs == 396).all()
    assert set(result.sample_start) == {"1927-01", "1960-01", "1993-01"}
    assert result.joint_p_holm.between(0, 1).all()


def test_hac_and_gmm_sensitivity_outputs():
    sample = synthetic_sample()
    alpha = alpha_bandwidth_sensitivity(sample, lags=(6, 12))
    assert len(alpha) == 20
    assert set(alpha.hac_lags) == {6, 12}
    sdf = sdf_bandwidth_sensitivity(sample, lags=(0, 6), center_options=(False, True))
    assert len(sdf) == 4
    assert sdf.j_p_value.between(0, 1).all()
    restriction = approximate_sdf_slope_restriction(sample)
    assert 0 <= restriction["conditional_p_value"] <= 1
