"""発展会計の図。"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from lib.chapter01.accounting import with_tfp


def plot_gap_decomposition(row: pd.Series) -> Figure:
    """基準の国との所得の差（対数）を、資本・人的資本・TFP の棒で描く。

    row は、`income_gap` の 1 行。3 本の棒の高さの和が、所得の差になる。
    """
    values = [row["capital"], row["human_capital"], row["tfp"]]
    fig, ax = plt.subplots()
    ax.bar(["Capital", "Human capital", "TFP"], values)
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_ylabel("Contribution to the income gap (log)")
    plt.close(fig)
    return fig


def plot_income_and_tfp(df: pd.DataFrame, alpha: float) -> Figure:
    """国ごとの、対数の TFP（横軸）と対数の所得（縦軸）の散布図と、近似直線を描く。"""
    table = with_tfp(df, alpha)
    x = np.log(table["tfp"].to_numpy())
    y = np.log(table["y"].to_numpy())
    slope, intercept = np.polyfit(x, y, 1)
    ends = np.array([x.min(), x.max()])

    fig, ax = plt.subplots()
    ax.plot(x, y, "o", label="Countries")
    ax.plot(ends, intercept + slope * ends, label="Fitted line")
    ax.set_xlabel("TFP (log)")
    ax.set_ylabel("Income per worker (log)")
    ax.legend()
    plt.close(fig)
    return fig
