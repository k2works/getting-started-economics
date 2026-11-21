"""等産出量曲線・等費用線と、限界生産性の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter06.production import (
    cost_minimizing_inputs,
    isocost_k,
    isoquant_k,
    marginal_product_labor,
    minimum_cost,
)

_POINTS = 50


def plot_cost_minimization(
    levels: Sequence[float], quantity: float, w: float, r: float
) -> Figure:
    """等産出量曲線の族と、生産量 quantity を最も安く作る等費用線（接線）を描く。

    等費用線は、最小の費用で引く。等産出量曲線に、1 点で接し、その点が最適な (L, K)。
    """
    cost = minimum_cost(quantity, w, r)
    l_max = cost / w
    labors = [l_max * (i + 1) / _POINTS for i in range(_POINTS)]
    fig, ax = plt.subplots()
    for level in levels:
        ax.plot(labors, [isoquant_k(level, x) for x in labors], label=f"q = {level}")
    ax.plot(
        [0, l_max],
        [isocost_k(cost, w, r, 0), isocost_k(cost, w, r, l_max)],
        label=f"Isocost (cost = {cost:g})",
    )
    labor, capital = cost_minimizing_inputs(quantity, w, r)
    ax.plot([labor], [capital], "o", label="Optimum")
    ax.set_xlabel("Labor L")
    ax.set_ylabel("Capital K")
    # 等産出量曲線は L が小さいと立ち上がるので、等費用線の K 切片の 1.5 倍までを見せる
    ax.set_xlim(0, l_max)
    ax.set_ylim(0, 1.5 * cost / r)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig


def plot_marginal_product(capital: float, l_max: float) -> Figure:
    """資本を一定にしたときの、労働の限界生産性。労働が増えると、逓減する。"""
    labors = [l_max * (i + 1) / _POINTS for i in range(_POINTS)]
    fig, ax = plt.subplots()
    ax.plot(
        labors,
        [marginal_product_labor(x, capital) for x in labors],
        label=f"MPL (K = {capital:g})",
    )
    ax.set_xlabel("Labor L")
    ax.set_ylabel("Marginal product of labor")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig
