"""オークンの法則とフィリップス曲線の図。"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure


def plot_rolling_slope(slopes: pd.Series) -> Figure:
    """窓をずらしながら求めた傾きの推移を、0 の線と一緒に描く。"""
    n = len(slopes)
    fig, ax = plt.subplots()
    ax.plot(range(n), slopes.to_numpy(), label="Slope")
    ax.plot([0, n - 1], [0, 0], "--", color="gray", label="Zero")
    ax.set_xlabel("Window (end quarter, in order)")
    ax.set_ylabel("Slope")
    ax.legend()
    plt.close(fig)
    return fig
