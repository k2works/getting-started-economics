"""第 15 章: 自然独占の図のテスト。"""

from collections.abc import Sequence
from typing import cast

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter11.monopoly import Monopoly
from lib.chapter15.plot import plot_natural_monopoly

DEMAND = Monopoly(100, 1, 10)


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_ydata())]


def line(ax: Axes, label: str) -> Line2D:
    return next(item for item in ax.lines if item.get_label() == label)


def natural() -> Axes:
    return plot_natural_monopoly(DEMAND, 800, 100, 100).axes[0]


def test_自然独占の図の線() -> None:
    assert [item.get_label() for item in natural().lines] == [
        "Demand",
        "Marginal cost",
        "Average cost",
        "MC pricing",
        "AC pricing",
        "Unregulated",
    ]


def test_平均費用は右下がりで限界費用より高い() -> None:
    ax = natural()
    average = line(ax, "Average cost")
    assert len(xs(average)) == 100
    for q, cost in zip(xs(average), ys(average), strict=True):
        assert cost == pytest.approx(10 + 800 / q)
    assert all(a > b for a, b in zip(ys(average), ys(average)[1:], strict=False))
    assert ys(line(ax, "Marginal cost")) == [10, 10]


def test_3つの価格設定の点() -> None:
    ax = natural()
    mc, ac, free = (
        line(ax, "MC pricing"),
        line(ax, "AC pricing"),
        line(ax, "Unregulated"),
    )
    assert (xs(mc)[0], ys(mc)[0]) == (90, 10)
    assert (xs(ac)[0], ys(ac)[0]) == (pytest.approx(80), pytest.approx(20))
    assert (xs(free)[0], ys(free)[0]) == (45, 55)


def test_自然独占の図の軸と凡例() -> None:
    ax = natural()
    assert ax.get_xlim() == (0, 100)
    assert ax.get_ylim() == (0, 100)
    assert ax.get_legend() is not None


def test_傾きが2の市場の需要曲線の端点() -> None:
    ax = plot_natural_monopoly(Monopoly(100, 2, 10), 400, 100, 100).axes[0]
    assert xs(line(ax, "Demand")) == [0, 50]
