import math

import numpy as np
import pytest
from matplotlib.axes import Axes

from lib.chapter06.elasticity import linear_demand_elasticity
from lib.chapter06.growth import taylor_exp_approximation
from lib.chapter06.plot import plot_elasticity_regions, plot_taylor_exp


def _line(ax: Axes, label: str) -> tuple[list[float], list[float]]:
    line = next(x for x in ax.lines if x.get_label() == label)
    xs = np.asarray(line.get_xdata(), dtype=float).tolist()
    ys = np.asarray(line.get_ydata(), dtype=float).tolist()
    return xs, ys


def test_需要曲線は中点を境に弾力的な部分と非弾力的な部分に分かれる() -> None:
    ax = plot_elasticity_regions(100, 2).axes[0]
    assert _line(ax, "Elastic part (e > 1)") == ([0, 50], [50, 25])
    assert _line(ax, "Inelastic part (e < 1)") == ([50, 100], [25, 0])
    assert _line(ax, "Unit elastic (e = 1)") == ([50], [25])
    assert linear_demand_elasticity(25, 100, 2) == 1
    assert (ax.get_xlabel(), ax.get_ylabel()) == ("Quantity", "Price")
    assert ax.get_legend() is not None
    assert (ax.get_xlim()[0], ax.get_ylim()[0]) == (0, 0)


def test_テイラー近似の図は次数ごとの近似とeのx乗を描く() -> None:
    curves = plot_taylor_exp(-2, 2, [1, 2, 3], 1).axes[0]
    xs, ys = _line(curves, "e^x")
    assert (xs[0], xs[-1]) == pytest.approx((-2, 2))
    assert ys == pytest.approx([math.exp(x) for x in xs])
    for order in [1, 2, 3]:
        line = next(x for x in curves.lines if x.get_label() == f"Order {order}")
        assert line.get_linestyle() == "--"
        xs, ys = _line(curves, f"Order {order}")
        assert ys == pytest.approx([taylor_exp_approximation(x, order) for x in xs])
    assert curves.get_legend() is not None


def test_誤差の図は次数ごとの誤差を対数目盛で描く() -> None:
    _, errors = plot_taylor_exp(-2, 2, [1, 2, 3], 1).axes
    orders, values = _line(errors, "Error at x = 1")
    assert orders == [0, 1, 2, 3]
    expected = [abs(taylor_exp_approximation(1, n) - math.e) for n in range(4)]
    assert values == pytest.approx(expected)
    assert errors.get_yscale() == "log"
    assert (errors.get_xlabel(), errors.get_ylabel()) == ("Order", "Absolute error")
    assert errors.get_legend() is not None
