"""無差別曲線と予算線の接点（効用最大化）と、所得を変えたときの最適点の軌跡の図。"""

from collections.abc import Callable, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter07.budget import budget_intercepts
from lib.chapter07.vectors import vector_length
from lib.chapter08.utility import (
    cobb_douglas_demand,
    cobb_douglas_indifference_y,
    cobb_douglas_marginal_utilities,
    cobb_douglas_utility,
    quasilinear_demand,
)


def _plot_indifference(
    ax: Axes, level: float, share: float, x_end: float, style: str, label: str
) -> None:
    """効用が level の無差別曲線を、x = x_end ÷ 20 から x_end まで描く。"""
    xs = np.linspace(x_end / 20, x_end, 200)
    ys = [cobb_douglas_indifference_y(level, float(x), share) for x in xs]
    ax.plot(xs, ys, style, color="C2", label=label)


def _plot_gradient(
    ax: Axes, optimum: tuple[float, float], share: float, length: float
) -> None:
    """最適点から、効用の勾配 (U_x, U_y) の向きに、長さ length の矢印を描く。"""
    x, y = optimum
    gradient = cobb_douglas_marginal_utilities(x, y, share)
    scale = length / vector_length(list(gradient))
    end = (x + scale * gradient[0], y + scale * gradient[1])
    ax.plot(
        [x, end[0]],
        [y, end[1]],
        color="C3",
        label="Gradient of U (same direction as prices)",
    )
    ax.annotate(
        "", xy=end, xytext=optimum, arrowprops={"arrowstyle": "->", "color": "C3"}
    )


def plot_utility_maximization(
    prices: Sequence[float], income: float, share: float
) -> Figure:
    """予算線・最適点を通る無差別曲線・効用の低い無差別曲線・効用の勾配を描く。"""
    x_end, y_end = budget_intercepts(prices, income)
    optimum = cobb_douglas_demand(prices, income, share)
    level = cobb_douglas_utility(*optimum, share)
    fig, ax = plt.subplots()
    ax.plot([0, x_end], [y_end, 0], color="C0", label="Budget line")
    right = 1.1 * x_end
    _plot_indifference(
        ax, level, share, right, "-", f"Indifference curve (U = {level:.2f})"
    )
    _plot_indifference(
        ax, 0.7 * level, share, right, ":", "Indifference curve (lower utility)"
    )
    _plot_gradient(ax, optimum, share, min(x_end, y_end) / 4)
    ax.plot([optimum[0]], [optimum[1]], "ko", label="Optimum")
    ax.set_xlim(0, right)
    ax.set_ylim(0, 1.5 * y_end)
    ax.set_xlabel("Good x")
    ax.set_ylabel("Good y")
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig


def _plot_expansion(
    ax: Axes,
    demand: Callable[[float], tuple[float, float]],
    prices: Sequence[float],
    incomes: Sequence[float],
) -> None:
    labels = [f"Budget (income {incomes[0]:g})", "Budget after income rise"]
    for i, income in enumerate(incomes):
        x_end, y_end = budget_intercepts(prices, income)
        # 3 本目からの予算線は、凡例に重ねて載せない
        label = labels[i] if i < len(labels) else "_nolegend_"
        ax.plot(
            [0, x_end], [y_end, 0], "-" if i == 0 else "--", color="C0", label=label
        )
    bundles = [demand(income) for income in incomes]
    ax.plot(
        [b[0] for b in bundles],
        [b[1] for b in bundles],
        "o-",
        color="C3",
        label="Optimal bundles",
    )
    ax.set_xlabel("Good x")
    ax.set_ylabel("Good y")
    ax.legend(fontsize="x-small")


def plot_income_expansion_paths(
    prices: Sequence[float], incomes: Sequence[float], share: float, weight: float
) -> Figure:
    """所得を変えたときの最適点の軌跡。左はコブ・ダグラス型、右は準線形効用。"""
    if not incomes:
        raise ValueError("所得を 1 つ以上与えてください")
    fig, (left, right) = plt.subplots(1, 2, figsize=(10, 4.5))
    _plot_expansion(
        left, lambda m: cobb_douglas_demand(prices, m, share), prices, incomes
    )
    left.set_title(f"Cobb-Douglas (a = {share:g})")
    _plot_expansion(
        right, lambda m: quasilinear_demand(prices, m, weight), prices, incomes
    )
    right.set_title(f"Quasi-linear (U = {weight:g}√x + y)")
    plt.close(fig)
    return fig
