import numpy as np
import pytest
from matplotlib.axes import Axes

from lib.chapter05.cost import average_cost, average_variable_cost, marginal_cost
from lib.chapter05.derivative import Polynomial, difference_quotient_errors
from lib.chapter05.plot import plot_cost_curves, plot_derivative_errors


def _line(ax: Axes, label: str) -> tuple[list[float], list[float]]:
    line = next(x for x in ax.lines if x.get_label() == label)
    xs = np.asarray(line.get_xdata(), dtype=float).tolist()
    ys = np.asarray(line.get_ydata(), dtype=float).tolist()
    return xs, ys


def test_費用曲線の各点は限界費用と平均費用の値() -> None:
    cost = Polynomial((50, 4, 0.5))
    ax = plot_cost_curves(cost, 20, 30).axes[0]
    for label, curve in [
        ("Marginal cost (MC)", marginal_cost),
        ("Average cost (AC)", average_cost),
        ("Average variable cost (AVC)", average_variable_cost),
    ]:
        xs, ys = _line(ax, label)
        assert (xs[0], xs[-1]) == pytest.approx((0.3, 30))
        assert ys == pytest.approx([curve(cost, q) for q in xs])
    assert (ax.get_xlabel(), ax.get_ylabel()) == ("Quantity", "Cost / Price")
    assert ax.get_legend() is not None
    assert (ax.get_xlim()[0], ax.get_ylim()) == (0, (0, 40))


def test_利潤最大の点と利潤の長方形() -> None:
    ax = plot_cost_curves(Polynomial((100, 10, 1)), 50, 30).axes[0]
    assert _line(ax, "Price") == ([0, 30], [50, 50])
    assert _line(ax, "Profit maximum (P = MC)") == ([20], [50])
    assert _line(ax, "Minimum AC (MC = AC)") == ([10], [30])
    # 長方形の高さは P − AC(20) = 50 − 35、幅は 20。面積は利潤 300
    box = ax.collections[0].get_paths()[0].get_extents()
    assert (box.x0, box.x1, box.y0, box.y1) == pytest.approx((0, 20, 35, 50))
    assert ax.collections[0].get_label() == "Profit"


def test_誤差の図は刻み幅ごとの誤差を両対数で描く() -> None:
    cube = Polynomial((0, 0, 0, 1))
    steps = [10.0**-k for k in range(1, 15)]
    ax = plot_derivative_errors(cube, 3, 1, steps).axes[0]
    xs, ys = _line(ax, "Central difference error")
    assert xs == steps
    assert ys == pytest.approx(difference_quotient_errors(cube, 3, 1, steps))
    assert (ax.get_xscale(), ax.get_yscale()) == ("log", "log")
    assert (ax.get_xlabel(), ax.get_ylabel()) == ("Step size h", "Absolute error")
    assert ax.get_legend() is not None
