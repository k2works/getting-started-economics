"""残差診断: 標準化残差・てこ比・クックの距離・Q-Q プロット。"""

import math

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import stats

from lib.chapter01.statistics import standardize
from lib.chapter03.multiple import OlsResult


def _sigma_hat(result: OlsResult) -> float:
    """誤差項の標準偏差の推定値 σ̂ = √(残差平方和 ÷ (n − k))。"""
    return math.sqrt(float(result.residuals @ result.residuals) / result.df_resid)


def standardized_residuals(result: OlsResult) -> NDArray[np.float64]:
    """標準化残差 e ÷ σ̂。"""
    return result.residuals / _sigma_hat(result)


def studentized_residuals(
    result: OlsResult, leverage: NDArray[np.float64]
) -> NDArray[np.float64]:
    """スチューデント化残差 e ÷ (σ̂ · √(1 − てこ比))。"""
    if np.any(leverage >= 1):
        raise ValueError("てこ比が 1 の観測値があり、その観測値の残差は計算できない")
    return result.residuals / (_sigma_hat(result) * np.sqrt(1 - leverage))


def cooks_distance(
    result: OlsResult, leverage: NDArray[np.float64]
) -> NDArray[np.float64]:
    """クックの距離 = r² ÷ k · h ÷ (1 − h)。観測値を除くと、推定値がどれだけ動くか。"""
    k = len(result.coefficients)
    r = studentized_residuals(result, leverage)
    distance: NDArray[np.float64] = r**2 / k * leverage / (1 - leverage)
    return distance


def qq_points(values: ArrayLike) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Q-Q プロットの点: 標準正規分布の分位点と、標準化して小さい順に並べた値。"""
    ordered = np.sort(standardize(np.asarray(values, dtype=float)))
    n = len(ordered)
    probabilities = (np.arange(1, n + 1) - 0.5) / n
    return stats.norm.ppf(probabilities), ordered


def match_moments(
    x_shape: ArrayLike,
    y_shape: ArrayLike,
    means: tuple[float, float],
    sds: tuple[float, float],
    correlation: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """形の違う 2 つの数列を、平均・標準偏差・相関が指定どおりになるように直す。"""
    zx = standardize(np.asarray(x_shape, dtype=float))
    zy = standardize(np.asarray(y_shape, dtype=float))
    n = len(zx)
    perpendicular = zy - (zy @ zx / (n - 1)) * zx
    sd = math.sqrt(perpendicular @ perpendicular / (n - 1))
    if sd < 1e-12:
        raise ValueError("y の形が x に比例しているので、相関を指定できない")
    y = correlation * zx + math.sqrt(1 - correlation**2) * perpendicular / sd
    return means[0] + sds[0] * zx, means[1] + sds[1] * y


def same_summary_datasets() -> dict[
    str, tuple[NDArray[np.float64], NDArray[np.float64]]
]:
    """平均・標準偏差・相関・回帰直線が同じで、形が違う 4 組のデータ（11 個ずつ）。"""
    x = np.arange(11.0)
    shapes: dict[str, tuple[ArrayLike, ArrayLike]] = {
        "linear": (x, [1.2, -0.8, 2.0, -1.5, 0.3, 0.9, -2.2, 1.7, -0.4, 0.1, -1.1]),
        "curved": (x, -((x - 5) ** 2)),
        "outlier": (x, [0.0] * 10 + [10.0]),
        "clustered": (
            [0.0] * 9 + [1.0] * 2,
            [0.3, -1.0, 1.1, 0.2, -0.5, 0.8, -0.2, 0.6, -0.9, 2.5, 1.9],
        ),
    }
    return {
        name: match_moments(xs, ys, (9, 7.5), (3.3, 2.0), 0.8)
        for name, (xs, ys) in shapes.items()
    }
