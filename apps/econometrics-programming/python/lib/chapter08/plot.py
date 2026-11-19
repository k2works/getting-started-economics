"""標準誤差の比較の図。"""

from collections.abc import Mapping

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def plot_standard_errors(values: Mapping[str, float]) -> Figure:
    """実際のばらつきと、通常・頑健な標準誤差を、棒グラフで比べる。"""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(list(values), list(values.values()))
    ax.set_ylabel("Standard error of the slope")
    plt.close(fig)
    return fig
