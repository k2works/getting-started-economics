"""第 3 章: 需要表と供給表の図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D

from lib.chapter03.plot import plot_schedules
from lib.chapter03.schedule import demand_schedule, supply_schedule

PRICES = [0, 10, 20, 30]


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def test_需要表と供給表の図には需要と供給の2本の線と均衡点がある() -> None:
    demand = demand_schedule(PRICES, intercept=100, slope=2)
    supply = supply_schedule(PRICES, intercept=0, slope=3)
    ax = plot_schedules(demand, supply).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Demand",
        "Supply",
        "Market clearing",
    ]


def test_表の価格ごとの数量が点になる() -> None:
    demand = demand_schedule(PRICES, intercept=100, slope=2)
    supply = supply_schedule(PRICES, intercept=0, slope=3)
    ax = plot_schedules(demand, supply).axes[0]
    assert xy(ax.lines[0]) == [
        pytest.approx((100, 0)),
        pytest.approx((80, 10)),
        pytest.approx((60, 20)),
        pytest.approx((40, 30)),
    ]
    assert xy(ax.lines[1]) == [
        pytest.approx((0, 0)),
        pytest.approx((30, 10)),
        pytest.approx((60, 20)),
        pytest.approx((90, 30)),
    ]


def test_需要量と供給量が等しい価格20が均衡点になる() -> None:
    demand = demand_schedule(PRICES, intercept=100, slope=2)
    supply = supply_schedule(PRICES, intercept=0, slope=3)
    ax = plot_schedules(demand, supply).axes[0]
    assert xy(ax.lines[2]) == [pytest.approx((60, 20))]


def test_需要量と供給量が等しい価格がなければ均衡点は描かない() -> None:
    demand = demand_schedule([0, 15, 30], intercept=100, slope=2)
    supply = supply_schedule([0, 15, 30], intercept=0, slope=3)
    ax = plot_schedules(demand, supply).axes[0]
    assert [line.get_label() for line in ax.lines] == ["Demand", "Supply"]
