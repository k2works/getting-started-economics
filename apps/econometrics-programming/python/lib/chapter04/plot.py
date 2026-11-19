"""診断図と、要約統計量が同じで形が違うデータの図。"""

from collections.abc import Mapping

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import ArrayLike, NDArray

from lib.chapter02.simple import fit_simple, fitted_values
from lib.chapter03.multiple import fit_ols, leverage
from lib.chapter04.diagnostics import (
    qq_points,
    standardized_residuals,
    studentized_residuals,
)


def plot_diagnostics(y: ArrayLike, x: ArrayLike) -> Figure:
    """回帰の診断図 4 点（残差と当てはめ値、Q-Q、スケール、てこ比）を描く。"""
    target = np.asarray(y, dtype=float)
    result = fit_ols(target, x)
    h = leverage(x)
    fitted = target - result.residuals
    fig, axes = plt.subplots(2, 2, figsize=(9, 7))
    ax = axes[0, 0]
    ax.plot(fitted, result.residuals, "o")
    ax.plot([fitted.min(), fitted.max()], [0, 0], "--", color="gray")
    ax.set_title("Residuals vs Fitted")
    ax.set_xlabel("Fitted values")
    ax.set_ylabel("Residuals")
    theoretical, ordered = qq_points(result.residuals)
    ax = axes[0, 1]
    ax.plot(theoretical, ordered, "o")
    ends = [float(theoretical.min()), float(theoretical.max())]
    ax.plot(ends, ends, "--", color="gray")
    ax.set_title("Normal Q-Q")
    ax.set_xlabel("Theoretical quantiles")
    ax.set_ylabel("Standardized residuals")
    ax = axes[1, 0]
    ax.plot(fitted, np.sqrt(np.abs(standardized_residuals(result))), "o")
    ax.set_title("Scale-Location")
    ax.set_xlabel("Fitted values")
    ax.set_ylabel("sqrt(|standardized residuals|)")
    ax = axes[1, 1]
    ax.plot(h, studentized_residuals(result, h), "o")
    ax.set_title("Residuals vs Leverage")
    ax.set_xlabel("Leverage")
    ax.set_ylabel("Studentized residuals")
    fig.tight_layout()
    plt.close(fig)
    return fig


def plot_same_summary(
    datasets: Mapping[str, tuple[NDArray[np.float64], NDArray[np.float64]]],
) -> Figure:
    """要約統計量が同じで形が違う 4 組のデータと、共通の回帰直線を描く。"""
    fig, axes = plt.subplots(2, 2, figsize=(8, 6), sharex=True, sharey=True)
    for ax, (name, (x, y)) in zip(axes.flat, datasets.items(), strict=True):
        ax.plot(x, y, "o", label="Data")
        ends = [float(x.min()), float(x.max())]
        ax.plot(ends, fitted_values(fit_simple(x, y), ends), label="Fitted line")
        ax.set_title(name)
    fig.tight_layout()
    plt.close(fig)
    return fig
