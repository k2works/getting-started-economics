"""予算線と最適消費点の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter01.utility import indifference_curve_y
from lib.chapter02.budget import budget_intercepts, optimal_bundle

_POINTS = 50


def _style(ax: Axes, y_top: float) -> None:
    ax.set_xlabel("Good x")
    ax.set_ylabel("Good y")
    ax.set_xlim(left=0)
    # 無差別曲線は、x が小さいと、立ち上がるので、予算線の y 切片の 1.5 倍までを見せる
    ax.set_ylim(0, 1.5 * y_top)
    ax.legend(fontsize="x-small")


def plot_optimal_choice(
    income: float, px: float, py: float, levels: Sequence[float], x_max: float
) -> Figure:
    """無差別曲線と予算線を重ね、接する点（最適消費点）に印をつける。"""
    step = x_max / _POINTS
    xs = [step * (i + 1) for i in range(_POINTS)]
    fig, ax = plt.subplots()
    for level in levels:
        ax.plot(xs, [indifference_curve_y(level, x) for x in xs], label=f"U = {level}")
    x_intercept, y_intercept = budget_intercepts(income, px, py)
    ax.plot([0, x_intercept], [y_intercept, 0], label="Budget line")
    x, y = optimal_bundle(income, px, py)
    ax.plot([x], [y], "o", label="Optimum")
    _style(ax, y_intercept)
    plt.close(fig)
    return fig


def plot_price_change(income: float, prices: Sequence[float], py: float) -> Figure:
    """価格が下がると、予算線の x 切片だけが右へ動く。最適点をつなぐと価格消費曲線。"""
    fig, ax = plt.subplots()
    bundles = []
    y_intercept = income / py
    for price in prices:
        x_intercept, y_intercept = budget_intercepts(income, price, py)
        ax.plot([0, x_intercept], [y_intercept, 0], label=f"Px = {price}")
        bundles.append(optimal_bundle(income, price, py))
    ax.plot(
        [x for x, _ in bundles],
        [y for _, y in bundles],
        "o-",
        label="Price-consumption curve",
    )
    _style(ax, y_intercept)
    plt.close(fig)
    return fig
