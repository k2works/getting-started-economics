"""線形確率モデル・ロジット・プロビットの曲線の図。"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray

from lib.chapter03.multiple import fit_ols
from lib.chapter14.discrete import fit_binary, predicted_probabilities


def plot_probability_curves(x: NDArray[np.float64], y: NDArray[np.float64]) -> Figure:
    """0 か 1 のデータと、線形確率モデルの直線、ロジット・プロビットの曲線を描く。"""
    grid = np.linspace(float(x.min()) - 1, float(x.max()) + 1, 100)
    ols = fit_ols(y, x).coefficients
    fig, ax = plt.subplots()
    ax.plot(x, y, "o", alpha=0.3, label="Data")
    ax.plot(grid, ols["const"] + ols["x1"] * grid, label="Linear probability")
    for link, name in (("logit", "Logit"), ("probit", "Probit")):
        fit = fit_binary(y, x, link)
        ax.plot(grid, predicted_probabilities(fit, grid), label=name)
    ax.set_xlabel("x")
    ax.set_ylabel("P(y = 1)")
    ax.legend()
    plt.close(fig)
    return fig
