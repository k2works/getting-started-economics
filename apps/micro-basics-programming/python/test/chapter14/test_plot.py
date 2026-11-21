"""第 14 章: シグナル（教育年数）と成果報酬の図のテスト。"""

from collections.abc import Sequence
from typing import cast

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter14.plot import plot_bonus, plot_signal


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_ydata())]


def line(ax: Axes, label: str) -> Line2D:
    return next(item for item in ax.lines if item.get_label() == label)


def signal() -> Axes:
    return plot_signal(100, 60, 10, 20, 6).axes[0]


def bonus() -> Axes:
    return plot_bonus(0.8, 0.4, 10, 60).axes[0]


def test_シグナルの図の線() -> None:
    assert [item.get_label() for item in signal().lines] == [
        "High type (signal)",
        "Low type (imitate)",
        "Low type (no signal)",
        "Lower bound",
        "Upper bound",
    ]


def test_高い能力の人の利得は教育で下がる() -> None:
    high = line(signal(), "High type (signal)")
    assert xs(high) == [0, 6]
    assert ys(high) == [100, pytest.approx(100 - 10 * 6)]


def test_低い能力の人がまねした利得は急に下がる() -> None:
    low = line(signal(), "Low type (imitate)")
    assert ys(low) == [100, pytest.approx(100 - 20 * 6)]


def test_教育しない低い能力の人の利得は水平線() -> None:
    flat = line(signal(), "Low type (no signal)")
    assert ys(flat) == [60, 60]
    assert xs(flat) == [0, 6]


def test_教育年数の範囲の端は2年と4年() -> None:
    ax = signal()
    assert xs(line(ax, "Lower bound")) == [pytest.approx(2)] * 2
    assert xs(line(ax, "Upper bound")) == [pytest.approx(4)] * 2
    assert line(ax, "Lower bound").get_linestyle() == ":"


def test_シグナルの図の軸と凡例() -> None:
    ax = signal()
    assert ax.get_xlim() == (0, 6)
    assert ax.get_xlabel() == "Years of education"
    assert ax.get_ylabel() == "Payoff"
    assert ax.get_legend() is not None


def test_成果報酬の図の線() -> None:
    assert [item.get_label() for item in bonus().lines] == [
        "Work",
        "Shirk",
        "Minimum bonus",
    ]


def test_努力する期待利得と努力しない期待利得() -> None:
    ax = bonus()
    work, shirk = line(ax, "Work"), line(ax, "Shirk")
    assert xs(work) == [0, 60]
    assert ys(work) == [pytest.approx(-10), pytest.approx(0.8 * 60 - 10)]
    assert ys(shirk) == [0, pytest.approx(0.4 * 60)]


def test_最低の成果報酬で2本の線が交わる() -> None:
    point = line(bonus(), "Minimum bonus")
    assert xs(point) == [pytest.approx(25)]
    assert ys(point) == [pytest.approx(0.4 * 25)]


def test_成果報酬の図の軸と凡例() -> None:
    ax = bonus()
    assert ax.get_xlim() == (0, 60)
    assert ax.get_xlabel() == "Bonus b"
    assert ax.get_ylabel() == "Expected payoff"
    assert ax.get_legend() is not None
