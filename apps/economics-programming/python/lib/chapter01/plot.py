"""需要曲線の図。縦軸が価格、横軸が数量。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter01.demand import choke_price, quantity_demanded


def plot_demand_curve(intercept: float, slope: float) -> Figure:
    """需要曲線 Q = a - bP と、2 つの切片（チョーク価格と、価格 0 の需要量）を描く。"""
    top_price = choke_price(intercept, slope)
    prices = [0.0, top_price]

    fig, ax = plt.subplots()
    ax.plot(
        [quantity_demanded(p, intercept, slope) for p in prices], prices, label="Demand"
    )
    ax.plot([0], [top_price], "o", color="black", label="Choke price")
    ax.plot(
        [quantity_demanded(0, intercept, slope)],
        [0],
        "s",
        color="black",
        label="Quantity at price 0",
    )
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Price")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend()
    plt.close(fig)
    return fig
