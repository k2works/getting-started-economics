"""外部不経済（死荷重の三角形）と、自然独占の価格規制の図。"""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter09.plot import outline_area
from lib.chapter11.monopoly import Monopoly, monopoly_outcome
from lib.chapter13.externality import (
    ExternalityMarket,
    market_quantity,
    socially_optimal_quantity,
)
from lib.chapter13.natural import average_cost_pricing, marginal_cost_pricing

_POINTS = 100


def _style(ax: Axes, q_max: float, p_max: float) -> None:
    ax.set_xlabel("Quantity Q")
    ax.set_ylabel("Price P")
    ax.set_xlim(0, q_max)
    ax.set_ylim(0, p_max)
    ax.legend(fontsize="x-small")


def plot_externality(market: ExternalityMarket, q_max: float, p_max: float) -> Figure:
    """需要・私的限界費用・社会的限界費用（点線）と、死荷重の三角形を描く。"""
    a, b = market.demand_intercept, market.demand_slope
    c, d, e = market.cost_intercept, market.cost_slope, market.external_cost
    q_market, q_opt = market_quantity(market), socially_optimal_quantity(market)
    fig, ax = plt.subplots()
    ax.plot([0, a / b], [a, 0], label="Demand")
    ax.plot([0, q_max], [c, c + d * q_max], label="Private marginal cost")
    ax.plot(
        [0, q_max],
        [c + e, c + e + d * q_max],
        linestyle="--",
        label="Social marginal cost",
    )
    outline_area(
        ax,
        [q_opt, q_market, q_market, q_opt],
        [a - b * q_opt, a - b * q_market, c + d * q_market + e, a - b * q_opt],
        "Deadweight loss",
    )
    ax.plot([q_market], [a - b * q_market], "o", label="Market point")
    ax.plot([q_opt], [a - b * q_opt], "o", label="Optimal point")
    _style(ax, q_max, p_max)
    plt.close(fig)
    return fig


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
