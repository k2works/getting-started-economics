"""供給曲線（利潤・損益分岐点・操業停止点）と、課税後の供給曲線の図。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter05.cost import (
    CostCurve,
    average_cost,
    average_variable_cost,
    cost_minima,
    marginal_cost,
)
from lib.chapter07.supply import (
    profit_maximizing_output,
    shutdown_price,
    supply_price,
    supply_price_ad_valorem,
    supply_price_unit_tax,
)

_POINTS = 100
_TAX_POINTS = 50


def plot_supply(curve: CostCurve, price: float, q_max: float, y_max: float) -> Figure:
    """AC・AVC・MC と価格の線に、利潤の長方形と 3 つの点を重ねて描く。

    3 つの点は、利潤最大・損益分岐・操業停止。供給曲線は、操業停止点より上の MC。
    利潤の長方形は、高さ (P − AC)、幅 q。
    """
    qs = [q_max * (i + 1) / _POINTS for i in range(_POINTS)]
    q_best = profit_maximizing_output(curve, price)
    q_stop = cost_minima(curve, q_max)["AVC"][0]
    fig, ax = plt.subplots()
    ax.plot(qs, [average_cost(curve, q) for q in qs], label="AC")
    ax.plot(qs, [average_variable_cost(curve, q) for q in qs], label="AVC")
    ax.plot(qs, [marginal_cost(curve, q) for q in qs], label="MC")
    above = [q for q in qs if q >= q_stop]
    ax.plot(
        above,
        [marginal_cost(curve, q) for q in above],
        linewidth=3,
        label="Supply curve (MC above shutdown)",
    )
    ax.plot([0, q_max], [price, price], label="Price")
    cost = average_cost(curve, q_best)
    ax.plot(
        [0, q_best, q_best, 0, 0],
        [price, price, cost, cost, price],
        label="Profit rectangle",
    )
    minima = cost_minima(curve, q_max)
    ax.plot([q_best], [price], "o", label="Profit-maximizing point")
    ax.plot([minima["AC"][0]], [minima["AC"][1]], "o", label="Break-even point")
    ax.plot([minima["AVC"][0]], [shutdown_price(curve)], "o", label="Shutdown point")
    ax.set_xlabel("Quantity q")
    ax.set_ylabel("Price and cost per unit")
    ax.set_xlim(0, q_max)
    ax.set_ylim(0, y_max)
    ax.legend(fontsize="x-small", loc="lower right")
    plt.close(fig)
    return fig


def plot_tax_supply(
    curve: CostCurve, tax: float, rate: float, q_min: float, q_max: float
) -> Figure:
    """供給曲線と、課税後の供給曲線。従量税は上へ平行に動き、従価税は傾きが急になる。"""
    step = (q_max - q_min) / (_TAX_POINTS - 1)
    qs = [q_min + step * i for i in range(_TAX_POINTS)]
    fig, ax = plt.subplots()
    ax.plot(qs, [supply_price(curve, q) for q in qs], label="Supply")
    ax.plot(
        qs,
        [supply_price_unit_tax(curve, q, tax) for q in qs],
        "--",
        label="Supply after unit tax",
    )
    ax.plot(
        qs,
        [supply_price_ad_valorem(curve, q, rate) for q in qs],
        "--",
        label="Supply after ad valorem tax",
    )
    ax.set_xlabel("Quantity q")
    ax.set_ylabel("Price")
    ax.set_xlim(q_min, q_max)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig
