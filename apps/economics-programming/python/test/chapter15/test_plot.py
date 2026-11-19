"""第 15 章: 独占の図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Rectangle

from lib.chapter15.monopoly import monopoly_outcome
from lib.chapter15.plot import plot_monopoly

DEMAND = {"demand_intercept": 100, "demand_slope": 2}


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def area(polygon: Polygon) -> float:
    """多角形の面積（靴ひも公式）。"""
    vertices: Any = polygon.get_xy()
    points = [(float(x), float(y)) for x, y in vertices]
    pairs = zip(points, points[1:] + points[:1], strict=True)
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in pairs)) / 2


def test_独占の図には需要_限界収入_限界費用の線と独占点_競争点がある() -> None:
    ax = plot_monopoly(**DEMAND, marginal_cost=10).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Demand",
        "MR",
        "MC",
        "Monopoly",
        "Competitive",
    ]


def test_限界収入の線は需要曲線の2倍の傾き() -> None:
    ax = plot_monopoly(**DEMAND, marginal_cost=10).axes[0]
    demand, mr = xy(ax.lines[0]), xy(ax.lines[1])
    demand_slope = (demand[1][1] - demand[0][1]) / (demand[1][0] - demand[0][0])
    mr_slope = (mr[1][1] - mr[0][1]) / (mr[1][0] - mr[0][0])
    assert mr_slope == pytest.approx(2 * demand_slope)


def test_独占点と競争点の位置() -> None:
    ax = plot_monopoly(**DEMAND, marginal_cost=10).axes[0]
    assert xy(ax.lines[3])[0] == pytest.approx((40, 30))
    assert xy(ax.lines[4])[0] == pytest.approx((80, 10))


def test_死荷重の三角形の面積は独占の死荷重と等しい() -> None:
    ax = plot_monopoly(**DEMAND, marginal_cost=10).axes[0]
    triangle = next(p for p in ax.patches if isinstance(p, Polygon))
    outcome = monopoly_outcome(**DEMAND, marginal_cost=10)
    assert area(triangle) == pytest.approx(outcome.deadweight_loss)


def test_利潤の長方形の面積は独占の利潤と等しい() -> None:
    ax = plot_monopoly(**DEMAND, marginal_cost=10).axes[0]
    box = next(p for p in ax.patches if isinstance(p, Rectangle))
    outcome = monopoly_outcome(**DEMAND, marginal_cost=10)
    assert box.get_width() * box.get_height() == pytest.approx(outcome.profit)


def test_死荷重の三角形の頂点は独占点と競争点と限界費用の線の上の点() -> None:
    ax = plot_monopoly(**DEMAND, marginal_cost=10).axes[0]
    triangle = next(p for p in ax.patches if isinstance(p, Polygon))
    vertices: Any = triangle.get_xy()
    corners = {(round(float(x), 6), round(float(y), 6)) for x, y in vertices}
    assert corners == {(40, 30), (40, 10), (80, 10)}
