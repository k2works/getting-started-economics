"""厳密な経路と、線形近似の経路を比べる図。"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure


def plot_exact_vs_linear(df: pd.DataFrame) -> Figure:
    """資本の乖離（%）の、厳密な経路（実線）と線形近似の経路（点線）を、描く。"""
    n = len(df)
    fig, ax = plt.subplots()
    ax.plot(range(n), df["exact"].to_numpy(), label="Exact")
    ax.plot(range(n), df["linear"].to_numpy(), ":", label="Linear approximation")
    ax.plot([0, n - 1], [0, 0], "--", color="gray", label="Zero")
    ax.set_xlabel("Period")
    ax.set_ylabel("Capital, deviation from steady state (%)")
    ax.legend()
    plt.close(fig)
    return fig
