import math

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes

from lib.chapter11.auction import (
    expected_auction_revenue_formula,
    simulate_auction_revenues,
)
from lib.chapter11.integral import (
    midpoint_rule_integral,
    quadrature_errors,
    trapezoid_rule_integral,
)
from lib.chapter11.plot import (
    plot_auction_revenues,
    plot_integration_errors,
    plot_uniform_distribution,
)


def _series(ax: Axes, label: str) -> tuple[list[float], list[float]]:
    line = next(x for x in ax.lines if x.get_label() == label)
    xs = np.asarray(line.get_xdata(), dtype=float).tolist()
    ys = np.asarray(line.get_ydata(), dtype=float).tolist()
    return xs, ys


def test_分布の図は密度の下の面積と分布関数の差で同じ確率を示す() -> None:
    density_ax, cdf_ax = plot_uniform_distribution(2, 6, 3, 5).axes
    xs, ys = _series(density_ax, "Density f(x)")
    assert (xs[0], xs[-1]) == (0, 8)
    assert ys == pytest.approx([0.25 if 2 <= x <= 6 else 0 for x in xs])
    (area,) = density_ax.collections
    assert area.get_label() == "P(3 <= X <= 5) = 0.50"
    corners = np.asarray(area.get_paths()[0].vertices, dtype=float)
    assert (corners[:, 0].min(), corners[:, 0].max()) == pytest.approx((3, 5))
    assert (corners[:, 1].min(), corners[:, 1].max()) == pytest.approx((0, 0.25))
    xs, ys = _series(cdf_ax, "Distribution function F(x)")
    assert ys == pytest.approx([min(max((x - 2) / 4, 0), 1) for x in xs])
    assert _series(cdf_ax, "F(5) - F(3)") == ([5, 5], [0.25, 0.75])
    # 凡例が線に重ならないよう、縦軸の上に余白がある
    assert density_ax.get_ylim()[1] > 0.3 and cdf_ax.get_ylim()[1] > 1.2
    for ax in (density_ax, cdf_ax):
        assert ax.get_xlabel() == "Value x"
        assert ax.get_legend() is not None
    plt.close("all")


def test_オークションの図は2つの方式の収入の分布と公式の平均() -> None:
    ax = plot_auction_revenues(2, 2000, seed=3).axes[0]
    first, second = ax.containers
    # ヒストグラムの名前は、最初の棒に付く
    assert first[0].get_label() == "First-price revenue"
    assert second[0].get_label() == "Second-price revenue"
    heights = [b.get_height() for b in first]
    expected, _ = np.histogram(
        simulate_auction_revenues(2, 2000, seed=3, rule="first"),
        bins=np.linspace(0, 1, 41),
        density=True,
    )
    assert heights == pytest.approx(expected.tolist())
    tallest = max(b.get_height() for bars in ax.containers for b in bars)
    assert ax.get_ylim()[1] > tallest * 1.2
    mean = float(expected_auction_revenue_formula(2))
    xs, _ = _series(ax, "Expected revenue (n - 1)/(n + 1) = 0.333")
    assert xs == pytest.approx([mean, mean])
    assert ax.get_xlabel() == "Seller's revenue"
    assert ax.get_legend() is not None
    plt.close("all")


def test_誤差の図は分割数と誤差を両対数で描く() -> None:
    pieces = [2, 4, 8, 16]
    ax = plot_integration_errors(math.exp, math.e - 1, 0, 1, pieces).axes[0]
    for label, rule in [
        ("Midpoint rule", midpoint_rule_integral),
        ("Trapezoid rule", trapezoid_rule_integral),
    ]:
        xs, ys = _series(ax, label)
        assert xs == pieces
        assert ys == pytest.approx(
            quadrature_errors(rule, math.exp, math.e - 1, 0, 1, pieces)
        )
    xs, ys = _series(ax, "Slope of 1/n^2")
    assert xs == pieces
    # 台形法の最初の点から始まり、n を 2 倍にするたびに 1/4 になる
    assert ys[0] == _series(ax, "Trapezoid rule")[1][0]
    assert [y * n**2 for y, n in zip(ys, xs, strict=True)] == pytest.approx(
        [ys[0] * 4] * 4
    )
    assert ax.get_xscale() == "log" and ax.get_yscale() == "log"
    assert ax.get_xlabel() == "Number of pieces n"
    assert ax.get_legend() is not None
    plt.close("all")
