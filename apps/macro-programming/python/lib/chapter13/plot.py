"""データとモデルの特徴を比べる図。"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

MOMENT_LABELS = {
    "y_std": "Std of y",
    "p_std": "Std of p",
    "y_autocorr": "Autocorr of y",
    "p_autocorr": "Autocorr of p",
    "correlation": "Corr of y and p",
}


def plot_moment_comparison(data: dict[str, float], model: dict[str, float]) -> Figure:
    """データとモデルの、5 つの特徴（標準偏差・自己相関・相関）を、並べた棒で描く。"""
    positions = np.arange(len(MOMENT_LABELS))
    width = 0.38
    fig, ax = plt.subplots()
    ax.bar(positions - width / 2, [data[k] for k in MOMENT_LABELS], width, label="Data")
    ax.bar(
        positions + width / 2, [model[k] for k in MOMENT_LABELS], width, label="Model"
    )
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_xticks(positions, list(MOMENT_LABELS.values()), rotation=20, ha="right")
    ax.legend()
    fig.tight_layout()
    plt.close(fig)
    return fig
