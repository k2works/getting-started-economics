"""第 13 章: 外部不経済と自然独占の図のテスト。"""

from collections.abc import Sequence
from typing import cast

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter11.monopoly import Monopoly
from lib.chapter13.externality import ExternalityMarket
from lib.chapter13.plot import plot_externality, plot_natural_monopoly

POLLUTION = ExternalityMarket(100, 1, 10, 1, 20)
DEMAND = Monopoly(100, 1, 10)


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


def externality() -> Axes:
    return plot_externality(POLLUTION, 100, 100).axes[0]


def natural() -> Axes:
    return plot_natural_monopoly(DEMAND, 800, 100, 100).axes[0]


def test_外部不経済の図の線() -> None:
    assert [item.get_label() for item in externality().lines] == [
        "Demand",
        "Private marginal cost",
        "Social marginal cost",
        "Deadweight loss",
        "Market point",
        "Optimal point",
    ]


def test_社会的限界費用は私的限界費用より外部費用だけ高い() -> None:
    ax = externality()
    private = line(ax, "Private marginal cost")
    social = line(ax, "Social marginal cost")
    assert (xs(private), ys(private)) == ([0, 100], [10, 110])
    assert xs(social) == [0, 100]
    assert [s - p for s, p in zip(ys(social), ys(private), strict=True)] == [20, 20]
    assert social.get_linestyle() == "--"


def test_市場の点と最適な点() -> None:
    ax = externality()
    market, optimal = line(ax, "Market point"), line(ax, "Optimal point")
    assert (xs(market)[0], ys(market)[0]) == (45, 55)
    assert (xs(optimal)[0], ys(optimal)[0]) == (35, 65)


def test_死荷重の三角形の面積() -> None:
    ax = externality()
    assert area(line(ax, "Deadweight loss")) == pytest.approx(100)
    assert len(ax.patches) == 1
    assert ax.patches[0].get_alpha() == pytest.approx(0.25)


def test_外部不経済の図の軸と凡例() -> None:
    ax = externality()
    assert ax.get_xlim() == (0, 100)
    assert ax.get_ylim() == (0, 100)
    assert ax.get_xlabel() == "Quantity Q"
    assert ax.get_ylabel() == "Price P"
    assert ax.get_legend() is not None


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
