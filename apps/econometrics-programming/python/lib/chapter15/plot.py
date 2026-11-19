"""打ち切られたデータと、OLS・トービットの直線の図。"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray

from lib.chapter03.multiple import fit_ols
from lib.chapter15.limited import fit_tobit


def plot_censored_data(x: NDArray[np.float64], y: NDArray[np.float64]) -> Figure:
    """0 で打ち切られたデータと、真の直線（1 + 2x）、OLS・トービットの直線を描く。"""
    ends = np.array([float(x.min()), float(x.max())])
    ols = fit_ols(y, x).coefficients
    tobit = fit_tobit(y, x).coefficients
    fig, ax = plt.subplots()
    ax.plot(x, y, "o", alpha=0.3, label="Data")
    ax.plot(ends, 1 + 2 * ends, "--", label="True line")
    ax.plot(ends, ols["const"] + ols["x1"] * ends, label="OLS")
    ax.plot(ends, tobit["const"] + tobit["x1"] * ends, label="Tobit")
    ax.set_xlabel("x")
    ax.set_ylabel("y (censored at 0)")
    ax.legend()
    plt.close(fig)
    return fig
