"""市場のデータと、需要・供給・OLS の直線の図。"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from lib.chapter02.simple import fit_simple, fitted_values


def plot_market(market: pd.DataFrame) -> Figure:
    """均衡の点と、OLS の直線、真の需要曲線（q = 10 − p）、供給曲線（q = p）。"""
    fig, ax = plt.subplots()
    ax.plot(market["p"], market["q"], "o", alpha=0.4, label="Data")
    ends = np.array([market["p"].min(), market["p"].max()])
    ax.plot(
        ends,
        fitted_values(fit_simple(market["p"], market["q"]), ends),
        color="black",
        label="OLS fit",
    )
    ax.plot(ends, 10 - ends, "--", label="Demand (slope -1)")
    ax.plot(ends, ends, "--", label="Supply (slope +1)")
    ax.set_xlabel("Price")
    ax.set_ylabel("Quantity")
    ax.legend()
    plt.close(fig)
    return fig
