"""需要曲線・供給曲線・均衡と、シフト・調整過程の図。"""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter08.market import (
    LinearMarket,
    equilibrium,
    marshall_adjustment,
    quantity_supplied,
    shift_demand,
    walras_adjustment,
)


def _style(ax: Axes, q_max: float, p_max: float) -> None:
    ax.set_xlabel("Quantity Q")
    ax.set_ylabel("Price P")
    ax.set_xlim(0, q_max)
    ax.set_ylim(0, p_max)
    ax.legend(fontsize="x-small")


def _draw_curves(ax: Axes, market: LinearMarket, p_max: float) -> None:
    """需要曲線（数量が 0 になる価格から、価格 0 まで）と、供給曲線を描く。"""
    choke = -market.demand_intercept / market.demand_slope
    ax.plot([0, market.demand_intercept], [choke, 0], label="Demand")
    reservation = -market.supply_intercept / market.supply_slope
    ax.plot([0, quantity_supplied(market, p_max)], [reservation, p_max], label="Supply")


def plot_market(market: LinearMarket, q_max: float, p_max: float) -> Figure:
    """需要曲線・供給曲線と、均衡点（交点）を描く。縦軸が価格、横軸が数量。"""
    fig, ax = plt.subplots()
    _draw_curves(ax, market, p_max)
    price, quantity = equilibrium(market)
    ax.plot([quantity], [price], "o", label="Equilibrium")
    _style(ax, q_max, p_max)
    plt.close(fig)
    return fig


def plot_shift(
    market: LinearMarket, delta: float, q_max: float, p_max: float
) -> Figure:
    """需要曲線が delta だけ右へ動いたときの、均衡の移動。動かしたあとは、点線。"""
    moved = shift_demand(market, delta)
    fig, ax = plt.subplots()
    _draw_curves(ax, market, p_max)
    choke = -moved.demand_intercept / moved.demand_slope
    ax.plot([0, moved.demand_intercept], [choke, 0], "--", label="Demand after shift")
    price0, quantity0 = equilibrium(market)
    price1, quantity1 = equilibrium(moved)
    ax.plot([quantity0], [price0], "o", label="Equilibrium before")
    ax.plot([quantity1], [price1], "o", label="Equilibrium after")
    _style(ax, q_max, p_max)
    plt.close(fig)
    return fig


def plot_adjustment(
    market: LinearMarket, price0: float, quantity0: float, speed: float, steps: int
) -> Figure:
    """ワルラス的調整（価格の推移）と、マーシャル的調整（数量の推移）を、左右に並べる。"""
    price, quantity = equilibrium(market)
    fig, (left, right) = plt.subplots(1, 2, figsize=(9, 3.5))
    steps_axis = list(range(steps + 1))
    prices = walras_adjustment(market, price0, speed, steps)
    quantities = marshall_adjustment(market, quantity0, speed, steps)
    left.plot(steps_axis, prices, label="Price")
    left.plot([0, steps], [price, price], label="Equilibrium price")
    left.set_title("Walras (price)")
    left.set_ylabel("Price P")
    right.plot(steps_axis, quantities, label="Quantity")
    right.plot([0, steps], [quantity, quantity], label="Equilibrium quantity")
    right.set_title("Marshall (quantity)")
    right.set_ylabel("Quantity Q")
    for ax in (left, right):
        ax.set_xlabel("Step")
        ax.legend(fontsize="x-small")
    fig.tight_layout()
    plt.close(fig)
    return fig
