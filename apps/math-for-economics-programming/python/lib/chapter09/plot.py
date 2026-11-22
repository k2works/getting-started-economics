"""データと回帰直線（残差の線分つき）、残差と説明変数の散布図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter09.regression import (
    regression_design_matrix,
    regression_fitted_values,
    regression_residuals,
    simple_regression_coefficients,
)


def _fit_line(
    xs: Sequence[float], ys: Sequence[float]
) -> tuple[list[float], list[float]]:
    """単回帰の直線を、x の最小から最大まで結ぶ 2 点。"""
    intercept, slope = simple_regression_coefficients(xs, ys)
    ends = [min(xs), max(xs)]
    return ends, [intercept + slope * x for x in ends]


def plot_regression_with_residuals(xs: Sequence[float], ys: Sequence[float]) -> Figure:
    """データの点、単回帰の直線、各点から直線までの残差（縦の線分）。"""
    beta = list(simple_regression_coefficients(xs, ys))
    fitted = regression_fitted_values(regression_design_matrix([xs]), beta)
    fig, ax = plt.subplots()
    ax.plot(xs, ys, "o", color="C0", label="Data")
    ax.plot(*_fit_line(xs, ys), color="C1", label="Regression line")
    for i, (x, y, f) in enumerate(zip(xs, ys, fitted, strict=True)):
        label = "Residual" if i == 0 else "_nolegend_"
        ax.plot([x, x], [y, f], ":", color="C3", label=label, gid="residual")
    ax.set_xlabel("Price")
    ax.set_ylabel("Quantity")
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig


def plot_residuals_against_x(xs: Sequence[float], ys: Sequence[float]) -> Figure:
    """残差と x の散布図に、残差を x に回帰した直線（傾き 0）を重ねる。"""
    design = regression_design_matrix([xs])
    beta = list(simple_regression_coefficients(xs, ys))
    residuals = regression_residuals(design, ys, beta)
    fig, ax = plt.subplots()
    ax.plot(xs, residuals, "o", color="C3", label="Residuals")
    ax.plot(
        *_fit_line(xs, residuals), color="C1", label="Regression of residuals on price"
    )
    ax.set_xlabel("Price")
    ax.set_ylabel("Residual")
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig
