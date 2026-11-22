"""自然独占の価格規制の図。"""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter11.monopoly import Monopoly, monopoly_outcome
from lib.chapter15.natural import average_cost_pricing, marginal_cost_pricing

_POINTS = 100


def _style(ax: Axes, q_max: float, p_max: float) -> None:
    ax.set_xlabel("Quantity Q")
    ax.set_ylabel("Price P")
    ax.set_xlim(0, q_max)
    ax.set_ylim(0, p_max)
    ax.legend(fontsize="x-small")


def plot_natural_monopoly(
    monopoly: Monopoly, fixed_cost: float, q_max: float, p_max: float
) -> Figure:
    """需要・限界費用・平均費用と、3 つの価格設定（限界費用・平均費用・規制なし）。"""
    a, b, c = monopoly.demand_intercept, monopoly.demand_slope, monopoly.marginal_cost
    qs = [q_max * (i + 1) / _POINTS for i in range(_POINTS)]
    mc = marginal_cost_pricing(monopoly, fixed_cost)
    ac = average_cost_pricing(monopoly, fixed_cost)
    free = monopoly_outcome(monopoly)
    fig, ax = plt.subplots()
    ax.plot([0, a / b], [a, 0], label="Demand")
    ax.plot([0, q_max], [c, c], label="Marginal cost")
    ax.plot(qs, [c + fixed_cost / q for q in qs], label="Average cost")
    ax.plot([mc.quantity], [mc.price], "o", label="MC pricing")
    ax.plot([ac.quantity], [ac.price], "o", label="AC pricing")
    ax.plot([free.quantity], [free.price], "o", label="Unregulated")
    _style(ax, q_max, p_max)
    plt.close(fig)
    return fig
