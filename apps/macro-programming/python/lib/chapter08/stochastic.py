"""確率過程: ホワイト・ノイズと、1 階自己回帰 AR(1)。

ホワイト・ノイズ ε(t) は、平均 0、分散 σ²、ほかの期とは無相関。
AR(1) は、x(t) = ρ·x(t−1) + ε(t)。|ρ| < 1 なら定常で、分散は σ² ÷ (1 − ρ²)、
ラグ k の自己相関は ρ^k。ショックの影響は、毎期 ρ 倍になって、消えていく。
"""

import math
from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from lib.chapter04.difference import linear_path


def _check_sigma(sigma: float) -> None:
    if sigma < 0:
        raise ValueError("標準偏差は 0 以上でなければならない")


def _check_stationary(rho: float) -> None:
    if abs(rho) >= 1:
        raise ValueError("rho の絶対値が 1 以上なので、定常ではない")


def white_noise(n: int, sigma: float, rng: np.random.Generator) -> NDArray[np.float64]:
    """平均 0、標準偏差 sigma の、独立な正規乱数 n 個。乱数の生成器を、引数で渡す。"""
    if n < 1:
        raise ValueError("系列の長さは 1 以上でなければならない")
    _check_sigma(sigma)
    return rng.normal(0.0, sigma, n)


def ar1_series(
    rho: float, sigma: float, n: int, rng: np.random.Generator, burn_in: int = 200
) -> NDArray[np.float64]:
    """AR(1) x(t) = ρ·x(t−1) + ε(t) の系列を、長さ n で作る。

    初期値の影響を消すために、最初の burn_in 個は捨てる。
    """
    _check_stationary(rho)
    shocks = white_noise(n + burn_in, sigma, rng)
    x = np.zeros(n + burn_in)
    for t in range(1, n + burn_in):
        x[t] = rho * x[t - 1] + shocks[t]
    return x[burn_in:]


def sample_autocovariance(x: Sequence[float] | NDArray[np.float64], lag: int) -> float:
    """標本の自己共分散 = Σ (x(t) − 平均)(x(t−lag) − 平均) ÷ n。"""
    values = np.asarray(x, dtype=float)
    n = len(values)
    if lag < 0 or lag >= n:
        raise ValueError("ラグは 0 以上で、系列の長さより短くなければならない")
    centered = values - values.mean()
    return float((centered[lag:] * centered[: n - lag]).sum() / n)


def sample_autocorrelation(x: Sequence[float] | NDArray[np.float64], lag: int) -> float:
    """標本の自己相関 = ラグ lag の自己共分散 ÷ 分散（ラグ 0 の自己共分散）。"""
    variance = sample_autocovariance(x, 0)
    if variance == 0:
        raise ValueError("系列に変動がないので、自己相関は求められない")
    return sample_autocovariance(x, lag) / variance


def autocorrelation_function(
    x: Sequence[float] | NDArray[np.float64], max_lag: int
) -> NDArray[np.float64]:
    """ラグ 0 から max_lag までの自己相関を並べる（ラグ 0 は 1）。"""
    return np.array([sample_autocorrelation(x, lag) for lag in range(max_lag + 1)])


def ar1_variance(rho: float, sigma: float) -> float:
    """AR(1) の分散の理論値 σ² ÷ (1 − ρ²)。"""
    _check_stationary(rho)
    return sigma**2 / (1 - rho**2)


def ar1_autocorrelation(rho: float, lag: int) -> float:
    """AR(1) のラグ k の自己相関の理論値 ρ^k。"""
    return float(rho**lag)


def shock_half_life(rho: float) -> float:
    """ショックの影響が半分になるまでの期間 = ln 0.5 ÷ ln|ρ|。"""
    if not 0 < abs(rho) < 1:
        raise ValueError("rho の絶対値は 0 より大きく 1 より小さくなければならない")
    return math.log(0.5) / math.log(abs(rho))


def ar1_impulse_response(
    rho: float, periods: int, shock: float = 1.0
) -> NDArray[np.float64]:
    """1 回のショックの影響の推移 ρ^t·shock。第 4 章の差分方程式（a = ρ、b = 0）。"""
    return np.array(linear_path(rho, 0, shock, periods))
