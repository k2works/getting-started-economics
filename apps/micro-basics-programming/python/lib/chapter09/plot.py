"""消費者余剰・生産者余剰と、課税・死荷重の図。"""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter08.market import LinearMarket, equilibrium, quantity_supplied
from lib.chapter08.plot import draw_curves
from lib.chapter09.surplus import choke_price, reservation_price, tax_equilibrium


def _style(ax: Axes, q_max: float, p_max: float) -> None:
    ax.set_xlabel("Quantity Q")
    ax.set_ylabel("Price P")
    ax.set_xlim(0, q_max)
    ax.set_ylim(0, p_max)
    ax.legend(fontsize="x-small")


def _outline(ax: Axes, xs: list[float], ys: list[float], label: str) -> None:
    """閉じた折れ線を描き、同じ色で、面積を半透明に塗る（塗りは、凡例に載せない）。"""
    (item,) = ax.plot(xs, ys, label=label)
    ax.fill(xs, ys, color=item.get_color(), alpha=0.25, label="_nolegend_")


def plot_surplus(market: LinearMarket, q_max: float, p_max: float) -> Figure:
    """需要曲線・供給曲線と、消費者余剰・生産者余剰の三角形を描く（均衡の価格で）。"""
    price, quantity = equilibrium(market)
    fig, ax = plt.subplots()
    draw_curves(ax, market, p_max)
    choke, reservation = choke_price(market), reservation_price(market)
    _outline(ax, [0, quantity, 0, 0], [choke, price, price, choke], "Consumer surplus")
    _outline(
        ax,
        [0, quantity, 0, 0],
        [reservation, price, price, reservation],
        "Producer surplus",
    )
    ax.plot([quantity], [price], "o", label="Equilibrium")
    _style(ax, q_max, p_max)
    plt.close(fig)
    return fig


def plot_tax(market: LinearMarket, tax: float, q_max: float, p_max: float) -> Figure:
    """従量税による、供給曲線の移動（点線）と、税収の長方形・死荷重の三角形を描く。"""
    result = tax_equilibrium(market, tax)
    price, quantity = equilibrium(market)
    fig, ax = plt.subplots()
    draw_curves(ax, market, p_max)
    ax.plot(
        [0, quantity_supplied(market, p_max - tax)],
        [reservation_price(market) + tax, p_max],
        "--",
        label="Supply after tax",
    )
    q, buyer, seller = result.quantity, result.buyer_price, result.seller_price
    rectangle = ([0, q, q, 0, 0], [buyer, buyer, seller, seller, buyer])
    _outline(ax, *rectangle, "Tax revenue")
    _outline(ax, [q, q, quantity, q], [buyer, seller, price, buyer], "Deadweight loss")
    ax.plot([quantity], [price], "o", label="Equilibrium")
    ax.plot([q], [buyer], "o", label="Equilibrium with tax")
    _style(ax, q_max, p_max)
    plt.close(fig)
    return fig
