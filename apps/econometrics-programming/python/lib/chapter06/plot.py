"""標本の大きさごとの、推定値の分布の図。"""

from collections.abc import Mapping

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray


def plot_estimate_distributions(
    estimates: Mapping[int, NDArray[np.float64]], true_value: float
) -> Figure:
    """標本の大きさごとの推定値のヒストグラム（密度）と、真の値の線を描く。"""
    fig, ax = plt.subplots()
    for n, values in estimates.items():
        ax.hist(values, bins=30, density=True, alpha=0.5, label=f"n = {n}")
    ax.axvline(true_value, color="black", linestyle="--", label="True value")
    ax.set_xlabel("Estimated slope")
    ax.set_ylabel("Density")
    ax.legend()
    plt.close(fig)
    return fig
