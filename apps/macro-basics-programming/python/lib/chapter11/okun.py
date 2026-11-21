"""需給ギャップとオークンの法則（自作の最小二乗法）。

オークンの法則: 失業率の変化 Δu = 切片 + 傾き × 成長率。傾きは負（成長率が高いほど、
失業率は下がる）。
"""

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class OkunFit:
    """Δu = intercept + slope × 成長率 の係数。"""

    slope: float
    intercept: float


def output_gap_ratio(actual_gdp: float, potential_gdp: float) -> float:
    """需給ギャップ = (実際の GDP − 潜在 GDP) ÷ 潜在 GDP。負なら、需要不足。"""
    if potential_gdp <= 0:
        raise ValueError("潜在 GDP は、正にする")
    return (actual_gdp - potential_gdp) / potential_gdp


def okun_coefficients(
    growth: Sequence[float], unemployment_change: Sequence[float]
) -> OkunFit:
    """最小二乗法で、Δu = 切片 + 傾き × 成長率 の係数を求める。

    傾き = Σ(x − x̄)(y − ȳ) ÷ Σ(x − x̄)²、切片 = ȳ − 傾き × x̄。
    """
    if len(growth) != len(unemployment_change):
        raise ValueError("成長率と失業率の変化は、同じ長さにする")
    if len(growth) < 2:
        raise ValueError("回帰には、2 点以上が必要")
    x = np.asarray(growth, dtype=float)
    y = np.asarray(unemployment_change, dtype=float)
    dx = x - x.mean()
    if np.ptp(x) <= 1e-12 * max(1.0, float(np.abs(x).max())):
        raise ValueError("成長率がすべて同じで、傾きが決まらない")
    slope = float((dx * (y - y.mean())).sum() / (dx**2).sum())
    return OkunFit(slope=slope, intercept=float(y.mean() - slope * x.mean()))


def okun_breakeven_growth(fit: OkunFit) -> float:
    """失業率が変わらない（Δu = 0）成長率 = −切片 ÷ 傾き。"""
    if fit.slope == 0:
        raise ValueError("傾きが 0 で、失業率が変わらない成長率は決まらない")
    return -fit.intercept / fit.slope


def synthetic_unemployment_change(
    growth: Sequence[float],
    slope: float,
    intercept: float,
    noise: float,
    seed: int,
) -> list[float]:
    """関係 Δu = 切片 + 傾き × 成長率 に、正規分布の雑音を足した、架空のデータ。"""
    if noise < 0:
        raise ValueError("雑音の標準偏差は、0 以上にする")
    rng = np.random.default_rng(seed)
    x = np.asarray(growth, dtype=float)
    values = intercept + slope * x + rng.normal(0.0, noise, size=len(x))
    return [float(v) for v in values]
