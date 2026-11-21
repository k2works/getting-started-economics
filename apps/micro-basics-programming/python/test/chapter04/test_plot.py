"""第 4 章: スルツキー分解の図のテスト。"""

from collections.abc import Sequence
from typing import cast

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter04.plot import plot_cross_price, plot_slutsky


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_ydata())]


def line(ax: Axes, label: str) -> Line2D:
    return next(item for item in ax.lines if item.get_label() == label)


def slutsky() -> Axes:
    return plot_slutsky(80, 2, 0.5, 1, 100).axes[0]


def cross() -> Axes:
    return plot_cross_price(80, 2, [1, 2, 3, 4]).axes[0]


def test_スルツキー分解の図の線() -> None:
    labels = [item.get_label() for item in slutsky().lines]
    assert labels == [
        "U0 = 800",
        "U1 = 3200",
        "Original budget",
        "New budget",
        "Compensated budget (after income adjustment)",
        "A: original",
        "B: after substitution effect",
        "C: after income effect",
    ]


def test_3つの点は元の点と代替効果のあとと最終() -> None:
    ax = slutsky()
    points = {
        "A: original": (20, 40),
        "B: after substitution effect": (40, 20),
        "C: after income effect": (80, 40),
    }
    for label, (x, y) in points.items():
        assert xs(line(ax, label)) == pytest.approx([x])
        assert ys(line(ax, label)) == pytest.approx([y])


def test_予算線の傾きは価格比() -> None:
    ax = slutsky()

    def slope(label: str) -> float:
        item = line(ax, label)
        return (ys(item)[1] - ys(item)[0]) / (xs(item)[1] - xs(item)[0])

    assert slope("Original budget") == pytest.approx(-2)
    assert slope("New budget") == pytest.approx(-0.5)
    assert slope("Compensated budget (after income adjustment)") == pytest.approx(-0.5)


def test_補償された予算線は代替効果のあとの点を通る点線() -> None:
    ax = slutsky()
    compensated = line(ax, "Compensated budget (after income adjustment)")
    assert compensated.get_linestyle() == "--"
    # x = 40 のとき y = 20（点 B）。x 切片は 80、y 切片は 40
    assert xs(compensated) == pytest.approx([0, 80])
    assert ys(compensated) == pytest.approx([40, 0])


def test_元の無差別曲線は点AとBを通る() -> None:
    curve = line(slutsky(), "U0 = 800")
    for x, y in zip(xs(curve), ys(curve), strict=True):
        assert x * y == pytest.approx(800)


def test_スルツキー分解の図の軸と凡例() -> None:
    ax = slutsky()
    assert ax.get_xlabel() == "Good x"
    assert ax.get_ylabel() == "Good y"
    assert ax.get_xlim() == (0, 100)
    assert ax.get_ylim() == (0, 120)
    assert ax.get_legend() is not None


def test_交差価格効果の図は代替財と補完財の2本() -> None:
    ax = cross()
    assert [item.get_label() for item in ax.lines] == [
        "Perfect substitutes",
        "Perfect complements",
    ]


def test_代替財は相手が高くなると需要が増える() -> None:
    substitutes = line(cross(), "Perfect substitutes")
    assert xs(substitutes) == [1, 2, 3, 4]
    assert ys(substitutes) == [0, 40, 40, 40]


def test_補完財は相手が高くなると需要が減る() -> None:
    complements = line(cross(), "Perfect complements")
    assert ys(complements) == pytest.approx([80 / 3, 20, 16, 80 / 6])


def test_交差価格効果の図の軸と凡例() -> None:
    ax = cross()
    assert ax.get_xlabel() == "Price of good y"
    assert ax.get_ylabel() == "Demand for good x"
    assert ax.get_legend() is not None
