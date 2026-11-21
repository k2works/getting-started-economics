"""第 7 章: 供給曲線と課税の図のテスト。"""

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
)
from lib.chapter07.plot import plot_supply, plot_tax_supply

CURVE = CostCurve(1, -6, 15, 32)


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_ydata())]


def line(ax: Axes, label: str) -> Line2D:
    return next(item for item in ax.lines if item.get_label() == label)


def supply() -> Axes:
    return plot_supply(CURVE, 30, 8, 40).axes[0]


def tax() -> Axes:
    return plot_tax_supply(CURVE, 6, 0.2, 3, 6).axes[0]


def test_供給曲線の図の線() -> None:
    assert [item.get_label() for item in supply().lines] == [
        "AC",
        "AVC",
        "MC",
        "Supply curve (MC above shutdown)",
        "Price",
        "Profit rectangle",
        "Profit-maximizing point",
        "Break-even point",
        "Shutdown point",
    ]


def test_曲線は100点で値は費用関数と一致する() -> None:
    ax = supply()
    for label, function in (
        ("AC", average_cost),
        ("AVC", average_variable_cost),
        ("MC", marginal_cost),
    ):
        item = line(ax, label)
        assert len(xs(item)) == 100
        for q, value in zip(xs(item), ys(item), strict=True):
            assert value == pytest.approx(function(CURVE, q))
    assert xs(line(ax, "MC"))[0] == pytest.approx(8 / 100)
    assert xs(line(ax, "MC"))[-1] == pytest.approx(8)


def test_供給曲線は操業停止点より上の限界費用() -> None:
    item = line(supply(), "Supply curve (MC above shutdown)")
    assert xs(item)[0] >= 3 - 1e-9
    assert xs(item)[-1] == pytest.approx(8)
    for q, value in zip(xs(item), ys(item), strict=True):
        assert value == pytest.approx(marginal_cost(CURVE, q))
        assert value >= 6 - 1e-9


def test_価格の線は水平() -> None:
    item = line(supply(), "Price")
    assert xs(item) == [0, 8]
    assert ys(item) == [30, 30]


def test_利潤の長方形の面積は利潤() -> None:
    item = line(supply(), "Profit rectangle")
    assert len(xs(item)) == 5
    width = xs(item)[1] - xs(item)[0]
    height = ys(item)[0] - ys(item)[2]
    assert width == pytest.approx(5)
    assert width * height == pytest.approx(68)
    assert xs(item)[0] == xs(item)[3] == xs(item)[4] == 0
    assert ys(item)[0] == ys(item)[1] == ys(item)[4] == 30


def test_3つの点() -> None:
    ax = supply()
    best = line(ax, "Profit-maximizing point")
    assert (xs(best)[0], ys(best)[0]) == pytest.approx((5, 30))
    even = line(ax, "Break-even point")
    assert (xs(even)[0], ys(even)[0]) == pytest.approx((4, 15), abs=1e-3)
    shut = line(ax, "Shutdown point")
    assert (xs(shut)[0], ys(shut)[0]) == pytest.approx((3, 6), abs=1e-3)


def test_供給曲線の図の軸と凡例() -> None:
    ax = supply()
    assert ax.get_xlabel() == "Quantity q"
    assert ax.get_ylabel() == "Price and cost per unit"
    assert ax.get_xlim() == (0, 8)
    assert ax.get_ylim() == (0, 40)
    assert ax.get_legend() is not None


def test_課税の図の線() -> None:
    assert [item.get_label() for item in tax().lines] == [
        "Supply",
        "Supply after unit tax",
        "Supply after ad valorem tax",
    ]


def test_課税の図は50点で左端は操業停止点の生産量() -> None:
    ax = tax()
    for item in ax.lines:
        assert len(xs(item)) == 50
        assert xs(item)[0] == pytest.approx(3)
        assert xs(item)[-1] == pytest.approx(6)


def test_従量税は税額だけ上に平行移動する() -> None:
    ax = tax()
    base, unit = ys(line(ax, "Supply")), ys(line(ax, "Supply after unit tax"))
    assert base[0] == pytest.approx(6)
    assert all(u - b == pytest.approx(6) for b, u in zip(base, unit, strict=True))


def test_従価税は上乗せが生産量とともに大きくなる() -> None:
    ax = tax()
    base = ys(line(ax, "Supply"))
    ad = ys(line(ax, "Supply after ad valorem tax"))
    gaps = [a - b for b, a in zip(base, ad, strict=True)]
    assert gaps[0] == pytest.approx(1.5)
    assert all(a < b for a, b in zip(gaps, gaps[1:], strict=False))
    assert ad == pytest.approx([b / 0.8 for b in base])


def test_課税後の曲線は点線() -> None:
    ax = tax()
    assert line(ax, "Supply after unit tax").get_linestyle() == "--"
    assert line(ax, "Supply after ad valorem tax").get_linestyle() == "--"
    assert line(ax, "Supply").get_linestyle() == "-"


def test_課税の図の軸と凡例() -> None:
    ax = tax()
    assert ax.get_xlabel() == "Quantity q"
    assert ax.get_ylabel() == "Price"
    assert ax.get_xlim() == (3, 6)
    assert ax.get_ylim()[0] == 0
    assert ax.get_legend() is not None
