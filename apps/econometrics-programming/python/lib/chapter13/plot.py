"""検定の棄却率の図。"""

from collections.abc import Mapping

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def plot_rejection_rates(rates: Mapping[str, float], level: float) -> Figure:
    """検定の棄却率の棒グラフと、有意水準の線。"""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(list(rates), list(rates.values()))
    ax.axhline(level, color="red", linestyle="--", label="Significance level")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Rejection rate")
    ax.legend()
    plt.close(fig)
    return fig
