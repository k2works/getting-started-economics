"""第 10 章: 効用最大化と利潤最大化の図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from lib.chapter04.cost import average_cost
from lib.chapter04.utility import cobb_douglas_utility
from lib.chapter10.plot import plot_profit_maximization, plot_utility_maximization

BUDGET = {"price_x": 2, "price_y": 4, "income": 40}


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def test_効用最大化の図には予算線と無差別曲線と最適点がある() -> None:
    ax = plot_utility_maximization(**BUDGET).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Budget line",
        "Indifference curve",
        "Optimum",
    ]


def test_予算線は財xだけ買う点20_0と財yだけ買う点0_10を結ぶ() -> None:
    ax = plot_utility_maximization(**BUDGET).axes[0]
    assert xy(ax.lines[0]) == [pytest.approx((0, 10)), pytest.approx((20, 0))]


def test_最適点は10_5() -> None:
    ax = plot_utility_maximization(**BUDGET).axes[0]
    assert xy(ax.lines[2]) == [pytest.approx((10, 5), abs=1e-4)]


def test_無差別曲線は最適点と同じ効用で予算線の上か外にある() -> None:
    ax = plot_utility_maximization(**BUDGET).axes[0]
    best = cobb_douglas_utility(10, 5)
    for x, y in xy(ax.lines[1]):
        assert cobb_douglas_utility(x, y) == pytest.approx(best)
        # 予算線の内側には、同じ効用の点がない（最適点で接する）
        assert 2 * x + 4 * y >= 40 - 1e-4


def test_財xの比重が大きいと最適点は右下に動く() -> None:
    ax = plot_utility_maximization(**BUDGET, alpha=0.75).axes[0]
    assert xy(ax.lines[2]) == [pytest.approx((15, 2.5), abs=1e-4)]


def test_利潤最大化の図には限界費用_平均可変費用_平均費用_価格_最適点がある() -> None:
    ax = plot_profit_maximization(price=15).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "MC",
        "AVC",
        "AC",
        "Price",
        "Optimum",
    ]


def test_価格15のとき最適な生産量は4() -> None:
    ax = plot_profit_maximization(price=15).axes[0]
    assert xy(ax.lines[4]) == [pytest.approx((4, 15), abs=1e-6)]


def test_利潤の長方形の面積は利潤22と等しい() -> None:
    ax = plot_profit_maximization(price=15).axes[0]
    box = next(p for p in ax.patches if isinstance(p, Rectangle))
    assert box.get_width() * box.get_height() == pytest.approx(22, abs=1e-6)
    assert box.get_y() == pytest.approx(average_cost(4), abs=1e-6)


def test_操業停止点を下回る価格では最適点も利潤も描かない() -> None:
    ax = plot_profit_maximization(price=5).axes[0]
    assert [line.get_label() for line in ax.lines] == ["MC", "AVC", "AC", "Price"]
    assert not any(isinstance(p, Rectangle) for p in ax.patches)
