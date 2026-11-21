"""屈折需要曲線と、協調が続く条件（割引因子の閾値）の図。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter12.kinked import (
    KinkedDemand,
    marginal_revenue_above,
    marginal_revenue_below,
)
from lib.chapter12.repeated import (
    cooperation_threshold,
    cooperation_value,
    deviation_value,
)


def plot_kinked(
    demand: KinkedDemand,
    q_max: float,
    p_max: float,
    cost_low: float,
    cost_high: float,
) -> Figure:
    """屈折需要曲線と、限界収入の途切れ。限界費用が途切れの中なら、価格は動かない。"""
    q, p = demand.kink_quantity, demand.kink_price
    b1, b2 = demand.upper_slope, demand.lower_slope
    above, below = marginal_revenue_above(demand), marginal_revenue_below(demand)
    y_min = below - 40
    a2 = p + b2 * q
    fig, ax = plt.subplots()
    ax.plot([0, q, q + p / b2], [p + b1 * q, p, 0], label="Demand")
    ax.plot([0, q], [p + b1 * q, above], label="Marginal revenue (upper)")
    ax.plot(
        [q, (a2 - y_min) / (2 * b2)], [below, y_min], label="Marginal revenue (lower)"
    )
    ax.plot([q, q], [below, above], linestyle=":", label="MR gap")
    ax.plot([0, q_max], [cost_low, cost_low], label="Marginal cost (low)")
    ax.plot([0, q_max], [cost_high, cost_high], label="Marginal cost (high)")
    ax.set_xlabel("Quantity Q")
    ax.set_ylabel("Price P")
    ax.set_xlim(0, q_max)
    ax.set_ylim(y_min, p_max)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig


def plot_trigger(
    temptation: float,
    reward: float,
    punishment: float,
    delta_max: float,
    delta_points: int,
    y_max: float,
) -> Figure:
    """協調を続ける価値と、一度裏切る価値。割引因子が閾値を超えると、協調が上回る。"""
    deltas = [delta_max * i / (delta_points - 1) for i in range(delta_points)]
    threshold = cooperation_threshold(temptation, reward, punishment)
    fig, ax = plt.subplots()
    ax.plot(
        deltas,
        [cooperation_value(reward, d) for d in deltas],
        label="Cooperate forever",
    )
    ax.plot(
        deltas,
        [deviation_value(temptation, punishment, d) for d in deltas],
        label="Defect once",
    )
    ax.plot(
        [threshold],
        [cooperation_value(reward, threshold)],
        "o",
        label="Threshold",
    )
    ax.set_xlabel("Discount factor")
    ax.set_ylabel("Present value")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, y_max)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig
