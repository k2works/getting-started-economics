"""第 3 章: 需要曲線と所得消費曲線の図のテスト。"""

from collections.abc import Sequence
from typing import cast

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter03.plot import plot_demand_curve, plot_income_consumption


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_ydata())]


def demand() -> Axes:
    return plot_demand_curve([80, 160], [4, 2, 1, 0.5], 1).axes[0]


def consumption() -> Axes:
    return plot_income_consumption([40, 80, 160], 2, 1).axes[0]


def test_需要曲線の図は所得ごとに1本ずつ() -> None:
    ax = demand()
    assert [line.get_label() for line in ax.lines] == ["Income = 80", "Income = 160"]


def test_需要曲線は横軸が数量で縦軸が価格() -> None:
    ax = demand()
    first = ax.lines[0]
    assert xs(first) == pytest.approx([10, 20, 40, 80])
    assert ys(first) == [4, 2, 1, 0.5]
    assert ax.get_xlabel() == "Quantity of good x"
    assert ax.get_ylabel() == "Price of good x"


def test_需要曲線は右下がり() -> None:
    first = demand().lines[0]
    assert all(a < b for a, b in zip(xs(first), xs(first)[1:], strict=False))
    assert all(a > b for a, b in zip(ys(first), ys(first)[1:], strict=False))


def test_所得が増えると需要曲線は右へ動く() -> None:
    low, high = demand().lines
    assert all(
        h == pytest.approx(2 * lo) for lo, h in zip(xs(low), xs(high), strict=True)
    )
    assert ys(low) == ys(high)


def test_需要曲線の図の軸と凡例() -> None:
    ax = demand()
    assert ax.get_xlim()[0] == 0
    assert ax.get_ylim()[0] == 0
    assert ax.get_legend() is not None


def test_所得消費曲線の図() -> None:
    ax = consumption()
    line = ax.lines[0]
    assert line.get_label() == "Income-consumption curve"
    assert xs(line) == pytest.approx([10, 20, 40])
    assert ys(line) == pytest.approx([20, 40, 80])
    assert ax.get_xlabel() == "Good x"
    assert ax.get_ylabel() == "Good y"
    assert ax.get_xlim()[0] == 0
    assert ax.get_ylim()[0] == 0
    assert ax.get_legend() is not None
