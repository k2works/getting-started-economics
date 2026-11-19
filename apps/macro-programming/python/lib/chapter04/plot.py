"""差分方程式の図。"""

from collections.abc import Mapping

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def plot_paths(paths: Mapping[str, list[float]], steady_state: float) -> Figure:
    """経路（名前 -> 値の推移）を重ねて、定常状態の線と一緒に描く。"""
    longest = max(len(path) for path in paths.values())
    fig, ax = plt.subplots()
    for name, path in paths.items():
        ax.plot(range(len(path)), path, "o-", markersize=3, label=name)
    ax.plot(
        [0, longest - 1],
        [steady_state] * 2,
        "--",
        color="gray",
        label="Steady state",
    )
    ax.set_xlabel("Period t")
    ax.set_ylabel("x(t)")
    ax.legend()
    plt.close(fig)
    return fig


def plot_cobweb(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
    initial_price: float,
    periods: int,
) -> Figure:
    """蜘蛛の巣モデルの図: 価格が決める供給量と、その数量で決まる次の価格をたどる。

    横軸が数量、縦軸が価格。供給は、前期の価格で決まる。
    """
    price = initial_price
    quantity = supply_intercept + supply_slope * price
    path = [(quantity, price)]
    for _ in range(periods):
        price = (demand_intercept - quantity) / demand_slope
        path.append((quantity, price))
        quantity = supply_intercept + supply_slope * price
        path.append((quantity, price))
    quantities = [demand_intercept * i / 50 for i in range(51)]

    fig, ax = plt.subplots()
    ax.plot(
        quantities,
        [(demand_intercept - q) / demand_slope for q in quantities],
        label="Demand",
    )
    ax.plot(
        quantities,
        [(q - supply_intercept) / supply_slope for q in quantities],
        label="Supply",
    )
    ax.plot(
        [q for q, _ in path], [p for _, p in path], "o-", markersize=3, label="Path"
    )
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Price")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend()
    plt.close(fig)
    return fig
