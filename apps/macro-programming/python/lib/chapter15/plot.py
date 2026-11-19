"""IS-MP-PC モデルの図。"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

STEADY = {"pi": 2.0, "y": 100.0, "i": 4.0, "r": 2.0}


def _zero_line(ax: Axes, n: int) -> None:
    ax.plot([0, n - 1], [0, 0], "--", color="gray", label="Zero")


def plot_responses(df: pd.DataFrame) -> Figure:
    """インパルス反応を、定常状態（π* = 2、y* = 100、i = 4、r = 2）からの乖離で描く。"""
    n = len(df)
    fig, ax = plt.subplots()
    labels = {
        "pi": "Inflation",
        "y": "Output",
        "i": "Nominal rate",
        "r": "Real rate",
    }
    for column, label in labels.items():
        ax.plot(range(n), (df[column] - STEADY[column]).to_numpy(), label=label)
    _zero_line(ax, n)
    ax.set_xlabel("Period (shock at period 3)")
    ax.set_ylabel("Deviation from steady state")
    ax.legend()
    plt.close(fig)
    return fig


def plot_stance_comparison(case1: pd.DataFrame, case2: pd.DataFrame) -> Figure:
    """2 つの政策スタンスの、インフレ率と産出量の反応（定常状態からの乖離）を比べる。"""
    n = len(case1)
    fig, ax = plt.subplots()
    for number, df, style in ((1, case1, "-"), (2, case2, ":")):
        ax.plot(
            range(n),
            (df["pi"] - STEADY["pi"]).to_numpy(),
            style,
            color="tab:blue",
            label=f"Inflation (case {number})",
        )
        ax.plot(
            range(n),
            (df["y"] - STEADY["y"]).to_numpy(),
            style,
            color="tab:orange",
            label=f"Output (case {number})",
        )
    _zero_line(ax, n)
    ax.set_xlabel("Period (shock at period 3)")
    ax.set_ylabel("Deviation from steady state")
    ax.legend()
    plt.close(fig)
    return fig
