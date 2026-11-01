"""A normalized CAPM SDF with six moments estimated by two-step GMM.

m_t = 1 - c (f_t - mu), where f_t is the market excess return.
Five pricing moments are E[m_t (R_i-R_f)] = 0.
The sixth identifies the market mean E[f_t - mu] = 0.

Outputs are sample-dependent, and failure to reject J does not validate pricing.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares
from scipy.stats import chi2

from .data import INDUSTRIES


@dataclass(frozen=True)
class GMMResult:
    mu: float
    c: float
    j_stat: float
    j_p_value: float
    degrees_freedom: int
    observations: int
    se_mu: float
    se_c: float
    cov_mu_c: float


def moment_matrix(theta: np.ndarray, excess: np.ndarray,
                  market: np.ndarray) -> np.ndarray:
    mu, c = np.asarray(theta, dtype=float)
    discount = 1.0 - c * (market - mu)
    return np.column_stack([discount[:, None] * excess, market - mu])


def long_run_covariance(g: np.ndarray, lags: int = 6, *,
                        centered: bool = False) -> np.ndarray:
    """Bartlett/Newey–West long-run moment covariance, /T convention."""
    g = np.asarray(g, dtype=float)
    if g.ndim != 2 or len(g) <= lags or lags < 0:
        raise ValueError("Insufficient observations for HAC moment covariance")
    if centered:
        g = g - g.mean(axis=0, keepdims=True)
    n = len(g)
    covariance = (g.T @ g) / n
    for lag in range(1, lags + 1):
        gamma = (g[lag:].T @ g[:-lag]) / n
        weight = 1.0 - lag / (lags + 1.0)
        covariance += weight * (gamma + gamma.T)
    return (covariance + covariance.T) / 2.0


def _objective(theta: np.ndarray, e: np.ndarray, f: np.ndarray,
               weight: np.ndarray) -> tuple[float, np.ndarray]:
    mu, c = theta
    mbar = moment_matrix(theta, e, f).mean(axis=0)
    derivatives = np.zeros((e.shape[1] + 1, 2))
    derivatives[:-1, 0] = c * e.mean(axis=0)
    derivatives[:-1, 1] = -((f - mu)[:, None] * e).mean(axis=0)
    derivatives[-1, 0] = -1.0
    return float(mbar @ weight @ mbar), 2.0 * derivatives.T @ weight @ mbar


def two_step_gmm(excess: np.ndarray, market: np.ndarray, *, lags: int = 6,
                 centered: bool = False) -> GMMResult:
    e = np.asarray(excess, dtype=float)
    f = np.asarray(market, dtype=float)
    if e.ndim != 2 or e.shape[1] != 5 or f.shape != (len(e),):
        raise ValueError("Expected T x 5 excess-return matrix and T market returns")
    if len(f) <= max(20, lags + 2) or not (np.isfinite(e).all() and np.isfinite(f).all()):
        raise ValueError("Insufficient or non-finite GMM inputs")
    var_f = float(f.var())
    if var_f <= 1e-14:
        raise ValueError("Market excess return lacks variation")
    guess = np.array([f.mean(), f.mean() / var_f])
    identity = np.eye(e.shape[1] + 1)

    def estimate(weights: np.ndarray, init: np.ndarray) -> np.ndarray:
        # Minimize the weighted moment residual directly. A Cholesky-like
        # symmetric square root is stable even if the weighting matrix is
        # rank-deficient; a scaled least-squares solve avoids BFGS precision
        # loss when long-run moment covariances are small.
        eigenvalues, eigenvectors = np.linalg.eigh((weights + weights.T) / 2.0)
        root = (eigenvectors * np.sqrt(np.maximum(eigenvalues, 0.0))) @ eigenvectors.T

        def residual(theta: np.ndarray) -> np.ndarray:
            return root @ moment_matrix(theta, e, f).mean(axis=0)

        def jacobian(theta: np.ndarray) -> np.ndarray:
            mu, c = theta
            derivative = np.zeros((e.shape[1] + 1, 2))
            derivative[:-1, 0] = c * e.mean(axis=0)
            derivative[:-1, 1] = -((f - mu)[:, None] * e).mean(axis=0)
            derivative[-1, 0] = -1.0
            return root @ derivative

        fit = least_squares(residual, init, jac=jacobian, method="trf",
                            x_scale="jac", max_nfev=1500,
                            xtol=1e-12, ftol=1e-12, gtol=1e-12)
        if not fit.success or not np.isfinite(fit.fun).all():
            raise RuntimeError(f"GMM optimisation failed: {fit.message}")
        return np.asarray(fit.x, dtype=float)

    first = estimate(identity, guess)
    g1 = moment_matrix(first, e, f)
    covariance = long_run_covariance(g1, lags=lags, centered=centered)
    weighting = np.linalg.pinv(covariance, rcond=1e-12)
    final = estimate(weighting, first)
    moments = moment_matrix(final, e, f).mean(axis=0)
    j_stat = max(0.0, len(e) * float(moments @ weighting @ moments))
    df = e.shape[1] + 1 - 2
    mu, c = final
    derivatives = np.zeros((e.shape[1] + 1, 2))
    derivatives[:-1, 0] = c * e.mean(axis=0)
    derivatives[:-1, 1] = -((f - mu)[:, None] * e).mean(axis=0)
    derivatives[-1, 0] = -1.0
    # Conventional efficient two-step GMM covariance, treating step-one W as fixed.
    standard = np.linalg.pinv(derivatives.T @ weighting @ derivatives, rcond=1e-12) / len(e)
    se = np.sqrt(np.clip(np.diag(standard), 0.0, np.inf))
    return GMMResult(mu=float(mu), c=float(c), j_stat=j_stat,
                     j_p_value=float(chi2.sf(j_stat, df)), degrees_freedom=df,
                     observations=int(len(e)), se_mu=float(se[0]), se_c=float(se[1]),
                     cov_mu_c=float(standard[0, 1]))


def estimate_sdf(sample, *, lags: int = 6, centered: bool = False) -> GMMResult:
    f = sample["Mkt-RF"].to_numpy(dtype=float)
    excess = np.column_stack(
        [(sample[name] - sample["RF"]).to_numpy(dtype=float) for name in INDUSTRIES]
    )
    return two_step_gmm(excess, f, lags=lags, centered=centered)
