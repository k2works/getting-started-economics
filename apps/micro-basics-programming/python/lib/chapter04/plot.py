"""スルツキー分解と、交差価格効果の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter01.utility import cobb_douglas_utility, indifference_curve_y
from lib.chapter02.budget import budget_intercepts
from lib.chapter04.slutsky import (
    demand_perfect_complements,
    demand_perfect_substitutes,
    slutsky_decomposition,
)

_POINTS = 50


def _style(ax: Axes) -> None:
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize="x-small")


def plot_slutsky(
    income: float, px_old: float, px_new: float, py: float, x_max: float
) -> Figure:
    """スルツキー分解の 3 点（A・B・C）を、無差別曲線と予算線に重ねて描く。

    A（元の点）から B（代替効果のあと）は、同じ無差別曲線の上の動き。
    B から C（最終）は、予算線の平行移動（所得効果）。
    """
    result = slutsky_decomposition(income, px_old, px_new, py)
    level_a = cobb_douglas_utility(*result.original)
    level_c = cobb_douglas_utility(*result.final)
    step = x_max / _POINTS
    xs = [step * (i + 1) for i in range(_POINTS)]
    fig, ax = plt.subplots()
    for name, level in (("U0", level_a), ("U1", level_c)):
        ax.plot(
            xs,
            [indifference_curve_y(level, x) for x in xs],
            label=f"{name} = {level:g}",
        )
    for label, price in (("Original budget", px_old), ("New budget", px_new)):
        x_intercept, y_intercept = budget_intercepts(income, price, py)
        ax.plot([0, x_intercept], [y_intercept, 0], label=label)
    x_b, y_b = result.substitution
    spend = px_new * x_b + py * y_b
    x_intercept, y_intercept = budget_intercepts(spend, px_new, py)
    ax.plot(
        [0, x_intercept],
        [y_intercept, 0],
        "--",
        label="Compensated budget (after income adjustment)",
    )
    for label, point in (
        ("A: original", result.original),
        ("B: after substitution effect", result.substitution),
        ("C: after income effect", result.final),
    ):
        ax.plot([point[0]], [point[1]], "o", label=label)
    ax.set_xlabel("Good x")
    ax.set_ylabel("Good y")
    _style(ax)
    # 無差別曲線は x が小さいと立ち上がるので、元の予算線の y 切片の 1.5 倍までを見せる
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, 1.5 * income / py)
    plt.close(fig)
    return fig


def plot_cross_price(income: float, px: float, py_values: Sequence[float]) -> Figure:
    """財 y の価格を動かしたときの、財 x の需要。代替財は増え、補完財は減る。"""
    fig, ax = plt.subplots()
    ax.plot(
        list(py_values),
        [demand_perfect_substitutes(income, px, py) for py in py_values],
        label="Perfect substitutes",
    )
    ax.plot(
        list(py_values),
        [demand_perfect_complements(income, px, py) for py in py_values],
        label="Perfect complements",
    )
    ax.set_xlabel("Price of good y")
    ax.set_ylabel("Demand for good x")
    _style(ax)
    plt.close(fig)
    return fig
