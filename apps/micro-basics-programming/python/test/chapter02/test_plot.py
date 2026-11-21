"""第 2 章: 予算線と最適消費点の図のテスト。"""

from collections.abc import Sequence
from typing import cast

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter01.utility import cobb_douglas_utility
from lib.chapter02.plot import plot_optimal_choice, plot_price_change


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_ydata())]


def line(ax: Axes, label: str) -> Line2D:
    return next(item for item in ax.lines if item.get_label() == label)


def choice() -> Axes:
    return plot_optimal_choice(80, 2, 1, [400, 800, 1200], 45).axes[0]


def price_change() -> Axes:
    return plot_price_change(80, [4, 2, 1], 1).axes[0]


def test_最適消費点の図の線() -> None:
    ax = choice()
    assert [item.get_label() for item in ax.lines] == [
        "U = 400",
        "U = 800",
        "U = 1200",
        "Budget line",
        "Optimum",
    ]


def test_予算線の端は両軸の切片() -> None:
    budget = line(choice(), "Budget line")
    assert xs(budget) == [0, 40]
    assert ys(budget) == [80, 0]


def test_最適消費点は予算線と無差別曲線の接点() -> None:
    ax = choice()
    optimum = line(ax, "Optimum")
    assert xs(optimum) == [20]
    assert ys(optimum) == [40]
    curve = line(ax, "U = 800")
    for x, y in zip(xs(curve), ys(curve), strict=True):
        assert cobb_douglas_utility(x, y) == pytest.approx(800)


def test_最適消費点の図の軸と凡例() -> None:
    ax = choice()
    assert ax.get_xlabel() == "Good x"
    assert ax.get_ylabel() == "Good y"
    assert ax.get_xlim()[0] == 0
    assert ax.get_ylim() == (0, 120)
    legend = ax.get_legend()
    assert legend is not None
    assert len(legend.get_texts()) == 5


def test_価格変化の図は価格ごとに予算線と最適点() -> None:
    ax = price_change()
    assert [item.get_label() for item in ax.lines] == [
        "Px = 4",
        "Px = 2",
        "Px = 1",
        "Price-consumption curve",
    ]


def test_価格が下がるとx切片だけが右へ動く() -> None:
    ax = price_change()
    assert [xs(line(ax, f"Px = {p}"))[1] for p in (4, 2, 1)] == [20, 40, 80]
    assert [ys(line(ax, f"Px = {p}"))[0] for p in (4, 2, 1)] == [80, 80, 80]


def test_価格消費曲線は各価格の最適点をつなぐ() -> None:
    curve = line(price_change(), "Price-consumption curve")
    assert xs(curve) == pytest.approx([10, 20, 40])
    assert ys(curve) == pytest.approx([40, 40, 40])


def test_価格変化の図の軸と凡例() -> None:
    ax = price_change()
    assert ax.get_xlabel() == "Good x"
    assert ax.get_ylabel() == "Good y"
    assert ax.get_ylim() == (0, 120)
    assert ax.get_legend() is not None


# --- 独立した変異確認で見つかった穴を埋めるテスト ---


def test_無差別曲線は50点で右端はx_max() -> None:
    curve = line(choice(), "U = 800")
    assert len(xs(curve)) == 50
    assert xs(curve)[0] == pytest.approx(45 / 50)
    assert xs(curve)[-1] == pytest.approx(45)


def test_財yの価格が1でないとき() -> None:
    ax = plot_optimal_choice(80, 2, 2, [400], 45).axes[0]
    assert ax.get_ylim() == (0, 60)
    assert ys(line(ax, "Budget line")) == [40, 0]
    ax2 = plot_price_change(80, [4, 2, 1], 2).axes[0]
    assert ax2.get_ylim() == (0, 60)
    assert [ys(line(ax2, f"Px = {p}"))[0] for p in (4, 2, 1)] == [40, 40, 40]
