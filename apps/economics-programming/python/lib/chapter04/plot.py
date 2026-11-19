"""費用曲線の図。縦軸が 1 単位あたりの費用、横軸が生産量。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter04.cost import average_cost, average_variable_cost, marginal_cost


def plot_cost_curves(max_quantity: float = 6, step: float = 0.1) -> Figure:
    """限界費用 MC・平均可変費用 AVC・平均費用 AC と、操業停止点を描いた図を返す。

    操業停止点は、平均可変費用が最低になる点（MC が AVC を下から横切る点）。
    """
    quantities = [round(i * step, 6) for i in range(1, round(max_quantity / step) + 1)]
    shutdown_quantity = min(quantities, key=average_variable_cost)

    fig, ax = plt.subplots()
    ax.plot(quantities, [marginal_cost(q) for q in quantities], label="MC")
    ax.plot(quantities, [average_variable_cost(q) for q in quantities], label="AVC")
    ax.plot(quantities, [average_cost(q) for q in quantities], label="AC")
    ax.plot(
        [shutdown_quantity],
        [average_variable_cost(shutdown_quantity)],
        "o",
        color="black",
        label="Shutdown point",
    )
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Cost per unit")
    ax.set_ylim(0, 30)
    ax.legend()
    plt.close(fig)
    return fig
