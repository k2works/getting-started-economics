"""第 1 章: 需要曲線の図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D

from lib.chapter01.plot import plot_demand_curve


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def test_需要曲線の図には需要曲線とチョーク価格と数量の切片がある() -> None:
    ax = plot_demand_curve(intercept=100, slope=2).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Demand",
        "Choke price",
        "Quantity at price 0",
    ]


def test_需要曲線は価格0で数量100_価格50で数量0を通る() -> None:
    ax = plot_demand_curve(intercept=100, slope=2).axes[0]
    assert xy(ax.lines[0]) == [pytest.approx((100, 0)), pytest.approx((0, 50))]


def test_チョーク価格は縦軸の切片_数量の切片は横軸の切片() -> None:
    ax = plot_demand_curve(intercept=100, slope=2).axes[0]
    assert xy(ax.lines[1]) == [pytest.approx((0, 50))]
    assert xy(ax.lines[2]) == [pytest.approx((100, 0))]
