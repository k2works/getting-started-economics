"""第 10 章: 関税と生産可能性フロンティアの図のテスト。"""

from collections.abc import Sequence
from typing import cast

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter08.market import LinearMarket
from lib.chapter10.comparative import Country
from lib.chapter10.plot import plot_ppf, plot_tariff

MARKET = LinearMarket(100, -1, -10, 1)
LARGE = Country("Large", 4, 8)
SMALL = Country("Small", 20, 10)


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


def tariff() -> Axes:
    return plot_tariff(MARKET, 40, 10, 100, 100).axes[0]


def ppf() -> Axes:
    return plot_ppf(LARGE, 80, SMALL, 40).axes[0]


def test_関税の図の線() -> None:
    assert [item.get_label() for item in tariff().lines] == [
        "Demand",
        "Supply",
        "World price",
        "Price with tariff",
        "Tariff revenue",
        "Production loss",
        "Consumption loss",
    ]


def test_世界価格と関税のもとの国内価格は水平線() -> None:
    ax = tariff()
    assert ys(line(ax, "World price")) == [40, 40]
    assert ys(line(ax, "Price with tariff")) == [50, 50]
    assert xs(line(ax, "World price")) == [0, 100]


def test_関税収入の長方形の面積は関税収入() -> None:
    item = line(tariff(), "Tariff revenue")
    assert area(item) == pytest.approx(100)
    assert sorted(set(xs(item))) == [40, 50]


def test_2つの死荷重の三角形の面積はそれぞれ50() -> None:
    ax = tariff()
    assert area(line(ax, "Production loss")) == pytest.approx(50)
    assert area(line(ax, "Consumption loss")) == pytest.approx(50)


def test_生産の歪みは供給が増える側で消費の歪みは需要が減る側() -> None:
    ax = tariff()
    production = line(ax, "Production loss")
    consumption = line(ax, "Consumption loss")
    assert min(xs(production)) == pytest.approx(30)
    assert max(xs(production)) == pytest.approx(40)
    assert min(xs(consumption)) == pytest.approx(50)
    assert max(xs(consumption)) == pytest.approx(60)


def test_面積は塗られている() -> None:
    ax = tariff()
    assert len(ax.patches) == 3
    for patch in ax.patches:
        assert patch.get_alpha() == pytest.approx(0.25)


def test_関税の図の軸と凡例() -> None:
    ax = tariff()
    assert ax.get_xlabel() == "Quantity Q"
    assert ax.get_ylabel() == "Price P"
    assert ax.get_xlim() == (0, 100)
    assert ax.get_ylim() == (0, 100)
    assert ax.get_legend() is not None


def test_生産可能性フロンティアの図の線() -> None:
    assert [item.get_label() for item in ppf().lines] == ["Large", "Small"]


def test_大国のフロンティアは労働80人で工業20か農業10() -> None:
    item = line(ppf(), "Large")
    assert xs(item) == [20, 0]
    assert ys(item) == [0, 10]


def test_小国のフロンティアは労働40人で工業2か農業4() -> None:
    item = line(ppf(), "Small")
    assert xs(item) == [2, 0]
    assert ys(item) == [0, 4]


def test_傾きの大きさは工業の機会費用() -> None:
    ax = ppf()
    for label, cost in (("Large", 0.5), ("Small", 2.0)):
        item = line(ax, label)
        assert (ys(item)[1] - ys(item)[0]) / (xs(item)[0] - xs(item)[1]) == cost


def test_フロンティアの図の軸と凡例() -> None:
    ax = ppf()
    assert ax.get_xlabel() == "Industry"
    assert ax.get_ylabel() == "Agriculture"
    assert ax.get_xlim()[0] == 0
    assert ax.get_ylim()[0] == 0
    assert ax.get_legend() is not None


# --- 独立した変異確認で見つかった穴を埋めるテスト ---


def test_国内価格の線の両端() -> None:
    assert xs(line(tariff(), "Price with tariff")) == [0, 100]
