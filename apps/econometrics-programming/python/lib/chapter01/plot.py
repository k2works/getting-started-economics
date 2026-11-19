"""正規分布と t 分布の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from scipy import stats


def plot_densities(degrees_of_freedom: Sequence[int] = (2, 5, 30)) -> Figure:
    """標準正規分布と、自由度ごとの t 分布の密度関数を重ねて描く。"""
    grid = np.linspace(-4, 4, 201)
    fig, ax = plt.subplots()
    ax.plot(grid, stats.norm.pdf(grid), label="Normal")
    for df in degrees_of_freedom:
        ax.plot(grid, stats.t.pdf(grid, df), label=f"t({df})")
    ax.set_xlabel("Value")
    ax.set_ylabel("Density")
    ax.legend()
    plt.close(fig)
    return fig
