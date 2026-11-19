"""成長会計の図。"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure


def plot_growth_contributions(table: pd.DataFrame) -> Figure:
    """国全体の平均の、所得の成長率と、3 つの寄与を、棒で描く。

    3 本の寄与の棒の高さの和が、所得の成長率の棒の高さになる。
    """
    means = [
        table["output"].mean(),
        table["capital"].mean(),
        table["human_capital"].mean(),
        table["tfp"].mean(),
    ]
    fig, ax = plt.subplots()
    ax.bar(["Output", "Capital", "Human capital", "TFP"], means)
    ax.set_ylabel("Growth rate (% per year)")
    plt.close(fig)
    return fig


def plot_tfp_growth(table: pd.DataFrame) -> Figure:
    """国ごとの、TFP の成長率（横軸）と所得の成長率（縦軸）の散布図と近似直線を描く。"""
    x = table["tfp"].to_numpy()
    y = table["output"].to_numpy()
    slope, intercept = np.polyfit(x, y, 1)
    ends = np.array([x.min(), x.max()])

    fig, ax = plt.subplots()
    ax.plot(x, y, "o", label="Countries")
    ax.plot(ends, intercept + slope * ends, label="Fitted line")
    ax.set_xlabel("TFP growth (% per year)")
    ax.set_ylabel("Income growth (% per year)")
    ax.legend()
    plt.close(fig)
    return fig
