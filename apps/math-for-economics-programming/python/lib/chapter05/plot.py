"""費用曲線（MC・AC・AVC）と利潤最大点の図、数値微分の刻み幅と誤差の図。"""

from collections.abc import Callable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from lib.chapter05.cost import (
    average_cost,
    average_variable_cost,
    marginal_cost,
    minimum_average_cost,
    profit_maximizing_quantity,
)
from lib.chapter05.derivative import Polynomial, difference_quotient_errors


def plot_cost_curves(cost: Polynomial, price: float, q_max: float) -> Figure:
    """2 次の費用の MC・AC・AVC と価格の線。P = MC の点と、利潤の長方形を描く。"""
    quantities = np.linspace(q_max / 100, q_max, 100).tolist()
    best = profit_maximizing_quantity(price, cost)
    low_q, low_ac = minimum_average_cost(cost)
    fig, ax = plt.subplots()
    if best > 0:  # 操業停止点より安ければ作らないので、利潤の長方形はない
        ax.fill_between(
            [0, best], average_cost(cost, best), price, alpha=0.2, label="Profit"
        )
    curves = [
        ("Marginal cost (MC)", marginal_cost),
        ("Average cost (AC)", average_cost),
        ("Average variable cost (AVC)", average_variable_cost),
    ]
    for label, curve in curves:
        ax.plot(quantities, [curve(cost, q) for q in quantities], label=label)
    ax.plot([0, q_max], [price, price], "--", label="Price")
    if best > 0:
        ax.plot([best], [price], "ko", label="Profit maximum (P = MC)")
    ax.plot([low_q], [low_ac], "s", label="Minimum AC")
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Cost / Price")
    ax.set_xlim(left=0)
    ax.set_ylim(0, 2 * price)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig


def plot_derivative_errors(
    func: Callable[[float], float], exact_slope: float, x: float, steps: list[float]
) -> Figure:
    """刻み幅 h ごとの、中心差分の誤差を、両対数目盛で描く。"""
    errors = difference_quotient_errors(func, exact_slope, x, steps)
    fig, ax = plt.subplots()
    ax.plot(steps, errors, "o-", label="Central difference error")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Step size h")
    ax.set_ylabel("Absolute error")
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig
