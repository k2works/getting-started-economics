"""需要曲線と供給曲線の図。縦軸が価格、横軸が数量。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Polygon, Rectangle

from lib.chapter07.surplus import (
    equilibrium,
    equilibrium_with_tax,
    inverse_demand,
)


def draw_market(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
) -> Figure:
    """需要曲線・供給曲線・均衡点を描いた図を返す。"""
    quantities = [float(q) for q in range(int(demand_intercept) + 1)]
    demand_prices = [
        inverse_demand(q, demand_intercept, demand_slope) for q in quantities
    ]
    # 供給曲線 Q = c + dP を P について解くと P = (Q - c) / d
    supply_prices = [(q - supply_intercept) / supply_slope for q in quantities]
    price, quantity = equilibrium(
        demand_intercept, demand_slope, supply_intercept, supply_slope
    )

    fig, ax = plt.subplots()
    ax.plot(quantities, demand_prices, label="Demand")
    ax.plot(quantities, supply_prices, label="Supply")
    ax.plot([quantity], [price], "o", color="black", label="Equilibrium")
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Price")
    ax.set_ylim(bottom=0)
    ax.legend()
    plt.close(fig)
    return fig


def draw_tax_wedge(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
    tax: float,
) -> Figure:
    """従量税の図: 供給曲線が税額だけ上にずれ、取引量が減り、死荷重ができる。

    税収は、取引量と税額でできる長方形。死荷重は、取引量の減少分と税額でできる三角形。
    """
    taxed = equilibrium_with_tax(
        demand_intercept, demand_slope, supply_intercept, supply_slope, tax
    )
    price, quantity = equilibrium(
        demand_intercept, demand_slope, supply_intercept, supply_slope
    )
    quantities = [float(q) for q in range(int(demand_intercept) + 1)]
    supply_prices = [(q - supply_intercept) / supply_slope for q in quantities]

    fig, ax = plt.subplots()
    ax.add_patch(
        Rectangle(
            (0, taxed.producer_price),
            taxed.quantity,
            tax,
            alpha=0.3,
            color="tab:green",
            label="Tax revenue",
        )
    )
    ax.add_patch(
        Polygon(
            [
                (taxed.quantity, taxed.producer_price),
                (quantity, price),
                (taxed.quantity, taxed.consumer_price),
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
    ax.plot(quantities, supply_prices, label="Supply")
    ax.plot(quantities, [p + tax for p in supply_prices], label="Supply + tax")
    ax.plot([quantity], [price], "o", color="black", label="Equilibrium (no tax)")
    ax.plot(
        [taxed.quantity],
        [taxed.consumer_price],
        "s",
        color="black",
        label="Equilibrium (tax)",
    )
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Price")
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper right")
    plt.close(fig)
    return fig
