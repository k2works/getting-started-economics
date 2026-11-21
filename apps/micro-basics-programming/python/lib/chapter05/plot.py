"""費用曲線の図。"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from lib.chapter05.cost import (
    CostCurve,
    average_cost,
    average_variable_cost,
    cost_minima,
    marginal_cost,
    total_cost,
    variable_cost,
)

_POINTS = 100


def _grid(q_max: float) -> list[float]:
    """q_max の 100 分の 1 から q_max までを、100 点に等分する（q = 0 は、除く）。"""
    return [float(q) for q in np.linspace(q_max / _POINTS, q_max, _POINTS)]


def plot_cost_curves(curve: CostCurve, q_max: float, y_max: float) -> Figure:
    """MC・AC・AVC の 3 本と、最低点を描く。MC は、AVC と AC の最低点を通る。"""
    qs = _grid(q_max)
    fig, ax = plt.subplots()
    ax.plot(qs, [marginal_cost(curve, q) for q in qs], label="MC")
    ax.plot(qs, [average_cost(curve, q) for q in qs], label="AC")
    ax.plot(qs, [average_variable_cost(curve, q) for q in qs], label="AVC")
    minima = cost_minima(curve, q_max)
    for name in ("MC", "AVC", "AC"):
        q, value = minima[name]
        ax.plot([q], [value], "o", label=f"Minimum of {name}")
    ax.set_xlabel("Quantity q")
    ax.set_ylabel("Cost per unit")
    ax.set_xlim(0, q_max)
    ax.set_ylim(0, y_max)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig


def plot_total_cost(curve: CostCurve, q_max: float) -> Figure:
    """総費用・可変費用・固定費用を描く。総費用 = 可変費用 + 固定費用（逆 S 字）。"""
    qs = _grid(q_max)
    fig, ax = plt.subplots()
    ax.plot(qs, [total_cost(curve, q) for q in qs], label="Total cost")
    ax.plot(qs, [variable_cost(curve, q) for q in qs], label="Variable cost")
    ax.plot(qs, [curve.fixed for _ in qs], label="Fixed cost")
    ax.set_xlabel("Quantity q")
    ax.set_ylabel("Cost")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig
