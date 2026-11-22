"""需要曲線の弾力的・非弾力的な部分の図と、e^x のテイラー近似の図。"""

import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from lib.chapter06.growth import taylor_exp_approximation


def plot_elasticity_regions(a: float, b: float) -> Figure:
    """直線の需要 q = a − b·p を、中点（ε = 1）の上下で塗り分けて描く。"""
    mid_q, mid_p = a / 2, a / (2 * b)
    fig, ax = plt.subplots()
    ax.plot([0, mid_q], [a / b, mid_p], color="tab:red", label="Elastic part (e > 1)")
    ax.plot([mid_q, a], [mid_p, 0], color="tab:blue", label="Inelastic part (e < 1)")
    ax.plot([mid_q], [mid_p], "ko", label="Unit elastic (e = 1)")
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Price")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig


def plot_taylor_exp(
    x_low: float, x_high: float, orders: list[int], x_error: float
) -> Figure:
    """左: e^x と、次数ごとのテイラー近似。右: x_error での誤差を、次数ごとに。"""
    xs = np.linspace(x_low, x_high, 101).tolist()
    fig, (curves, errors) = plt.subplots(1, 2, figsize=(10, 4))
    curves.plot(xs, [math.exp(x) for x in xs], label="e^x")
    for order in orders:
        approx = [taylor_exp_approximation(x, order) for x in xs]
        curves.plot(xs, approx, "--", label=f"Order {order}")
    curves.set_xlabel("x")
    curves.set_ylabel("Value")
    curves.legend(fontsize="x-small")
    degrees = list(range(max(orders) + 1))
    gaps = [
        abs(taylor_exp_approximation(x_error, n) - math.exp(x_error)) for n in degrees
    ]
    errors.plot(degrees, gaps, "o-", label=f"Error at x = {x_error:g}")
    errors.set_yscale("log")
    errors.set_xlabel("Order")
    errors.set_ylabel("Absolute error")
    errors.legend(fontsize="x-small")
    plt.close(fig)
    return fig
