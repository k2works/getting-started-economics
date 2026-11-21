"""関税の余剰分析と、生産可能性フロンティアの図。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter08.market import LinearMarket
from lib.chapter08.plot import draw_curves
from lib.chapter09.plot import outline_area
from lib.chapter10.comparative import Country, ppf_endpoints
from lib.chapter10.trade import free_trade_result, tariff_result


def plot_tariff(
    market: LinearMarket,
    world_price: float,
    tariff: float,
    q_max: float,
    p_max: float,
) -> Figure:
    """関税による、国内価格の上昇と、関税収入の長方形・死荷重の 2 つの三角形を描く。"""
    free = free_trade_result(market, world_price)
    taxed = tariff_result(market, world_price, tariff)
    price = taxed.domestic_price
    fig, ax = plt.subplots()
    draw_curves(ax, market, p_max)
    ax.plot([0, q_max], [world_price, world_price], label="World price")
    ax.plot([0, q_max], [price, price], label="Price with tariff")
    supplied, demanded = taxed.quantity_supplied, taxed.quantity_demanded
    outline_area(
        ax,
        [supplied, demanded, demanded, supplied, supplied],
        [price, price, world_price, world_price, price],
        "Tariff revenue",
    )
    outline_area(
        ax,
        [free.quantity_supplied, supplied, supplied, free.quantity_supplied],
        [world_price, world_price, price, world_price],
        "Production loss",
    )
    outline_area(
        ax,
        [demanded, demanded, free.quantity_demanded, demanded],
        [price, world_price, world_price, price],
        "Consumption loss",
    )
    ax.set_xlabel("Quantity Q")
    ax.set_ylabel("Price P")
    ax.set_xlim(0, q_max)
    ax.set_ylim(0, p_max)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig


def plot_ppf(a: Country, labor_a: float, b: Country, labor_b: float) -> Figure:
    """2 国の生産可能性フロンティア。傾きの大きさ（機会費用）が違う。"""
    fig, ax = plt.subplots()
    for country, labor in ((a, labor_a), (b, labor_b)):
        (industry, _), (_, agriculture) = ppf_endpoints(country, labor)
        ax.plot([industry, 0], [0, agriculture], label=country.name)
    ax.set_xlabel("Industry")
    ax.set_ylabel("Agriculture")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig
