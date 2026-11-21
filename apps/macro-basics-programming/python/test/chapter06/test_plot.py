"""第 6 章: 貨幣乗数と信用創造の図のテスト。"""

import numpy as np
import pytest
from matplotlib.lines import Line2D

from lib.chapter06.plot import plot_credit_creation, plot_money_multiplier


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_ydata())]


def test_貨幣乗数の図は準備率ごとに1本の線を描く() -> None:
    ax = plot_money_multiplier([0.0, 0.1, 0.2], [0.01, 0.1]).axes[0]
    assert [line.get_label() for line in ax.lines] == ["R/D = 0.01", "R/D = 0.1"]


def test_貨幣乗数の線の座標() -> None:
    ax = plot_money_multiplier([0.0, 0.1, 0.2], [0.01, 0.1]).axes[0]
    assert xs(ax.lines[0]) == pytest.approx([0.0, 0.1, 0.2])
    assert ys(ax.lines[0]) == pytest.approx([100, 10, 1.2 / 0.21])
    assert ys(ax.lines[1]) == pytest.approx([10, 5.5, 1.2 / 0.3])


def test_信用創造の図はラウンドごとのマネーストックと上限を描く() -> None:
    ax = plot_credit_creation(110, 0.1, 0.01, 3).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Money stock after each round",
        "Limit (multiplier x H)",
    ]
    assert xs(ax.lines[0]) == pytest.approx([1, 2, 3])
    assert ys(ax.lines[0]) == pytest.approx([110, 209, 1100 * (1 - 0.9**3)])


def test_信用創造の上限は貨幣乗数とハイパワードマネーの積() -> None:
    ax = plot_credit_creation(110, 0.1, 0.01, 3).axes[0]
    assert ys(ax.lines[1]) == pytest.approx([1100, 1100])
    assert xs(ax.lines[1]) == pytest.approx([1, 3])


def test_軸の名前() -> None:
    ax = plot_money_multiplier([0.0, 0.1], [0.01]).axes[0]
    assert ax.get_xlabel() == "Cash-deposit ratio C/D"
    assert ax.get_ylabel() == "Money multiplier"
    ax2 = plot_credit_creation(110, 0.1, 0.01, 3).axes[0]
    assert ax2.get_xlabel() == "Round"
    assert ax2.get_ylabel() == "Money stock"
