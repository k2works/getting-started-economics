"""単回帰（最小二乗法）。観測値から、直線 y = 切片 + 傾き × x を推定する。"""

from collections.abc import Sequence


def fit_line(x: Sequence[float], y: Sequence[float]) -> tuple[float, float]:
    """最小二乗法で、(切片, 傾き) を返す。傾き = Σ(x - x̄)(y - ȳ) ÷ Σ(x - x̄)²。"""
    if len(x) != len(y):
        raise ValueError("x と y の点の数が合わない")
    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    spread_x = sum((xi - mean_x) ** 2 for xi in x)
    if spread_x == 0:
        raise ValueError("x がすべて同じ値なので、傾きは求められない")
    covariance = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y, strict=True))
    slope = covariance / spread_x
    return mean_y - slope * mean_x, slope


def r_squared(x: Sequence[float], y: Sequence[float]) -> float:
    """決定係数 R² = 1 - (残差の二乗和) ÷ (y の偏差の二乗和)。"""
    intercept, slope = fit_line(x, y)
    mean_y = sum(y) / len(y)
    residual = sum(
        (yi - (intercept + slope * xi)) ** 2 for xi, yi in zip(x, y, strict=True)
    )
    total = sum((yi - mean_y) ** 2 for yi in y)
    return 1 - residual / total
