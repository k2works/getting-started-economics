"""第 9 章: 余剰と死荷重の図のテスト。"""

from collections.abc import Sequence
from typing import cast

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter08.market import LinearMarket
from lib.chapter09.plot import plot_surplus, plot_tax

MARKET = LinearMarket(100, -1, -10, 1)


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_ydata())]


def line(ax: Axes, label: str) -> Line2D:
    return next(item for item in ax.lines if item.get_label() == label)


def surplus() -> Axes:
    return plot_surplus(MARKET, 100, 100).axes[0]


def taxed() -> Axes:
    return plot_tax(MARKET, 9, 100, 100).axes[0]


def area(item: Line2D) -> float:
    """閉じた折れ線の面積（靴ひも公式）。"""
    x, y = xs(item), ys(item)
    total = sum(x[i] * y[i + 1] - x[i + 1] * y[i] for i in range(len(x) - 1))
    return abs(total) / 2


def test_余剰の図の線() -> None:
    assert [item.get_label() for item in surplus().lines] == [
        "Demand",
        "Supply",
        "Consumer surplus",
        "Producer surplus",
        "Equilibrium",
    ]


def test_消費者余剰の三角形の面積は余剰() -> None:
    item = line(surplus(), "Consumer surplus")
    assert (xs(item)[1], ys(item)[1]) == (45, 55)
    assert xs(item)[0] == 0
    assert ys(item)[0] == 100
    assert area(item) == pytest.approx(1012.5)


def test_生産者余剰の三角形の面積は余剰() -> None:
    item = line(surplus(), "Producer surplus")
    assert (xs(item)[1], ys(item)[1]) == (45, 55)
    assert ys(item)[0] == 10
    assert area(item) == pytest.approx(1012.5)


def test_余剰の図の軸と凡例() -> None:
    ax = surplus()
    assert ax.get_xlim() == (0, 100)
    assert ax.get_ylim() == (0, 100)
    assert ax.get_legend() is not None


def test_課税の図の線() -> None:
    assert [item.get_label() for item in taxed().lines] == [
        "Demand",
        "Supply",
        "Supply after tax",
        "Tax revenue",
        "Deadweight loss",
        "Equilibrium",
        "Equilibrium with tax",
    ]


def test_課税後の供給曲線は税額だけ上へ動く点線() -> None:
    ax = taxed()
    item = line(ax, "Supply after tax")
    assert item.get_linestyle() == "--"
    assert xs(item)[0] == 0
    assert ys(item)[0] == pytest.approx(19)
    assert (xs(item)[1], ys(item)[1]) == pytest.approx((81, 100))


def test_税収の長方形の面積は税収() -> None:
    item = line(taxed(), "Tax revenue")
    assert area(item) == pytest.approx(364.5)
    assert ys(item)[0] == pytest.approx(59.5)
    assert ys(item)[2] == pytest.approx(50.5)
    assert xs(item)[1] == pytest.approx(40.5)


def test_死荷重の三角形の面積は死荷重() -> None:
    item = line(taxed(), "Deadweight loss")
    assert area(item) == pytest.approx(20.25)
    assert xs(item)[0] == pytest.approx(40.5)
    assert (xs(item)[2], ys(item)[2]) == (45, 55)


def test_課税後の均衡点() -> None:
    point = line(taxed(), "Equilibrium with tax")
    assert (xs(point)[0], ys(point)[0]) == pytest.approx((40.5, 59.5))


def test_課税の図の軸と凡例() -> None:
    ax = taxed()
    assert ax.get_xlabel() == "Quantity Q"
    assert ax.get_ylabel() == "Price P"
    assert ax.get_legend() is not None


def test_余剰と税収と死荷重の面積は塗られている() -> None:
    assert len(surplus().patches) == 2
    assert len(taxed().patches) == 2
    for ax in (surplus(), taxed()):
        for patch in ax.patches:
            assert patch.get_alpha() == pytest.approx(0.25)
