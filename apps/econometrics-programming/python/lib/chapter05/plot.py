"""信頼区間の図。"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure


def plot_confidence_intervals(intervals: pd.DataFrame, true_value: float) -> Figure:
    """標本ごとの信頼区間を縦線で描く。真の値を含む区間と、含まない区間で色を変える。"""
    fig, ax = plt.subplots()
    seen: set[bool] = set()
    names = {True: "Contains true value", False: "Misses true value"}
    colors = {True: "tab:blue", False: "tab:red"}
    for i, (lower, upper) in enumerate(
        zip(intervals["lower"], intervals["upper"], strict=True)
    ):
        contains = bool(lower <= true_value <= upper)
        label = "_interval" if contains in seen else names[contains]
        seen.add(contains)
        ax.plot([i, i], [lower, upper], color=colors[contains], label=label)
    ax.axhline(true_value, color="black", linestyle="--", label="True value")
    ax.set_xlabel("Sample")
    ax.set_ylabel("95% confidence interval of the slope")
    ax.legend()
    plt.close(fig)
    return fig
