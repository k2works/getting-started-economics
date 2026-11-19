"""標本選択と、OLS・ヘックマンの直線の図。"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from lib.chapter03.multiple import fit_ols
from lib.chapter16.heckit import heckit_two_step


def plot_selection(df: pd.DataFrame) -> Figure:
    """選択された人のデータと、真の直線、OLS（選択された標本）、ヘックマンの直線を描く。"""
    chosen = df[df["selected"] == 1]
    ends = np.array([float(df["x"].min()), float(df["x"].max())])
    ols = fit_ols(chosen["y"], chosen[["x"]]).coefficients
    heckit = heckit_two_step(df, ["x"], ["x", "z"]).coefficients
    fig, ax = plt.subplots()
    ax.plot(chosen["x"], chosen["y"], "o", alpha=0.3, label="Selected")
    ax.plot(ends, 1 + 2 * ends, "--", label="True line")
    ax.plot(ends, ols["const"] + ols["x"] * ends, label="OLS (selected)")
    ax.plot(ends, heckit["const"] + heckit["x"] * ends, label="Heckit")
    ax.set_xlabel("x")
    ax.set_ylabel("y (observed only if selected)")
    ax.legend()
    plt.close(fig)
    return fig
