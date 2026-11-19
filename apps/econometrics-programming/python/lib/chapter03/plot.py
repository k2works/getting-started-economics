"""多重共線性で、係数の推定値がばらつく様子の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def plot_collinearity_distributions(
    low: Sequence[float], high: Sequence[float], true_value: float = 1.0
) -> Figure:
    """相関が弱い場合と強い場合の、係数の推定値の分布を重ねて描く。"""
    fig, ax = plt.subplots()
    ax.hist(low, bins=20, alpha=0.6, label="Correlation low")
    ax.hist(high, bins=20, alpha=0.6, label="Correlation high")
    ax.axvline(true_value, color="red", label="True value")
    ax.set_xlabel("Estimated coefficient of x1")
    ax.set_ylabel("Frequency")
    ax.legend()
    plt.close(fig)
    return fig
