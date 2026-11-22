"""シグナル（教育年数）と、成果報酬（努力の誘因）の図。"""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter16.information import (
    minimum_bonus,
    separating_education_range,
)


def _style(ax: Axes, x_max: float, xlabel: str, ylabel: str) -> None:
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim(0, x_max)
    ax.legend(fontsize="x-small")


def plot_signal(
    wage_high: float,
    wage_low: float,
    cost_high: float,
    cost_low: float,
    e_max: float,
) -> Figure:
    """教育年数ごとの利得。範囲の中なら、高い能力の人だけが、教育を選ぶ。"""
    low, high = separating_education_range(wage_high, wage_low, cost_high, cost_low)
    y_min = wage_high - cost_low * e_max
    fig, ax = plt.subplots()
    ax.plot(
        [0, e_max],
        [wage_high, wage_high - cost_high * e_max],
        label="High type (signal)",
    )
    ax.plot(
        [0, e_max],
        [wage_high, wage_high - cost_low * e_max],
        label="Low type (imitate)",
    )
    ax.plot([0, e_max], [wage_low, wage_low], label="Low type (no signal)")
    ax.plot([low, low], [y_min, wage_high], linestyle=":", label="Lower bound")
    ax.plot([high, high], [y_min, wage_high], linestyle=":", label="Upper bound")
    _style(ax, e_max, "Years of education", "Payoff")
    plt.close(fig)
    return fig


def plot_bonus(p_high: float, p_low: float, effort_cost: float, b_max: float) -> Figure:
    """成果報酬 b ごとの、努力する・しない場合の、期待利得。交点が最低の成果報酬。"""
    bonus = minimum_bonus(p_high, p_low, effort_cost)
    fig, ax = plt.subplots()
    ax.plot([0, b_max], [-effort_cost, p_high * b_max - effort_cost], label="Work")
    ax.plot([0, b_max], [0, p_low * b_max], label="Shirk")
    ax.plot([bonus], [p_low * bonus], "o", label="Minimum bonus")
    _style(ax, b_max, "Bonus b", "Expected payoff")
    plt.close(fig)
    return fig
