"""第 1 章: 無差別曲線の図のテスト。"""

from collections.abc import Sequence
from typing import cast

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter01.plot import plot_indifference_curves, plot_special_utilities
from lib.chapter01.utility import (
    cobb_douglas_utility,
    concave_utility,
    perfect_complements_utility,
    perfect_substitutes_utility,
)


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_ydata())]


def curves() -> Axes:
    return plot_indifference_curves([400, 800, 1200], 5, 80).axes[0]


def special() -> list[Axes]:
    return plot_special_utilities().axes


def test_無差別曲線の族は水準ごとに1本ずつ() -> None:
    ax = curves()
    assert [line.get_label() for line in ax.lines] == [
        "U = 400",
        "U = 800",
        "U = 1200",
    ]


def test_曲線の上の点は効用が水準と等しい() -> None:
    for line, level in zip(curves().lines, [400, 800, 1200], strict=True):
        for x, y in zip(xs(line), ys(line), strict=True):
            assert cobb_douglas_utility(x, y) == pytest.approx(level)


def test_曲線は指定した範囲のxで右下がり() -> None:
    line = curves().lines[1]
    assert xs(line)[0] == pytest.approx(5)
    assert xs(line)[-1] == pytest.approx(80)
    assert ys(line)[0] == pytest.approx(160)
    assert ys(line)[-1] == pytest.approx(10)
    assert all(a > b for a, b in zip(ys(line), ys(line)[1:], strict=False))


def test_効用の高い曲線ほど右上にある() -> None:
    lines = curves().lines
    for a, b in zip(lines, lines[1:], strict=False):
        assert all(y2 > y1 for y1, y2 in zip(ys(a), ys(b), strict=True))


def test_軸の名前と凡例() -> None:
    ax = curves()
    assert ax.get_xlabel() == "Good x"
    assert ax.get_ylabel() == "Good y"
    assert ax.get_ylim()[0] == 0
    assert ax.get_xlim()[0] == 0
    legend = ax.get_legend()
    assert legend is not None
    assert [t.get_text() for t in legend.get_texts()] == [
        "U = 400",
        "U = 800",
        "U = 1200",
    ]


def test_特別な効用の図は3つの小さな図が左右に並ぶ() -> None:
    left, middle, right = special()
    assert left.get_position().x1 < middle.get_position().x0
    assert middle.get_position().x1 < right.get_position().x0
    assert [ax.get_title() for ax in (left, middle, right)] == [
        "Perfect substitutes",
        "Perfect complements",
        "Concave",
    ]


def test_完全代替財は直線() -> None:
    ax = special()[0]
    for line, level in zip(ax.lines, [20, 40], strict=True):
        assert line.get_label() == f"U = {level}"
        for x, y in zip(xs(line), ys(line), strict=True):
            assert perfect_substitutes_utility(x, y, 2, 1) == pytest.approx(level)
        slope = (ys(line)[1] - ys(line)[0]) / (xs(line)[1] - xs(line)[0])
        assert slope == pytest.approx(-2)


def test_完全補完財はL字() -> None:
    ax = special()[1]
    first = ax.lines[0]
    assert first.get_label() == "U = 4"
    assert list(zip(xs(first), ys(first), strict=True)) == [(4, 10), (4, 4), (10, 4)]
    for line, level in zip(ax.lines, [4, 8], strict=True):
        for x, y in zip(xs(line), ys(line), strict=True):
            assert perfect_complements_utility(x, y) == level


def test_別々に消費したいときは円の一部() -> None:
    ax = special()[2]
    for line, level in zip(ax.lines, [25, 100], strict=True):
        assert line.get_label() == f"U = {level}"
        for x, y in zip(xs(line), ys(line), strict=True):
            assert concave_utility(x, y) == pytest.approx(level)
        assert xs(line)[0] == pytest.approx(0)
        assert ys(line)[0] > ys(line)[-1]


def test_特別な図の軸と凡例() -> None:
    for ax in special():
        assert ax.get_xlabel() == "Good x"
        assert ax.get_ylabel() == "Good y"
        assert ax.get_legend() is not None
        assert ax.get_xlim()[0] == 0
        assert ax.get_ylim()[0] == 0


def test_曲線は50点で描く() -> None:
    assert all(len(xs(line)) == 50 for line in curves().lines)
