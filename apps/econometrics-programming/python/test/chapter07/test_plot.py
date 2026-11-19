"""第 7 章: ダミー変数の直線の図のテスト。"""

from typing import Any

import numpy as np
import pytest

from lib.chapter07.plot import plot_group_lines

X = np.array([1.0, 2.0, 3.0, 1.0, 2.0, 3.0])
D = np.array([0.0, 0.0, 0.0, 1.0, 1.0, 1.0])
Y = np.array([1.0, 2.0, 3.0, 3.0, 4.0, 5.0])


def ys(line: Any) -> list[float]:
    values: Any = line.get_ydata()
    return [float(v) for v in values]


def test_群ごとにデータと直線を描く() -> None:
    ax = plot_group_lines(X, Y, D, interaction=False).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Group 0",
        "Group 1",
        "Fit group 0",
        "Fit group 1",
    ]
    assert ys(ax.lines[0]) == [1, 2, 3]
    assert ys(ax.lines[1]) == [3, 4, 5]


def test_切片だけ違う直線は平行() -> None:
    ax = plot_group_lines(X, Y, D, interaction=False).axes[0]
    assert ys(ax.lines[2]) == pytest.approx([1, 3])
    assert ys(ax.lines[3]) == pytest.approx([3, 5])


def test_交差項があると傾きも変わる() -> None:
    y = Y.copy()
    y[3:] = [3.0, 5.0, 7.0]
    ax = plot_group_lines(X, y, D, interaction=True).axes[0]
    assert ys(ax.lines[2]) == pytest.approx([1, 3])
    assert ys(ax.lines[3]) == pytest.approx([3, 7])


def test_軸の名前() -> None:
    ax = plot_group_lines(X, Y, D, interaction=False).axes[0]
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y"
