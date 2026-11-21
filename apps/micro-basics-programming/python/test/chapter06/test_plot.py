"""第 6 章: 費用最小化の図のテスト。"""

from collections.abc import Sequence
from typing import cast

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter06.plot import plot_cost_minimization, plot_marginal_product
from lib.chapter06.production import marginal_product_labor, production


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in cast(Sequence[float], line.get_ydata())]


def line(ax: Axes, label: str) -> Line2D:
    return next(item for item in ax.lines if item.get_label() == label)


def minimization() -> Axes:
    return plot_cost_minimization([5, 10, 15], 10, 1, 4).axes[0]


def marginal() -> Axes:
    return plot_marginal_product(5, 80).axes[0]


def test_費用最小化の図の線() -> None:
    assert [item.get_label() for item in minimization().lines] == [
        "q = 5",
        "q = 10",
        "q = 15",
        "Isocost (cost = 40)",
        "Optimum",
    ]


def test_等産出量曲線の上の点は生産量が水準と等しい() -> None:
    ax = minimization()
    for level in (5, 10, 15):
        item = line(ax, f"q = {level}")
        for labor, capital in zip(xs(item), ys(item), strict=True):
            assert production(labor, capital) == pytest.approx(level)


def test_等産出量曲線は50点で右端は等費用線のL切片() -> None:
    item = line(minimization(), "q = 10")
    assert len(xs(item)) == 50
    assert xs(item)[0] == pytest.approx(40 / 50)
    assert xs(item)[-1] == pytest.approx(40)


def test_等費用線の両端は切片() -> None:
    item = line(minimization(), "Isocost (cost = 40)")
    assert xs(item) == [0, 40]
    assert ys(item) == [10, 0]


def test_最適点は費用最小の投入() -> None:
    point = line(minimization(), "Optimum")
    assert xs(point) == pytest.approx([20])
    assert ys(point) == pytest.approx([5])


def test_費用最小化の図の軸と凡例() -> None:
    ax = minimization()
    assert ax.get_xlabel() == "Labor L"
    assert ax.get_ylabel() == "Capital K"
    assert ax.get_xlim() == (0, 40)
    assert ax.get_ylim() == (0, 15)
    assert ax.get_legend() is not None


def test_資本の価格が1でないとき() -> None:
    ax = plot_cost_minimization([10], 10, 4, 1).axes[0]
    assert ax.get_xlim() == (0, 10)
    assert ax.get_ylim() == (0, 60)
    point = line(ax, "Optimum")
    assert xs(point) == pytest.approx([5])
    assert ys(point) == pytest.approx([20])


def test_限界生産性の図は逓減する() -> None:
    item = line(marginal(), "MPL (K = 5)")
    assert len(xs(item)) == 50
    assert xs(item)[0] == pytest.approx(80 / 50)
    assert xs(item)[-1] == pytest.approx(80)
    for labor, value in zip(xs(item), ys(item), strict=True):
        assert value == pytest.approx(marginal_product_labor(labor, 5))
    assert all(a > b for a, b in zip(ys(item), ys(item)[1:], strict=False))


def test_限界生産性の図の軸と凡例() -> None:
    ax = marginal()
    assert ax.get_xlabel() == "Labor L"
    assert ax.get_ylabel() == "Marginal product of labor"
    assert ax.get_xlim()[0] == 0
    assert ax.get_ylim()[0] == 0
    assert ax.get_legend() is not None
