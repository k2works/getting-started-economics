"""記事に載せる図の一覧（シリーズごとに書く）。

名前が、画像のファイル名（名前.png）になる。図を足すときは、ここに登録する。
登録のない画像は、`tools/render_figures.py` の検査で、孤立として失敗する。
"""

from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

from lib.chapter01.plot import plot_densities  # noqa: E402
from lib.chapter02.plot import (  # noqa: E402
    plot_regression_line,
    plot_slope_distribution,
)
from lib.chapter02.simple import fit_simple, sampling_distribution  # noqa: E402
from lib.chapter03.multiple import (  # noqa: E402
    multicollinearity_experiment,
    partial_out,
)
from lib.chapter03.plot import plot_collinearity_distributions  # noqa: E402
from lib.chapter04.diagnostics import same_summary_datasets  # noqa: E402
from lib.chapter04.plot import plot_diagnostics, plot_same_summary  # noqa: E402
from lib.chapter05.inference import slope_intervals  # noqa: E402
from lib.chapter05.plot import plot_confidence_intervals  # noqa: E402
from lib.chapter06.asymptotics import consistency_experiment  # noqa: E402
from lib.chapter06.plot import plot_estimate_distributions  # noqa: E402


def _correlated_regressors() -> pd.DataFrame:
    """第 3 章: y = 1 + 2·x1 − x2 + u（x1 と x2 は相関する）から作った標本。"""
    rng = np.random.default_rng(0)
    x1 = rng.standard_normal(60)
    x2 = 0.5 * x1 + rng.standard_normal(60)
    y = 1 + 2 * x1 - x2 + rng.standard_normal(60)
    return pd.DataFrame({"y": y, "x1": x1, "x2": x2})


def _fwl_figure() -> Figure:
    df = _correlated_regressors()
    y_tilde = partial_out(df["y"], df[["x2"]])
    x_tilde = partial_out(df["x1"], df[["x2"]])
    return plot_regression_line(x_tilde, y_tilde, fit_simple(x_tilde, y_tilde))


def _fan_shaped_data() -> tuple[np.ndarray, np.ndarray]:
    """第 4 章: x が大きいほど誤差が大きい標本（不均一分散）。"""
    rng = np.random.default_rng(0)
    x = rng.uniform(0, 4, 100)
    return x, 1 + 2 * x + (0.1 + 0.5 * x) * rng.standard_normal(100)


# 記事に載せる図。名前が、画像のファイル名（名前.png）になる
FIGURES: dict[str, Callable[[], Figure]] = {
    "ch01-densities": plot_densities,
    "ch02-regression-line": lambda: plot_regression_line(
        [1, 2, 3, 4], [2, 4, 5, 9], fit_simple([1, 2, 3, 4], [2, 4, 5, 9])
    ),
    "ch02-slope-distribution": lambda: plot_slope_distribution(
        sampling_distribution(50, 2000, 1, 0.5, 1, np.random.default_rng(0))[
            "slope"
        ].tolist(),
        0.5,
    ),
    "ch03-fwl": _fwl_figure,
    "ch03-collinearity": lambda: plot_collinearity_distributions(
        multicollinearity_experiment(0.0, 50, 1000, np.random.default_rng(0))[
            "x1"
        ].tolist(),
        multicollinearity_experiment(0.9, 50, 1000, np.random.default_rng(0))[
            "x1"
        ].tolist(),
    ),
    "ch04-diagnostics": lambda: plot_diagnostics(*reversed(_fan_shaped_data())),
    "ch04-same-summary": lambda: plot_same_summary(same_summary_datasets()),
    "ch05-confidence-intervals": lambda: plot_confidence_intervals(
        slope_intervals(30, 100, 0.95, np.random.default_rng(0)), 0.5
    ),
    "ch06-estimate-distributions": lambda: plot_estimate_distributions(
        consistency_experiment([30, 100, 250, 500], 1000, np.random.default_rng(0)),
        0.5,
    ),
}
