"""購買力平価の図。"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure


def plot_relative_price_levels(levels: pd.Series) -> Figure:
    """国ごとの相対価格水準を、低い順に棒で描く。高さ 1 が、一物一価。"""
    ordered = levels.sort_values()
    fig, ax = plt.subplots()
    ax.bar(list(ordered.index), ordered.to_numpy())
    ax.axhline(1, linestyle="--", color="gray", label="Law of one price")
    ax.set_ylabel("Relative price level (base = 1)")
    ax.tick_params(axis="x", labelrotation=90)
    ax.legend()
    plt.close(fig)
    return fig
