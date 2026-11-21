"""第 12 章: 屈折需要曲線と、協調が続く条件の図のテスト。"""

from collections.abc import Sequence
from typing import cast

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter12.kinked import KinkedDemand
from lib.chapter12.plot import plot_kinked, plot_trigger

KINKED = KinkedDemand(40, 50, 0.5, 2)


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_ydata())]


def line(ax: Axes, label: str) -> Line2D:
    return next(item for item in ax.lines if item.get_label() == label)


def kinked() -> Axes:
    return plot_kinked(KINKED, 100, 80, 10, 25).axes[0]


def trigger() -> Axes:
    return plot_trigger(5, 3, 1, 0.95, 100, 60).axes[0]


def test_屈折需要曲線の図の線() -> None:
    assert [item.get_label() for item in kinked().lines] == [
        "Demand",
        "Marginal revenue (upper)",
        "Marginal revenue (lower)",
        "MR gap",
        "Marginal cost (low)",
        "Marginal cost (high)",
    ]


def test_需要曲線は屈折点で傾きが変わる() -> None:
    demand = line(kinked(), "Demand")
    assert xs(demand)[1] == 40
    assert ys(demand)[1] == 50
    assert xs(demand)[0] == 0
    assert ys(demand)[0] == pytest.approx(50 + 0.5 * 40)
    assert ys(demand)[-1] == pytest.approx(0)
    assert xs(demand)[-1] == pytest.approx(40 + 50 / 2)


def test_限界収入は屈折点で途切れる() -> None:
    ax = kinked()
    upper, lower = (
        line(ax, "Marginal revenue (upper)"),
        line(ax, "Marginal revenue (lower)"),
    )
    assert (xs(upper)[-1], ys(upper)[-1]) == (40, pytest.approx(30))
    assert (xs(lower)[0], ys(lower)[0]) == (40, pytest.approx(-30))
    assert ys(upper)[0] == pytest.approx(70)


def test_途切れの線は屈折点の上下を結ぶ() -> None:
    gap = line(kinked(), "MR gap")
    assert xs(gap) == [40, 40]
    assert ys(gap) == [pytest.approx(-30), pytest.approx(30)]


def test_限界費用は水平線() -> None:
    ax = kinked()
    assert ys(line(ax, "Marginal cost (low)")) == [10, 10]
    assert ys(line(ax, "Marginal cost (high)")) == [25, 25]


def test_屈折需要曲線の図の軸と凡例() -> None:
    ax = kinked()
    assert ax.get_xlim() == (0, 100)
    assert ax.get_ylim() == (-70, 80)
    assert ax.get_xlabel() == "Quantity Q"
    assert ax.get_ylabel() == "Price P"
    assert ax.get_legend() is not None


def test_協調が続く条件の図の線() -> None:
    assert [item.get_label() for item in trigger().lines] == [
        "Cooperate forever",
        "Defect once",
        "Threshold",
    ]


def test_協調と裏切りの価値は閾値で交わる() -> None:
    ax = trigger()
    cooperate, defect = line(ax, "Cooperate forever"), line(ax, "Defect once")
    assert len(xs(cooperate)) == 100
    assert xs(cooperate)[0] == 0
    assert xs(cooperate)[-1] == pytest.approx(0.95)
    for delta, value in zip(xs(cooperate), ys(cooperate), strict=True):
        assert value == pytest.approx(3 / (1 - delta))
    for delta, value in zip(xs(defect), ys(defect), strict=True):
        assert value == pytest.approx(5 + delta * 1 / (1 - delta))
    below = [
        d
        for d, c, f in zip(xs(cooperate), ys(cooperate), ys(defect), strict=True)
        if c < f
    ]
    assert max(below) < 0.5


def test_閾値の点() -> None:
    point = line(trigger(), "Threshold")
    assert xs(point) == [pytest.approx(0.5)]
    assert ys(point) == [pytest.approx(6)]


def test_協調が続く条件の図の軸と凡例() -> None:
    ax = trigger()
    assert ax.get_xlim() == (0, 1)
    assert ax.get_ylim() == (0, 60)
    assert ax.get_xlabel() == "Discount factor"
    assert ax.get_ylabel() == "Present value"
    assert ax.get_legend() is not None
