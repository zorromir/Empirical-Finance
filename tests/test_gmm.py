import numpy as np
import pytest

from empirical_finance.gmm import long_run_covariance, moment_matrix, two_step_gmm


def test_sdf_formula_and_six_moments():
    f = np.array([0.01, -0.02, 0.02])
    e = np.ones((3, 5)) * 0.01
    g = moment_matrix(np.array([0.0, 2.0]), e, f)
    assert g.shape == (3, 6)
    assert g[0, 0] == pytest.approx(0.01 * (1 - 2 * .01))
    assert np.allclose(g[:, -1], f)


def test_nw_covariance_symmetric_and_centering_option():
    rng = np.random.default_rng(2026)
    g = rng.normal(size=(90, 6)) + 0.1
    s = long_run_covariance(g, lags=6)
    sc = long_run_covariance(g, lags=6, centered=True)
    assert s.shape == (6, 6)
    assert np.allclose(s, s.T)
    assert np.isfinite(sc).all()
    assert not np.allclose(s, sc)


def test_gmm_nonnegative_j_stat_and_valid_p_value():
    rng = np.random.default_rng(18)
    f = rng.normal(.006, .045, 400)
    e = np.column_stack([0.8 * f + rng.normal(0, .03, len(f))
                         for _ in range(5)])
    result = two_step_gmm(e, f)
    assert result.observations == 400
    assert result.degrees_freedom == 4
    assert np.isfinite(result.c)
    assert np.isfinite(result.se_c)
    assert result.j_stat >= 0
    assert 0 <= result.j_p_value <= 1


def test_gmm_rejects_bad_shapes():
    with pytest.raises(ValueError):
        two_step_gmm(np.ones((10, 3)), np.ones(10))
