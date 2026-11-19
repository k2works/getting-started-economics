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
from lib.chapter07.dummies import draw_wage_sample  # noqa: E402
from lib.chapter07.plot import plot_group_lines  # noqa: E402
from lib.chapter08.hetero import (  # noqa: E402
    draw_fan_sample,
    standard_error_comparison,
)
from lib.chapter08.plot import plot_standard_errors  # noqa: E402
from lib.chapter09.did import (  # noqa: E402
    draw_did_sample,
    draw_panel,
    group_period_means,
)
from lib.chapter09.plot import plot_did  # noqa: E402
from lib.chapter10.panel import estimator_comparison  # noqa: E402
from lib.chapter10.plot import (  # noqa: E402
    plot_entity_lines,
    plot_estimate_comparison,
)
from lib.chapter11.endogeneity import (  # noqa: E402
    draw_market,
    simulate_measurement_error,
    simulate_omitted,
)
from lib.chapter11.plot import plot_market  # noqa: E402
from lib.chapter12.iv import (  # noqa: E402
    draw_iv_sample,
    weak_instrument_experiment,
)
from lib.chapter13.iv_tests import sargan_rejection_rate  # noqa: E402
from lib.chapter13.plot import plot_rejection_rates  # noqa: E402


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


def _wage_figure(interaction: bool) -> Figure:
    df = draw_wage_sample(80, np.random.default_rng(0))
    return plot_group_lines(
        df["educ"].to_numpy(dtype=float),
        df["lwage"].to_numpy(),
        df["female"].to_numpy(dtype=float),
        interaction,
    )


def _fan_regression() -> Figure:
    x, y = draw_fan_sample(100, np.random.default_rng(0), True)
    return plot_regression_line(x, y, fit_simple(x, y))


def _standard_error_figure() -> Figure:
    r = standard_error_comparison(50, 2000, True, np.random.default_rng(0))
    return plot_standard_errors(
        {
            "Actual (SD of estimates)": r["sd"],
            "Classical": r["classical"],
            "Robust (HC1)": r["hc1"],
        }
    )


def _measurement_error_figure() -> Figure:
    estimates = pd.DataFrame(
        {
            "error sd 0.5": simulate_measurement_error(
                500, 0.5, 1000, np.random.default_rng(0)
            ),
            "error sd 1.0": simulate_measurement_error(
                500, 1.0, 1000, np.random.default_rng(0)
            ),
        }
    )
    return plot_estimate_comparison(estimates, 1.0)


def _first_stage_figure() -> Figure:
    sample = draw_iv_sample(200, 1.0, 0.5, np.random.default_rng(0))
    z, x = sample["z"].to_numpy(), sample["x"].to_numpy()
    return plot_regression_line(z, x, fit_simple(z, x))


def _iv_distribution_figure() -> Figure:
    strong = weak_instrument_experiment(100, 1.0, 1000, np.random.default_rng(0))
    weak = weak_instrument_experiment(100, 0.1, 1000, np.random.default_rng(0))
    estimates = pd.DataFrame(
        {"strong": strong["iv"].clip(-1, 3), "weak": weak["iv"].clip(-1, 3)}
    )
    return plot_estimate_comparison(estimates, 1.0)


def _rejection_figure() -> Figure:
    rates = {
        f"Invalid {invalid}": sargan_rejection_rate(
            500, invalid, 500, 0.05, np.random.default_rng(0)
        )
        for invalid in (0.0, 0.1, 0.3)
    }
    return plot_rejection_rates(rates, 0.05)


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
    "ch07-intercept-shift": lambda: _wage_figure(False),
    "ch07-interaction": lambda: _wage_figure(True),
    "ch08-fan-regression": _fan_regression,
    "ch08-standard-errors": _standard_error_figure,
    "ch09-did": lambda: plot_did(
        group_period_means(draw_did_sample(200, 1.5, np.random.default_rng(0)))
    ),
    "ch10-entity-lines": lambda: plot_entity_lines(
        draw_panel(30, 5, 1.0, np.random.default_rng(0)), 5
    ),
    "ch10-estimate-comparison": lambda: plot_estimate_comparison(
        estimator_comparison(200, 5, 1.0, 300, np.random.default_rng(0)), 1.0
    ),
    "ch11-omitted-variable": lambda: plot_estimate_comparison(
        simulate_omitted(200, 0.5, 1000, np.random.default_rng(0)), 1.0
    ),
    "ch11-measurement-error": _measurement_error_figure,
    "ch11-market": lambda: plot_market(
        draw_market(100, 2.0, 1.0, np.random.default_rng(0))
    ),
    "ch12-first-stage": _first_stage_figure,
    "ch12-iv-distributions": _iv_distribution_figure,
    "ch13-sargan-rejection": _rejection_figure,
}
