"""制限従属変数モデル: トービット（打ち切り）と切断回帰（最尤法）。"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from scipy import optimize, stats

from lib.chapter03.multiple import fit_ols


@dataclass(frozen=True)
class LimitedFit:
    """トービット・切断回帰の推定結果。係数の最後の `sigma` は、誤差の標準偏差。"""

    coefficients: pd.Series
    standard_errors: pd.Series
    log_likelihood: float
    n_obs: int


def tobit_log_likelihood(
    params: NDArray[np.float64],
    y: NDArray[np.float64],
    design: NDArray[np.float64],
    left: float,
) -> float:
    """トービット（下限 left で打ち切り）の対数尤度。params = (β, ln σ)。

    打ち切られた観測値（y = left）: ln Φ((left − x′β) ÷ σ)
    それ以外: ln φ((y − x′β) ÷ σ) − ln σ
    """
    beta, sigma = params[:-1], np.exp(params[-1])
    xb = design @ beta
    censored = y <= left
    uncensored = ~censored
    return float(
        np.sum(stats.norm.logcdf((left - xb[censored]) / sigma))
        + np.sum(stats.norm.logpdf((y[uncensored] - xb[uncensored]) / sigma))
        - uncensored.sum() * params[-1]
    )


def truncreg_log_likelihood(
    params: NDArray[np.float64],
    y: NDArray[np.float64],
    design: NDArray[np.float64],
    left: float,
) -> float:
    """切断回帰（y > left の観測値だけが標本にある）の対数尤度。params = (β, ln σ)。

    ln φ((y − x′β) ÷ σ) − ln σ − ln (1 − Φ((left − x′β) ÷ σ))
    """
    beta, sigma = params[:-1], np.exp(params[-1])
    xb = design @ beta
    return float(
        np.sum(stats.norm.logpdf((y - xb) / sigma))
        - len(y) * params[-1]
        - np.sum(stats.norm.logsf((left - xb) / sigma))
    )


def tobit_gradient(
    params: NDArray[np.float64],
    y: NDArray[np.float64],
    design: NDArray[np.float64],
    left: float,
) -> NDArray[np.float64]:
    """トービットの対数尤度の勾配（β と ln σ についての、1 階微分）。

    打ち切られた観測値は、逆ミルズ比 λ = φ(c) ÷ Φ(c)（c = (left − x′β) ÷ σ）を使う。
    """
    beta, sigma = params[:-1], np.exp(params[-1])
    xb = design @ beta
    censored = y <= left
    z = (y - xb) / sigma
    c = (left - xb) / sigma
    mills = np.exp(stats.norm.logpdf(c) - stats.norm.logcdf(c))
    weight = np.where(censored, -mills / sigma, z / sigma)
    d_log_sigma = np.where(censored, -mills * c, z**2 - 1)
    return np.append(design.T @ weight, d_log_sigma.sum())


def truncreg_gradient(
    params: NDArray[np.float64],
    y: NDArray[np.float64],
    design: NDArray[np.float64],
    left: float,
) -> NDArray[np.float64]:
    """切断回帰の対数尤度の勾配。m = φ(a) ÷ (1 − Φ(a))、a = (left − x′β) ÷ σ。"""
    beta, sigma = params[:-1], np.exp(params[-1])
    xb = design @ beta
    z = (y - xb) / sigma
    a = (left - xb) / sigma
    hazard = np.exp(stats.norm.logpdf(a) - stats.norm.logsf(a))
    weight = (z - hazard) / sigma
    d_log_sigma = z**2 - 1 - hazard * a
    return np.append(design.T @ weight, d_log_sigma.sum())


def hessian_from_gradient(
    gradient: Callable[[NDArray[np.float64]], NDArray[np.float64]],
    point: NDArray[np.float64],
) -> NDArray[np.float64]:
    """勾配の関数を、中心差分で微分して、2 階微分の行列（ヘッセ行列）を求める。

    刻み幅は、各パラメータの大きさに比例させる。結果は、対称な行列にそろえる。
    """
    n = len(point)
    hessian = np.zeros((n, n))
    for j in range(n):
        step = 1e-5 * max(1.0, abs(float(point[j])))
        e = np.eye(n)[j] * step
        hessian[:, j] = (gradient(point + e) - gradient(point - e)) / (2 * step)
    return (hessian + hessian.T) / 2


def _fit(
    log_likelihood: Callable[
        [NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], float], float
    ],
    gradient: Callable[
        [NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], float],
        NDArray[np.float64],
    ],
    y: ArrayLike,
    x: ArrayLike,
    left: float,
) -> LimitedFit:
    """対数尤度を最大化する（初期値は OLS）。標準誤差は、ヘッセ行列から求める。"""
    target = np.asarray(y, dtype=float)
    ols = fit_ols(target, x)
    columns = np.asarray(x, dtype=float)
    design = np.column_stack([np.ones(len(target)), columns.reshape(len(target), -1)])
    names = [*ols.coefficients.index, "sigma"]
    sigma0 = np.sqrt(ols.residuals @ ols.residuals / len(target))
    start = np.append(ols.coefficients.to_numpy(), np.log(sigma0))

    n = len(target)

    def negative(params: NDArray[np.float64]) -> float:
        return -log_likelihood(params, target, design, left)

    # 1 観測値あたりの対数尤度を最大化する（勾配の尺度を、nによらず、そろえる）
    result = optimize.minimize(
        lambda params: negative(params) / n,
        start,
        jac=lambda params: -gradient(params, target, design, left) / n,
        method="BFGS",
        options={"gtol": 1e-9},
    )
    if not result.success and np.max(np.abs(result.jac)) > 1e-6:
        raise ValueError("最尤法が収束しない")
    hessian = hessian_from_gradient(
        lambda params: gradient(params, target, design, left), result.x
    )
    covariance = np.linalg.inv(-hessian)
    errors = np.sqrt(np.diag(covariance))
    sigma = float(np.exp(result.x[-1]))
    values = np.append(result.x[:-1], sigma)
    errors = np.append(errors[:-1], sigma * errors[-1])  # デルタ法: σ = exp(ln σ)
    return LimitedFit(
        coefficients=pd.Series(values, index=names),
        standard_errors=pd.Series(errors, index=names),
        log_likelihood=float(-result.fun * n),
        n_obs=len(target),
    )


def fit_tobit(y: ArrayLike, x: ArrayLike, left: float = 0.0) -> LimitedFit:
    """トービットの最尤推定（下限 left で打ち切られた y）。"""
    return _fit(tobit_log_likelihood, tobit_gradient, y, x, left)


def fit_truncreg(y: ArrayLike, x: ArrayLike, left: float = 0.0) -> LimitedFit:
    """切断回帰の最尤推定（y > left の観測値だけが標本にある）。"""
    return _fit(truncreg_log_likelihood, truncreg_gradient, y, x, left)


def tobit_expected_value(
    fit: LimitedFit, x: ArrayLike, left: float = 0.0
) -> NDArray[np.float64]:
    """打ち切られた y の期待値 E[y | x] = left + (x′β − left)·Φ(z) + σ·φ(z)。

    z = (x′β − left) ÷ σ。
    """
    columns = np.asarray(x, dtype=float)
    xb = fit.coefficients.iloc[0] + columns.reshape(len(columns), -1) @ (
        fit.coefficients.iloc[1:-1].to_numpy()
    )
    sigma = fit.coefficients["sigma"]
    z = (xb - left) / sigma
    result: NDArray[np.float64] = (
        left + (xb - left) * stats.norm.cdf(z) + sigma * stats.norm.pdf(z)
    )
    return result


def tobit_marginal_effects(
    fit: LimitedFit, x: ArrayLike, left: float = 0.0
) -> pd.Series:
    """E[y | x] への、平均限界効果 = Φ(z) の平均 × 係数。"""
    columns = np.asarray(x, dtype=float)
    beta = fit.coefficients.iloc[1:-1]
    xb = fit.coefficients.iloc[0] + columns.reshape(len(columns), -1) @ beta.to_numpy()
    scale = float(np.mean(stats.norm.cdf((xb - left) / fit.coefficients["sigma"])))
    return scale * beta


def draw_latent_sample(
    n: int, rng: np.random.Generator
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """潜在変数 y* = 1 + 2x + u（x は標準正規、u は標準偏差 2 の正規分布）の標本。"""
    x = rng.standard_normal(n)
    return x, 1 + 2 * x + 2 * rng.standard_normal(n)


def censor(y_latent: NDArray[np.float64], left: float = 0.0) -> NDArray[np.float64]:
    """打ち切り: left を下回る値は、left として観測される（観測値の数は変わらない）。"""
    result: NDArray[np.float64] = np.maximum(y_latent, left)
    return result


def truncate(
    x: NDArray[np.float64], y_latent: NDArray[np.float64], left: float = 0.0
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """切断: left 以下の観測値は、標本から消える（観測値の数が減る）。"""
    kept = y_latent > left
    return x[kept], y_latent[kept]
