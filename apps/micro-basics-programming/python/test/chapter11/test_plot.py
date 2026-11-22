"""第 11 章: 独占と独占的競争の図のテスト。"""

import math
from collections.abc import Sequence
from typing import cast

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter11.monopoly import Monopoly
from lib.chapter11.plot import plot_long_run, plot_monopoly

MONOPOLY = Monopoly(100, 1, 10)


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_ydata())]


def line(ax: Axes, label: str) -> Line2D:
    return next(item for item in ax.lines if item.get_label() == label)


def area(item: Line2D) -> float:
    """閉じた折れ線の面積（靴ひも公式）。"""
    x, y = xs(item), ys(item)
    total = sum(x[i] * y[i + 1] - x[i + 1] * y[i] for i in range(len(x) - 1))
    return abs(total) / 2


def monopoly() -> Axes:
    return plot_monopoly(MONOPOLY, 100, 100).axes[0]


def long_run() -> Axes:
    return plot_long_run(MONOPOLY, 1000, 100, 100).axes[0]


def test_独占の図の線() -> None:
    assert [item.get_label() for item in monopoly().lines] == [
        "Demand",
        "Marginal revenue",
        "Marginal cost",
        "Monopoly profit",
        "Deadweight loss",
        "Monopoly point",
        "Competitive point",
    ]


def test_限界収入は需要曲線の2倍の傾き() -> None:
    ax = monopoly()
    demand, revenue = line(ax, "Demand"), line(ax, "Marginal revenue")
    assert (xs(demand), ys(demand)) == ([0, 100], [100, 0])
    assert (xs(revenue), ys(revenue)) == ([0, 50], [100, 0])


def test_限界費用は水平線() -> None:
    cost = line(monopoly(), "Marginal cost")
    assert ys(cost) == [10, 10]
    assert xs(cost) == [0, 100]


def test_独占点と競争点() -> None:
    ax = monopoly()
    mono, comp = line(ax, "Monopoly point"), line(ax, "Competitive point")
    assert (xs(mono)[0], ys(mono)[0]) == (45, 55)
    assert (xs(comp)[0], ys(comp)[0]) == (90, 10)


def test_独占の利潤の長方形と死荷重の三角形の面積() -> None:
    ax = monopoly()
    assert area(line(ax, "Monopoly profit")) == pytest.approx(2025)
    assert area(line(ax, "Deadweight loss")) == pytest.approx(1012.5)


def test_面積は塗られている() -> None:
    ax = monopoly()
    assert len(ax.patches) == 2
    for patch in ax.patches:
        assert patch.get_alpha() == pytest.approx(0.25)


def test_独占の図の軸と凡例() -> None:
    ax = monopoly()
    assert ax.get_xlabel() == "Quantity Q"
    assert ax.get_ylabel() == "Price P"
    assert ax.get_xlim() == (0, 100)
    assert ax.get_ylim() == (0, 100)
    assert ax.get_legend() is not None


def test_独占的競争の図の線() -> None:
    assert [item.get_label() for item in long_run().lines] == [
        "Demand before entry",
        "Demand after entry",
        "Marginal cost",
        "Average cost",
        "Long-run equilibrium",
    ]


def test_参入後の需要は点線で左へ動く() -> None:
    ax = long_run()
    after = line(ax, "Demand after entry")
    assert after.get_linestyle() == "--"
    assert ys(after)[0] == pytest.approx(10 + 2 * math.sqrt(1000))
    assert ys(after)[0] < ys(line(ax, "Demand before entry"))[0]
    assert line(ax, "Demand before entry").get_linestyle() == "-"


def test_長期均衡で価格は平均費用に等しい() -> None:
    ax = long_run()
    point = line(ax, "Long-run equilibrium")
    q, p = xs(point)[0], ys(point)[0]
    assert q == pytest.approx(math.sqrt(1000))
    assert p == pytest.approx(10 + 1000 / q)


def test_平均費用の曲線は100点で右下がり() -> None:
    average = line(long_run(), "Average cost")
    assert len(xs(average)) == 100
    assert xs(average)[0] == pytest.approx(1)
    assert xs(average)[-1] == pytest.approx(100)
    for q, cost in zip(xs(average), ys(average), strict=True):
        assert cost == pytest.approx(10 + 1000 / q)
    assert all(a > b for a, b in zip(ys(average), ys(average)[1:], strict=False))


def test_独占的競争の図の軸と凡例() -> None:
    ax = long_run()
    assert ax.get_xlim() == (0, 100)
    assert ax.get_ylim() == (0, 100)
    assert ax.get_legend() is not None


def test_傾きが2の市場の線は傾きで割った端点を持つ() -> None:
    ax = plot_monopoly(Monopoly(100, 2, 10), 100, 100).axes[0]
    assert xs(line(ax, "Demand")) == [0, 50]
    assert xs(line(ax, "Marginal revenue")) == [0, 25]
    ax = plot_long_run(Monopoly(100, 2, 10), 400, 100, 100).axes[0]
    assert xs(line(ax, "Demand before entry")) == [0, 50]
    assert ys(line(ax, "Demand before entry")) == [100, 0]
