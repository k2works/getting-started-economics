"""回帰の図。"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from lib.chapter03.regression import fit_ols


def plot_regression(
    x: pd.Series, y: pd.Series, xlabel: str = "x", ylabel: str = "y"
) -> Figure:
    """点の散布図と、最小二乗法の回帰直線を描く。"""
    result = fit_ols(y, pd.DataFrame({"x": x}))
    ends = np.array([x.min(), x.max()])
    line = result.coefficients["const"] + result.coefficients["x"] * ends

    fig, ax = plt.subplots()
    ax.plot(x, y, "o", label="Countries")
    ax.plot(ends, line, label="OLS line")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    plt.close(fig)
    return fig
