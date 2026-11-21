"""貨幣量と物価（交換方程式）、為替レートと純輸出の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter13.open_economy import net_exports_from_exchange_rate
from lib.chapter13.quantity import price_level_from_quantity


def plot_money_and_prices(
    velocity: float, outputs: Sequence[float], moneys: Sequence[float]
) -> Figure:
    """貨幣量 M と物価水準 P の関係を、生産量 Y ごとの直線で描く。

    P = MV ÷ Y なので、M が 2 倍になると P も 2 倍。Y が大きいと、傾きが小さい。
    """
    fig, ax = plt.subplots()
    for output in outputs:
        prices = [price_level_from_quantity(m, velocity, output) for m in moneys]
        ax.plot(moneys, prices, label=f"Y = {output}")
    ax.set_xlabel("Money supply M")
    ax.set_ylabel("Price level P")
    ax.legend()
    plt.close(fig)
    return fig


def plot_net_exports(
    rates: Sequence[float], base_net_exports: float, base_rate: float, slope: float
) -> Figure:
    """為替レート（1 ドルあたりの円）と純輸出。右へ行くほど円安で、純輸出が増える。"""
    net_exports = [
        net_exports_from_exchange_rate(e, base_net_exports, base_rate, slope)
        for e in rates
    ]
    fig, ax = plt.subplots()
    ax.plot(rates, net_exports, label="Net exports")
    ax.plot([base_rate], [base_net_exports], "o", label="Base")
    ax.set_xlabel("Exchange rate (yen per dollar)")
    ax.set_ylabel("Net exports")
    ax.legend()
    plt.close(fig)
    return fig
