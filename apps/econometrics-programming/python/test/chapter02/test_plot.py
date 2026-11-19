"""第 2 章: 回帰直線と、傾きの標本分布の図のテスト。"""

from typing import Any

import pytest

from lib.chapter02.plot import plot_regression_line, plot_slope_distribution
from lib.chapter02.simple import fit_simple

X = [1, 2, 3, 4]
Y = [2, 4, 5, 9]


def ys(line: Any) -> list[float]:
    data: Any = line.get_ydata()
    return [float(v) for v in data]


def xs(line: Any) -> list[float]:
    data: Any = line.get_xdata()
    return [float(v) for v in data]


def test_回帰直線の図はデータと直線と残差を描く() -> None:
    ax = plot_regression_line(X, Y, fit_simple(X, Y)).axes[0]
    labels = [line.get_label() for line in ax.lines]
    assert labels[:2] == ["Data", "Fitted line"]
    assert labels[2:] == ["_residual"] * 4
    assert xs(ax.lines[0]) == X
    assert ys(ax.lines[0]) == Y


def test_直線は傾き2点2を通る() -> None:
    ax = plot_regression_line(X, Y, fit_simple(X, Y)).axes[0]
    x, y = xs(ax.lines[1]), ys(ax.lines[1])
    assert x == [1, 4]
    assert y == pytest.approx([1.7, 8.3])


def test_残差の線は当てはめ値とデータを結ぶ() -> None:
    ax = plot_regression_line(X, Y, fit_simple(X, Y)).axes[0]
    first = ax.lines[2]
    assert xs(first) == [1, 1]
    assert ys(first) == pytest.approx([1.7, 2])
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y"


def test_傾きの分布の図は棒と真の値の線() -> None:
    slopes = [0.4, 0.5, 0.5, 0.6, 0.5, 0.45]
    ax = plot_slope_distribution(slopes, 0.5).axes[0]
    assert len(ax.patches) == 10
    assert [line.get_label() for line in ax.lines] == ["True slope"]
    assert xs(ax.lines[0]) == [0.5, 0.5]
    assert ax.get_xlabel() == "Estimated slope"
    assert ax.get_ylabel() == "Frequency"
    bars: list[Any] = list(ax.patches)
    assert sum(p.get_height() for p in bars) == len(slopes)
