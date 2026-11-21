"""付加価値と成長会計の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter01.gdp import GrowthAccounting, value_added


def plot_value_added(
    stages: Sequence[str], output: Sequence[float], intermediate: Sequence[float]
) -> Figure:
    """段階ごとの生産額を、中間投入（下）と付加価値（上）の積み上げ棒で描く。

    積み上げた高さが、その段階の生産額。付加価値の部分だけを足すと、GDP になる。
    """
    added = value_added(output, intermediate)
    fig, ax = plt.subplots()
    ax.bar(stages, intermediate, label="Intermediate input")
    ax.bar(stages, added, bottom=intermediate, label="Value added")
    ax.set_ylabel("Value (10,000 yen)")
    ax.legend()
    plt.close(fig)
    return fig


def plot_growth_accounting(result: GrowthAccounting) -> Figure:
    """成長会計の、労働・資本・技術進歩の寄与（% ポイント）を、3 本の棒で描く。"""
    fig, ax = plt.subplots()
    ax.bar(
        ["Labor", "Capital", "Technology"],
        [result.labor, result.capital, result.technology],
    )
    ax.set_ylabel("Growth (points)")
    plt.close(fig)
    return fig
