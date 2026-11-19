"""回帰直線と、傾きの標本分布の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from lib.chapter01.statistics import Array
from lib.chapter02.simple import SimpleFit, fitted_values


def plot_regression_line(x: Array, y: Array, fit: SimpleFit) -> Figure:
    """データ・回帰直線・残差（データと直線を結ぶ縦線）を描く。"""
    fig, ax = plt.subplots()
    ax.plot(x, y, "o", label="Data")
    ends = [float(np.min(x)), float(np.max(x))]
    ax.plot(ends, fitted_values(fit, ends), label="Fitted line")
    for xi, yi, fi in zip(x, y, fitted_values(fit, x), strict=True):
        ax.plot([xi, xi], [fi, yi], color="gray", linestyle=":", label="_residual")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    plt.close(fig)
    return fig


def plot_slope_distribution(slopes: Sequence[float], true_slope: float) -> Figure:
    """傾きの推定値のヒストグラムと、真の傾きの線を描く。"""
    fig, ax = plt.subplots()
    ax.hist(slopes, bins=10)
    ax.axvline(true_slope, color="red", label="True slope")
    ax.set_xlabel("Estimated slope")
    ax.set_ylabel("Frequency")
    ax.legend()
    plt.close(fig)
    return fig
