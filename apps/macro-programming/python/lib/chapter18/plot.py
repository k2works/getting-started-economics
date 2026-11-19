"""RBC モデルのインパルス反応の図。"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

LABELS = {
    "y": "Output",
    "c": "Consumption",
    "i": "Investment",
    "k": "Capital",
    "l": "Labour",
}


def plot_rbc_responses(df: pd.DataFrame) -> Figure:
    """産出量・消費・投資・資本（と、あれば労働）の反応を、0 の線と一緒に描く。"""
    n = len(df)
    fig, ax = plt.subplots()
    for column, label in LABELS.items():
        if column in df.columns:
            ax.plot(range(n), df[column].to_numpy(), label=label)
    ax.plot([0, n - 1], [0, 0], "--", color="gray", label="Zero")
    ax.set_xlabel("Period (shock at period 3)")
    ax.set_ylabel("Deviation from steady state (%)")
    ax.legend()
    plt.close(fig)
    return fig
