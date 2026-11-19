"""確率過程の図。"""

from collections.abc import Mapping, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray


def plot_series(series: Mapping[str, NDArray[np.float64]]) -> Figure:
    """系列（名前 -> 値の推移）を、時点を横軸にして、重ねて描く。"""
    fig, ax = plt.subplots()
    for name, values in series.items():
        ax.plot(range(len(values)), values, label=name)
    ax.set_xlabel("Period t")
    ax.set_ylabel("x(t)")
    ax.legend()
    plt.close(fig)
    return fig


def plot_acf(
    sample: Sequence[float] | NDArray[np.float64],
    theory: Sequence[float] | NDArray[np.float64],
) -> Figure:
    """標本の自己相関（棒）と、理論値（線）を、ラグごとに描く。"""
    lags = list(range(len(sample)))
    fig, ax = plt.subplots()
    ax.bar(lags, list(sample), label="Sample")
    ax.plot(lags, list(theory), "o-", color="tab:red", label="Theory")
    ax.set_xlabel("Lag")
    ax.set_ylabel("Autocorrelation")
    ax.legend()
    plt.close(fig)
    return fig
