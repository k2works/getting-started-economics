"""第 5 章: 信頼区間の図のテスト。"""

from typing import Any

import pandas as pd
import pytest

from lib.chapter05.plot import plot_confidence_intervals

TABLE = pd.DataFrame(
    {
        "lower": [0.3, 0.6, 0.1, 0.4],
        "upper": [0.7, 0.9, 0.4, 0.8],
    }
)


def ys(line: Any) -> list[float]:
    values: Any = line.get_ydata()
    return [float(v) for v in values]


def xs(line: Any) -> list[float]:
    values: Any = line.get_xdata()
    return [float(v) for v in values]


def test_区間ごとに縦線を描き最後に真の値の線を引く() -> None:
    ax = plot_confidence_intervals(TABLE, 0.5).axes[0]
    assert len(ax.lines) == 5
    assert [xs(line) for line in ax.lines[:4]] == [[0, 0], [1, 1], [2, 2], [3, 3]]
    assert ys(ax.lines[0]) == pytest.approx([0.3, 0.7])
    assert ys(ax.lines[4]) == [0.5, 0.5]


def test_含む区間と含まない区間で凡例の名前が違う() -> None:
    ax = plot_confidence_intervals(TABLE, 0.5).axes[0]
    labels = [line.get_label() for line in ax.lines]
    assert labels == [
        "Contains true value",
        "Misses true value",
        "_interval",
        "_interval",
        "True value",
    ]


def test_含む区間と含まない区間で色が違う() -> None:
    ax = plot_confidence_intervals(TABLE, 0.5).axes[0]
    colors = [line.get_color() for line in ax.lines[:4]]
    assert colors[0] == colors[3]
    assert colors[1] == colors[2]
    assert colors[0] != colors[1]


def test_真の値を含む区間は青で含まない区間は赤() -> None:
    ax = plot_confidence_intervals(TABLE, 0.5).axes[0]
    assert ax.lines[0].get_color() == "tab:blue"
    assert ax.lines[1].get_color() == "tab:red"


def test_軸の名前() -> None:
    ax = plot_confidence_intervals(TABLE, 0.5).axes[0]
    assert ax.get_xlabel() == "Sample"
    assert ax.get_ylabel() == "95% confidence interval of the slope"
