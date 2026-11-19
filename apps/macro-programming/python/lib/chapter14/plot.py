"""インパルス反応とシミュレーションの図。"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure


def _plot_paths(df: pd.DataFrame, xlabel: str) -> Figure:
    n = len(df)
    fig, ax = plt.subplots()
    ax.plot(range(n), df["y"].to_numpy(), label="Output (y)")
    ax.plot(range(n), df["p"].to_numpy(), label="Price (p)")
    ax.plot([0, n - 1], [0, 0], "--", color="gray", label="Zero")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Deviation from trend (%)")
    ax.legend()
    plt.close(fig)
    return fig


def plot_impulse_response(df: pd.DataFrame) -> Figure:
    """1 期間のショックへの、産出量と物価の反応を、0 の線と一緒に描く。"""
    return _plot_paths(df, "Period (shock at period 3)")


def plot_simulation(df: pd.DataFrame) -> Figure:
    """確率的シミュレーションの、産出量と物価の推移を、0 の線と一緒に描く。"""
    return _plot_paths(df, "Period")
