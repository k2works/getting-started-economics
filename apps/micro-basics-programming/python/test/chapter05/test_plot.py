"""第 5 章: 費用曲線の図のテスト。"""

from collections.abc import Sequence
from typing import cast

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter05.cost import (
    CostCurve,
    average_cost,
    average_variable_cost,
    marginal_cost,
    total_cost,
    variable_cost,
)
from lib.chapter05.plot import plot_cost_curves, plot_total_cost

CURVE = CostCurve(1, -6, 15, 32)


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_ydata())]


def line(ax: Axes, label: str) -> Line2D:
    return next(item for item in ax.lines if item.get_label() == label)


def unit() -> Axes:
    return plot_cost_curves(CURVE, 8, 40).axes[0]


def totals() -> Axes:
    return plot_total_cost(CURVE, 8).axes[0]


def test_費用曲線の図の線() -> None:
    assert [item.get_label() for item in unit().lines] == [
        "MC",
        "AC",
        "AVC",
        "Minimum of MC",
        "Minimum of AVC",
        "Minimum of AC",
    ]


def test_曲線は100点で左端は上限の100分の1() -> None:
    mc = line(unit(), "MC")
    assert len(xs(mc)) == 100
    assert xs(mc)[0] == pytest.approx(8 / 100)
    assert xs(mc)[-1] == pytest.approx(8)


def test_曲線の値は費用関数と一致する() -> None:
    ax = unit()
    for label, function in (
        ("MC", marginal_cost),
        ("AC", average_cost),
        ("AVC", average_variable_cost),
    ):
        item = line(ax, label)
        for q, value in zip(xs(item), ys(item), strict=True):
            assert value == pytest.approx(function(CURVE, q))


def test_最低点の印は3本の最低点() -> None:
    ax = unit()
    for label, (q, value) in (
        ("Minimum of MC", (2, 3)),
        ("Minimum of AVC", (3, 6)),
        ("Minimum of AC", (4, 15)),
    ):
        point = line(ax, label)
        assert xs(point) == pytest.approx([q], abs=1e-3)
        assert ys(point) == pytest.approx([value], abs=1e-2)


def test_平均費用は平均可変費用より上() -> None:
    ax = unit()
    ac, avc = ys(line(ax, "AC")), ys(line(ax, "AVC"))
    assert all(a > b for a, b in zip(ac, avc, strict=True))


def test_費用曲線の図の軸と凡例() -> None:
    ax = unit()
    assert ax.get_xlabel() == "Quantity q"
    assert ax.get_ylabel() == "Cost per unit"
    assert ax.get_xlim() == (0, 8)
    assert ax.get_ylim() == (0, 40)
    assert ax.get_legend() is not None


def test_総費用の図の線() -> None:
    assert [item.get_label() for item in totals().lines] == [
        "Total cost",
        "Variable cost",
        "Fixed cost",
    ]


def test_総費用は可変費用と固定費用の和() -> None:
    ax = totals()
    for q, tc, vc, fc in zip(
        xs(line(ax, "Total cost")),
        ys(line(ax, "Total cost")),
        ys(line(ax, "Variable cost")),
        ys(line(ax, "Fixed cost")),
        strict=True,
    ):
        assert tc == pytest.approx(total_cost(CURVE, q))
        assert vc == pytest.approx(variable_cost(CURVE, q))
        assert tc == pytest.approx(vc + fc)
        assert fc == 32


def test_総費用の図の軸と凡例() -> None:
    ax = totals()
    assert ax.get_xlabel() == "Quantity q"
    assert ax.get_ylabel() == "Cost"
    assert ax.get_xlim()[0] == 0
    assert ax.get_ylim()[0] == 0
    assert ax.get_legend() is not None
