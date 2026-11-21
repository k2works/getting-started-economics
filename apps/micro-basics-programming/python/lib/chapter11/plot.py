"""独占（利潤・死荷重）と、独占的競争の長期均衡の図。"""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter09.plot import outline_area
from lib.chapter11.monopoly import (
    Monopoly,
    competitive_outcome,
    long_run_monopolistic_competition,
    monopoly_outcome,
)

_POINTS = 100


def _demand_line(
    ax: Axes, intercept: float, slope: float, label: str, linestyle: str = "-"
) -> None:
    ax.plot([0, intercept / slope], [intercept, 0], label=label, linestyle=linestyle)


def _style(ax: Axes, q_max: float, p_max: float) -> None:
    ax.set_xlabel("Quantity Q")
    ax.set_ylabel("Price P")
    ax.set_xlim(0, q_max)
    ax.set_ylim(0, p_max)
    ax.legend(fontsize="x-small")


def plot_monopoly(monopoly: Monopoly, q_max: float, p_max: float) -> Figure:
    """需要・限界収入・限界費用と、独占の利潤の長方形・死荷重の三角形を描く。"""
    a, b, c = monopoly.demand_intercept, monopoly.demand_slope, monopoly.marginal_cost
    mono, comp = monopoly_outcome(monopoly), competitive_outcome(monopoly)
    fig, ax = plt.subplots()
    _demand_line(ax, a, b, "Demand")
    ax.plot([0, a / (2 * b)], [a, 0], label="Marginal revenue")
    ax.plot([0, q_max], [c, c], label="Marginal cost")
    q, p = mono.quantity, mono.price
    outline_area(ax, [0, q, q, 0, 0], [p, p, c, c, p], "Monopoly profit")
    outline_area(ax, [q, q, comp.quantity, q], [p, c, c, p], "Deadweight loss")
    ax.plot([q], [p], "o", label="Monopoly point")
    ax.plot([comp.quantity], [comp.price], "o", label="Competitive point")
    _style(ax, q_max, p_max)
    plt.close(fig)
    return fig


def plot_long_run(
    monopoly: Monopoly, fixed_cost: float, q_max: float, p_max: float
) -> Figure:
    """独占的競争。参入で需要が左へ動き（点線）、価格が平均費用に等しい点で利潤 0。"""
    b, c = monopoly.demand_slope, monopoly.marginal_cost
    result = long_run_monopolistic_competition(c, b, fixed_cost)
    qs = [q_max * (i + 1) / _POINTS for i in range(_POINTS)]
    fig, ax = plt.subplots()
    _demand_line(ax, monopoly.demand_intercept, b, "Demand before entry")
    _demand_line(ax, result.demand_intercept, b, "Demand after entry", linestyle="--")
    ax.plot([0, q_max], [c, c], label="Marginal cost")
    ax.plot(qs, [c + fixed_cost / q for q in qs], label="Average cost")
    ax.plot([result.quantity], [result.price], "o", label="Long-run equilibrium")
    _style(ax, q_max, p_max)
    plt.close(fig)
    return fig
