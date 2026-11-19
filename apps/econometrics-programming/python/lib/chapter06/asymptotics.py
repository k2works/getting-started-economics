"""大標本特性: 一致性、誤差項が正規でないときの t 値、正規性の検定、LM 検定。"""

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from scipy import stats

from lib.chapter02.simple import draw_sample
from lib.chapter03.multiple import fit_ols
from lib.chapter05.inference import TestResult


def skewness(x: ArrayLike) -> float:
    """歪度 = 3 次の中心モーメント ÷ （2 次の中心モーメント）^(3/2)。"""
    values = np.asarray(x, dtype=float)
    d = values - values.mean()
    return float(np.mean(d**3) / np.mean(d**2) ** 1.5)


def kurtosis(x: ArrayLike) -> float:
    """尖度 = 4 次の中心モーメント ÷ （2 次の中心モーメント）²。正規分布は 3。"""
    values = np.asarray(x, dtype=float)
    d = values - values.mean()
    return float(np.mean(d**4) / np.mean(d**2) ** 2)


def jarque_bera(x: ArrayLike) -> TestResult:
    """Jarque-Bera 検定。JB = n ÷ 6 · (歪度² + (尖度 − 3)² ÷ 4) は、χ²(2) に従う。"""
    n = len(np.asarray(x))
    statistic = n / 6 * (skewness(x) ** 2 + (kurtosis(x) - 3) ** 2 / 4)
    return TestResult(float(statistic), float(stats.chi2.sf(statistic, 2)))


def lm_test(y: ArrayLike, restricted: pd.DataFrame, extra: pd.DataFrame) -> TestResult:
    """LM 検定: extra の係数が 0 という仮説。LM = n · R²（補助回帰）は、χ²(q) に従う。

    補助回帰は、制約付き回帰の残差を、すべての説明変数で回帰したもの。
    """
    residuals = fit_ols(y, restricted).residuals
    full = pd.concat([restricted, extra], axis=1)
    auxiliary = fit_ols(residuals, full)
    statistic = len(residuals) * auxiliary.r_squared
    q = extra.shape[1]
    return TestResult(float(statistic), float(stats.chi2.sf(statistic, q)))


def draw_skewed_sample(
    n: int, intercept: float, slope: float, sigma: float, rng: np.random.Generator
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """誤差項が正規分布でない（平均 0 に直した指数分布。歪度 2）標本を作る。"""
    x = rng.standard_normal(n)
    u = sigma * (rng.exponential(1.0, n) - 1.0)
    return x, intercept + slope * x + u


def _draw(
    n: int, skewed: bool, rng: np.random.Generator
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    draw = draw_skewed_sample if skewed else draw_sample
    return draw(n, 1.0, 0.5, 1.0, rng)


def consistency_experiment(
    sample_sizes: list[int], repetitions: int, rng: np.random.Generator
) -> dict[int, NDArray[np.float64]]:
    """標本の大きさごとに、傾きの推定値を繰り返し求める（真の傾きは 0.5）。"""
    estimates = {}
    for n in sample_sizes:
        slopes = []
        for _ in range(repetitions):
            x, y = _draw(n, False, rng)
            slopes.append(fit_ols(y, x).coefficients["x1"])
        estimates[n] = np.array(slopes)
    return estimates


def t_value_distribution(
    n: int, repetitions: int, skewed: bool, rng: np.random.Generator
) -> NDArray[np.float64]:
    """真の傾きを帰無仮説にした t 値 (傾き − 0.5) ÷ 標準誤差を、繰り返し求める。"""
    values = []
    for _ in range(repetitions):
        x, y = _draw(n, skewed, rng)
        result = fit_ols(y, x)
        values.append((result.coefficients["x1"] - 0.5) / result.standard_errors["x1"])
    return np.array(values)


def jarque_bera_rejection_rate(
    n: int, repetitions: int, skewed: bool, rng: np.random.Generator
) -> float:
    """残差の Jarque-Bera 検定を、有意水準 5% で棄却する割合。"""
    rejected = 0
    for _ in range(repetitions):
        x, y = _draw(n, skewed, rng)
        rejected += jarque_bera(fit_ols(y, x).residuals).p_value < 0.05
    return rejected / repetitions
