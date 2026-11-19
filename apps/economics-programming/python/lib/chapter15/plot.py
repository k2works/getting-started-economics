"""独占の図。縦軸が価格、横軸が数量。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Polygon, Rectangle

from lib.chapter01.demand import choke_price
from lib.chapter07.surplus import inverse_demand
from lib.chapter15.monopoly import (
    competitive_quantity,
    marginal_revenue,
    monopoly_outcome,
)


def plot_monopoly(
    demand_intercept: float, demand_slope: float, marginal_cost: float
) -> Figure:
    """需要曲線・限界収入・限界費用と、独占点・競争点、利潤と死荷重を描いた図を返す。

    利潤は、独占の数量と、価格と限界費用の差でできる長方形。
    死荷重は、独占の数量から競争の数量までの、三角形。
    """
    outcome = monopoly_outcome(demand_intercept, demand_slope, marginal_cost)
    competitive = competitive_quantity(demand_intercept, demand_slope, marginal_cost)
    quantities = [float(q) for q in range(int(demand_intercept) + 1)]

    fig, ax = plt.subplots()
    ax.add_patch(
        Rectangle(
            (0, marginal_cost),
            outcome.quantity,
            outcome.price - marginal_cost,
            alpha=0.3,
            color="tab:green",
            label="Profit",
        )
    )
    ax.add_patch(
        Polygon(
            [
                (outcome.quantity, outcome.price),
                (outcome.quantity, marginal_cost),
                (competitive, marginal_cost),
            ],
            alpha=0.4,
            color="tab:red",
            label="Deadweight loss",
        )
    )
    ax.plot(
        quantities,
        [inverse_demand(q, demand_intercept, demand_slope) for q in quantities],
        label="Demand",
    )
    ax.plot(
        quantities,
        [marginal_revenue(q, demand_intercept, demand_slope) for q in quantities],
        label="MR",
    )
    ax.plot(quantities, [marginal_cost] * len(quantities), label="MC")
    ax.plot([outcome.quantity], [outcome.price], "o", color="black", label="Monopoly")
    ax.plot([competitive], [marginal_cost], "s", color="black", label="Competitive")
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Price")
    ax.set_ylim(0, choke_price(demand_intercept, demand_slope))
    ax.legend()
    plt.close(fig)
    return fig
