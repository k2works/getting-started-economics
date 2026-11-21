"""第 8 章: 需要曲線・供給曲線・調整過程の図のテスト。"""

from collections.abc import Sequence
from typing import cast

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter08.market import LinearMarket
from lib.chapter08.plot import plot_adjustment, plot_market, plot_shift

MARKET = LinearMarket(100, -1, -10, 1)


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_ydata())]


def line(ax: Axes, label: str) -> Line2D:
    return next(item for item in ax.lines if item.get_label() == label)


def market() -> Axes:
    return plot_market(MARKET, 100, 100).axes[0]


def shifted() -> Axes:
    return plot_shift(MARKET, 20, 100, 100).axes[0]


def adjustment() -> list[Axes]:
    return plot_adjustment(MARKET, 80, 0, 0.25, 10).axes


def test_市場の図の線() -> None:
    assert [item.get_label() for item in market().lines] == [
        "Demand",
        "Supply",
        "Equilibrium",
    ]


def test_需要曲線は右下がりで両軸の切片を通る() -> None:
    item = line(market(), "Demand")
    assert xs(item) == [0, 100]
    assert ys(item) == [100, 0]


def test_供給曲線は右上がりで価格10から始まる() -> None:
    item = line(market(), "Supply")
    assert xs(item) == [0, 90]
    assert ys(item) == [10, 100]


def test_均衡点は需要と供給の交点() -> None:
    point = line(market(), "Equilibrium")
    assert (xs(point)[0], ys(point)[0]) == (45, 55)


def test_市場の図の軸と凡例() -> None:
    ax = market()
    assert ax.get_xlabel() == "Quantity Q"
    assert ax.get_ylabel() == "Price P"
    assert ax.get_xlim() == (0, 100)
    assert ax.get_ylim() == (0, 100)
    assert ax.get_legend() is not None


def test_シフトの図の線() -> None:
    assert [item.get_label() for item in shifted().lines] == [
        "Demand",
        "Supply",
        "Demand after shift",
        "Equilibrium before",
        "Equilibrium after",
    ]


def test_需要のシフトは点線で右へ20動く() -> None:
    ax = shifted()
    after = line(ax, "Demand after shift")
    assert after.get_linestyle() == "--"
    assert xs(after) == [0, 120]
    assert ys(after) == [120, 0]
    assert line(ax, "Demand").get_linestyle() == "-"


def test_シフトの前後の均衡() -> None:
    ax = shifted()
    before, after = line(ax, "Equilibrium before"), line(ax, "Equilibrium after")
    assert (xs(before)[0], ys(before)[0]) == (45, 55)
    assert (xs(after)[0], ys(after)[0]) == pytest.approx((55, 65))


def test_シフトの図の軸と凡例() -> None:
    ax = shifted()
    assert ax.get_xlim() == (0, 100)
    assert ax.get_ylim() == (0, 100)
    assert ax.get_legend() is not None


def test_調整の図は価格と数量の2つの図が左右に並ぶ() -> None:
    left, right = adjustment()
    assert left.get_position().x1 < right.get_position().x0
    assert left.get_title() == "Walras (price)"
    assert right.get_title() == "Marshall (quantity)"


def test_ワルラス的調整の価格の推移() -> None:
    left, _ = adjustment()
    path = line(left, "Price")
    assert xs(path) == list(range(11))
    assert ys(path)[:3] == pytest.approx([80, 67.5, 61.25])
    assert ys(line(left, "Equilibrium price")) == [55, 55]
    assert xs(line(left, "Equilibrium price")) == [0, 10]


def test_マーシャル的調整の数量の推移() -> None:
    _, right = adjustment()
    path = line(right, "Quantity")
    assert xs(path) == list(range(11))
    assert ys(path)[:3] == pytest.approx([0, 22.5, 33.75])
    assert ys(line(right, "Equilibrium quantity")) == [45, 45]


def test_調整の図の軸と凡例() -> None:
    for ax in adjustment():
        assert ax.get_xlabel() == "Step"
        assert ax.get_legend() is not None
    assert adjustment()[0].get_ylabel() == "Price P"
    assert adjustment()[1].get_ylabel() == "Quantity Q"
