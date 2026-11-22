"""独占の利潤の放物線と、クールノー競争で企業の数を増やしたときの図。"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from lib.chapter02.monopoly import (
    competitive_outcome,
    cournot_outcome,
    monopoly_outcome,
    monopoly_profit,
)


def plot_monopoly_profit(a: float, b: float, cost: float) -> Figure:
    """利潤 π(Q) を、Q = 0 から完全競争の数量（利潤が 0 に戻る点）まで描く。"""
    best = monopoly_outcome(a, b, cost)
    q_end = competitive_outcome(a, b, cost).quantity
    quantities = np.linspace(0, q_end, 101).tolist()
    profits = [monopoly_profit(q, a, b, cost) for q in quantities]
    fig, ax = plt.subplots()
    ax.plot(quantities, profits, label="Profit")
    ax.plot([best.quantity], [best.profit], "ko", label="Monopoly optimum")
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Profit")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig


def plot_cournot_convergence(a: float, b: float, cost: float, max_firms: int) -> Figure:
    """企業の数 n = 1…max_firms の、クールノー均衡の総数量と価格を描く。"""
    firms = list(range(1, max_firms + 1))
    outcomes = [cournot_outcome(n, a, b, cost) for n in firms]
    competition = competitive_outcome(a, b, cost)
    ends = [firms[0], firms[-1]]
    fig, ax = plt.subplots()
    ax.plot(firms, [r.quantity for r in outcomes], "o-", label="Total quantity")
    ax.plot(firms, [r.price for r in outcomes], "s-", label="Price")
    ax.plot(ends, [competition.quantity] * 2, "--", label="Competitive quantity")
    ax.plot(ends, [cost] * 2, ":", label="Unit cost")
    ax.set_xlabel("Number of firms")
    ax.set_ylabel("Quantity / Price")
    ax.set_ylim(bottom=0)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig
