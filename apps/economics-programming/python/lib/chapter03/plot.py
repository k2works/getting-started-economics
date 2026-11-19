"""需要表と供給表の図。縦軸が価格、横軸が数量。"""

from collections.abc import Mapping

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter03.schedule import market_clearing_prices


def plot_schedules(demand: Mapping[int, float], supply: Mapping[int, float]) -> Figure:
    """需要表と供給表の点（価格ごとの数量）を線で結んで描く。

    需要量と供給量が等しい価格があれば、その点（市場均衡）も描く。
    """
    prices = sorted(demand)
    fig, ax = plt.subplots()
    ax.plot([demand[p] for p in prices], prices, "o-", label="Demand")
    ax.plot([supply[p] for p in sorted(supply)], sorted(supply), "o-", label="Supply")
    clearing = market_clearing_prices(demand, supply)
    if clearing:
        ax.plot(
            [demand[p] for p in clearing],
            clearing,
            "s",
            color="black",
            markersize=10,
            fillstyle="none",
            label="Market clearing",
        )
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Price")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend()
    plt.close(fig)
    return fig
