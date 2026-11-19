"""単回帰分析: 傾き = 共分散 ÷ 分散、残差、決定係数、標準誤差。"""

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from lib.chapter01.statistics import Array, sample_covariance, sample_variance


@dataclass(frozen=True)
class SimpleFit:
    """単回帰 y = intercept + slope · x の推定結果。"""

    intercept: float
    slope: float


def fit_simple(x: Array, y: Array) -> SimpleFit:
    """最小二乗法。傾き = Cov(x, y) ÷ Var(x)、切片 = ȳ − 傾き · x̄。"""
    var_x = sample_variance(x)
    if var_x == 0:
        raise ValueError("説明変数の分散が 0 なので、傾きを推定できない")
    slope = sample_covariance(x, y) / var_x
    intercept = float(np.mean(y)) - slope * float(np.mean(x))
    return SimpleFit(intercept=intercept, slope=slope)


def fitted_values(fit: SimpleFit, x: Array) -> NDArray[np.float64]:
    """当てはめ値 ŷ = 切片 + 傾き · x。"""
    return fit.intercept + fit.slope * np.asarray(x, dtype=float)


def residuals(fit: SimpleFit, x: Array, y: Array) -> NDArray[np.float64]:
    """残差 e = y − ŷ。"""
    return np.asarray(y, dtype=float) - fitted_values(fit, x)


def r_squared(fit: SimpleFit, x: Array, y: Array) -> float:
    """決定係数 R² = 1 − 残差平方和 ÷ 全平方和。"""
    rss = float(np.sum(residuals(fit, x, y) ** 2))
    tss = float(np.sum((np.asarray(y, dtype=float) - np.mean(y)) ** 2))
    return 1 - rss / tss


def slope_standard_error(fit: SimpleFit, x: Array, y: Array) -> float:
    """傾きの標準誤差 = √(σ̂² ÷ Σ(x − x̄)²)。σ̂² = 残差平方和 ÷ (n − 2)。"""
    n = len(x)
    if n <= 2:
        raise ValueError("自由度（n − 2）が 0 以下なので、標準誤差を計算できない")
    sigma2 = float(np.sum(residuals(fit, x, y) ** 2)) / (n - 2)
    sxx = sample_variance(x) * (n - 1)
    return math.sqrt(sigma2 / sxx)


def draw_sample(
    n: int, intercept: float, slope: float, sigma: float, rng: np.random.Generator
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """母集団の式 y = 切片 + 傾き · x + u から、n 個の標本を作る。

    x は標準正規分布、誤差項 u は平均 0・標準偏差 sigma の正規分布。
    """
    x = rng.standard_normal(n)
    u = sigma * rng.standard_normal(n)
    return x, intercept + slope * x + u


def sampling_distribution(
    n: int,
    repetitions: int,
    intercept: float,
    slope: float,
    sigma: float,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """標本を取り直して推定する作業を繰り返し、切片・傾き・標準誤差の表を返す。"""
    rows = []
    for _ in range(repetitions):
        x, y = draw_sample(n, intercept, slope, sigma, rng)
        fit = fit_simple(x, y)
        rows.append((fit.intercept, fit.slope, slope_standard_error(fit, x, y)))
    return pd.DataFrame(rows, columns=["intercept", "slope", "se"])
