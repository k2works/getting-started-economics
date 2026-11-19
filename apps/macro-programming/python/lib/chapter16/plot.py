"""景気循環の要素分解と、確率的ソロー・モデルの図。"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure


def plot_decomposition(shares: pd.Series) -> Figure:
    """GDP の変動に対する、TFP・資本・労働の寄与を、棒で描く。"""
    fig, ax = plt.subplots()
    ax.bar(list(shares.index), shares.to_numpy())
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_ylabel("Share of GDP variance")
    plt.close(fig)
    return fig


def plot_solow_simulation(dev: pd.DataFrame) -> Figure:
    """TFP・産出量・資本の、定常状態からの乖離（%）を、0 の線と一緒に描く。"""
    n = len(dev)
    fig, ax = plt.subplots()
    ax.plot(range(n), dev["a"].to_numpy(), label="TFP (a)")
    ax.plot(range(n), dev["y"].to_numpy(), label="Output (y)")
    ax.plot(range(n), dev["k"].to_numpy(), label="Capital (k)")
    ax.plot([0, n - 1], [0, 0], "--", color="gray", label="Zero")
    ax.set_xlabel("Period")
    ax.set_ylabel("Deviation from steady state (%)")
    ax.legend()
    plt.close(fig)
    return fig
