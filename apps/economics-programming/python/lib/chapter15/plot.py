"""独占の図。縦軸が価格、横軸が数量。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Polygon, Rectangle

from lib.chapter01.demand import choke_price
from lib.chapter07.surplus import equilibrium, inverse_demand
from lib.chapter15.externality import social_optimum_quantity
from lib.chapter15.monopoly import (
    competitive_quantity,
    marginal_revenue,
    monopoly_outcome,
)
from lib.chapter15.oligopoly import best_response, cournot_by_iteration


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


def plot_cournot(
    demand_intercept: float, demand_slope: float, marginal_cost: float
) -> Figure:
    """2 社のクールノー競争: 各社の最適反応曲線と、その交点（均衡）を描く。

    横軸が企業 1 の生産量、縦軸が企業 2 の生産量。企業 1 の反応曲線は、
    企業 2 の生産量に対する最適な生産量。
    """
    limit = competitive_quantity(demand_intercept, demand_slope, marginal_cost)
    others = [limit * i / 40 for i in range(41)]
    equilibrium_1, equilibrium_2 = cournot_by_iteration(
        demand_intercept, demand_slope, marginal_cost
    )

    def reaction(q: float) -> float:
        return best_response(q, demand_intercept, demand_slope, marginal_cost)

    fig, ax = plt.subplots()
    ax.plot([reaction(q) for q in others], others, label="Firm 1 best response")
    ax.plot(others, [reaction(q) for q in others], label="Firm 2 best response")
    ax.plot(
        [equilibrium_1],
        [equilibrium_2],
        "o",
        color="black",
        label="Cournot equilibrium",
    )
    ax.set_xlabel("Firm 1 quantity")
    ax.set_ylabel("Firm 2 quantity")
    ax.set_xlim(0, limit)
    ax.set_ylim(0, limit)
    ax.legend()
    plt.close(fig)
    return fig


def plot_externality(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
    external_cost: float,
) -> Figure:
    """外部不経済: 社会的な供給曲線は、私的な供給曲線を外部費用だけ上にずらしたもの。

    放任の市場点は、社会的に最適な数量より多く取引し、その差が死荷重の三角形になる。
    """
    price, quantity = equilibrium(
        demand_intercept, demand_slope, supply_intercept, supply_slope
    )
    optimum = social_optimum_quantity(
        demand_intercept, demand_slope, supply_intercept, supply_slope, external_cost
    )
    optimum_price = inverse_demand(optimum, demand_intercept, demand_slope)
    quantities = [float(q) for q in range(int(demand_intercept) + 1)]
    private = [(q - supply_intercept) / supply_slope for q in quantities]

    fig, ax = plt.subplots()
    ax.add_patch(
        Polygon(
            [
                (optimum, optimum_price),
                (quantity, price),
                (quantity, price + external_cost),
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
    ax.plot(quantities, private, label="Supply (private)")
    ax.plot(quantities, [p + external_cost for p in private], label="Supply (social)")
    ax.plot([quantity], [price], "o", color="black", label="Market")
    ax.plot([optimum], [optimum_price], "s", color="black", label="Social optimum")
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Price")
    ax.set_xlim(0, demand_intercept * 0.8)
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper right")
    plt.close(fig)
    return fig
