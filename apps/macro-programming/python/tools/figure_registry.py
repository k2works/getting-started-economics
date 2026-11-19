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

from lib.chapter01.accounting import income_gap, load_countries  # noqa: E402
from lib.chapter01.plot import (  # noqa: E402
    plot_gap_decomposition,
    plot_income_and_tfp,
)
from lib.chapter02.growth import growth_contribution, load_panel  # noqa: E402
from lib.chapter02.plot import (  # noqa: E402
    plot_growth_contributions,
    plot_tfp_growth,
)
from lib.chapter03.plot import plot_regression  # noqa: E402
from lib.chapter04.difference import linear_path  # noqa: E402
from lib.chapter04.plot import plot_cobweb, plot_paths  # noqa: E402
from lib.chapter05.plot import (  # noqa: E402
    plot_solow_convergence,
    plot_solow_diagram,
)
from lib.chapter06.convergence import (  # noqa: E402
    beta_by_start_year,
    income_growth,
)
from lib.chapter06.plot import plot_beta_over_time  # noqa: E402
from lib.chapter07.plot import plot_relative_price_levels  # noqa: E402
from lib.chapter07.ppp import (  # noqa: E402
    load_prices,
    relative_price_levels,
)

# 記事に載せる図。名前が、画像のファイル名（名前.png）になる
FIGURES: dict[str, Callable[[], Figure]] = {
    "ch01-gap-decomposition": lambda: plot_gap_decomposition(
        pd.Series(income_gap(load_countries(), "C01", 1 / 3).loc["C24"])
    ),
    "ch01-income-and-tfp": lambda: plot_income_and_tfp(load_countries(), 1 / 3),
    "ch02-growth-contributions": lambda: plot_growth_contributions(
        growth_contribution(load_panel(), 1990, 2019, 1 / 3)
    ),
    "ch02-tfp-growth": lambda: plot_tfp_growth(
        growth_contribution(load_panel(), 1990, 2019, 1 / 3)
    ),
    "ch04-difference-paths": lambda: plot_paths(
        {
            "a = 0.5": linear_path(0.5, 1, 0, 12),
            "a = -0.8": linear_path(-0.8, 3.6, 0, 12),
            "a = 1.1": linear_path(1.1, -0.2, 0, 12),
        },
        steady_state=2,
    ),
    "ch04-cobweb-stable": lambda: plot_cobweb(100, 3, 0, 2, 10, 6),
    "ch04-cobweb-unstable": lambda: plot_cobweb(100, 2, 0, 3, 19, 5),
    "ch05-solow-diagram": lambda: plot_solow_diagram(0.2, 0.05, 0.5),
    "ch05-solow-convergence": lambda: plot_solow_convergence(
        [2, 25], 0.2, 0.05, 0.5, periods=150
    ),
    "ch06-convergence": lambda: plot_regression(
        np.log(load_panel().xs(1990, level="year")["y"]),
        income_growth(load_panel(), 1990, 2019),
        xlabel="Initial income in 1990 (log)",
        ylabel="Growth rate 1990-2019 (% per year)",
    ),
    "ch06-beta-over-time": lambda: plot_beta_over_time(
        beta_by_start_year(load_panel(), 10)
    ),
    "ch07-relative-prices": lambda: plot_relative_price_levels(
        relative_price_levels(load_prices())
    ),
    "ch07-penn-effect": lambda: plot_regression(
        np.log(load_prices()["income"]),
        np.log(relative_price_levels(load_prices())),
        xlabel="Income per capita (log)",
        ylabel="Relative price level (log)",
    ),
    "ch03-regression": lambda: plot_regression(
        np.log(load_countries()["k"]),
        np.log(load_countries()["y"]),
        xlabel="Physical capital (log)",
        ylabel="Income per worker (log)",
    ),
}
