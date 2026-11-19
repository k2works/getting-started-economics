"""収斂の図。"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure


def plot_beta_over_time(betas: pd.Series) -> Figure:
    """開始年ごとの傾き β（収斂の強さ）を描く。0 より下なら、収斂している。"""
    fig, ax = plt.subplots()
    ax.plot(betas.index, betas.to_numpy(), "o-", markersize=3, label="Beta")
    ax.plot(
        [betas.index.min(), betas.index.max()], [0, 0], "--", color="gray", label="Zero"
    )
    ax.set_xlabel("Start year")
    ax.set_ylabel("Beta (growth on initial log income)")
    ax.legend()
    plt.close(fig)
    return fig
