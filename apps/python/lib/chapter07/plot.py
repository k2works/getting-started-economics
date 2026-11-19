"""需要曲線と供給曲線の図。縦軸が価格、横軸が数量。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter07.surplus import equilibrium


def draw_market(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
) -> Figure:
    """需要曲線・供給曲線・均衡点を描いた図を返す。"""
    quantities = [float(q) for q in range(int(demand_intercept) + 1)]
    # 需要曲線 Q = a - bP を P について解くと P = (a - Q) / b
    demand_prices = [(demand_intercept - q) / demand_slope for q in quantities]
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
