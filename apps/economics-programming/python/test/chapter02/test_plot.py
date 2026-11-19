"""第 2 章: 需要曲線上の価格弾力性の図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D

from lib.chapter02.plot import plot_elasticity_regions


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def point_elasticity(quantity: float, price: float, slope: float = 2) -> float:
    """需要曲線 Q = a - bP の上の点での価格弾力性 = b × P ÷ Q。"""
    return slope * price / quantity


def test_弾力性の図には弾力的な部分_非弾力的な部分_弾力性1の点がある() -> None:
    ax = plot_elasticity_regions(intercept=100, slope=2).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Elastic (e > 1)",
        "Inelastic (e < 1)",
        "Unit elasticity",
    ]


def test_弾力性が1になるのは需要曲線の真ん中の点で価格25_数量50() -> None:
    ax = plot_elasticity_regions(intercept=100, slope=2).axes[0]
    (point,) = xy(ax.lines[2])
    assert point == pytest.approx((50, 25))
    assert point_elasticity(point[0], point[1]) == pytest.approx(1)


def test_価格が高い部分は弾力的で低い部分は非弾力的() -> None:
    ax = plot_elasticity_regions(intercept=100, slope=2).axes[0]
    elastic = [(q, p) for q, p in xy(ax.lines[0]) if q > 0]
    inelastic = xy(ax.lines[1])
    assert all(point_elasticity(q, p) >= 1 - 1e-9 for q, p in elastic)
    assert all(point_elasticity(q, p) <= 1 + 1e-9 for q, p in inelastic)
    assert all(p >= 25 for _, p in elastic)
    assert all(p <= 25 for _, p in inelastic)
