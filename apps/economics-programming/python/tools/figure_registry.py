"""記事に載せる図の一覧（シリーズごとに書く）。

名前が、画像のファイル名（名前.png）になる。図を足すときは、ここに登録する。
登録のない画像は、`tools/render_figures.py` の検査で、孤立として失敗する。
"""

import random
from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

from matplotlib.figure import Figure  # noqa: E402

from lib.chapter01.plot import plot_demand_curve  # noqa: E402
from lib.chapter02.plot import plot_elasticity_regions  # noqa: E402
from lib.chapter03.plot import plot_schedules  # noqa: E402
from lib.chapter03.schedule import demand_schedule, supply_schedule  # noqa: E402
from lib.chapter04.plot import plot_cost_curves  # noqa: E402
from lib.chapter05.adjustment import walras_path  # noqa: E402
from lib.chapter05.plot import plot_price_paths  # noqa: E402
from lib.chapter06.bisection import make_excess_demand  # noqa: E402
from lib.chapter06.plot import plot_bisection  # noqa: E402
from lib.chapter07.plot import draw_market, draw_tax_wedge  # noqa: E402
from lib.chapter08.simulation import plot_histogram, sample_means  # noqa: E402
from lib.chapter09.plot import plot_keynesian_cross  # noqa: E402
from lib.chapter10.plot import (  # noqa: E402
    plot_profit_maximization,
    plot_utility_maximization,
)
from lib.chapter11.economy import load_economy  # noqa: E402
from lib.chapter12.charts import plot_gdp_chart, plot_growth_chart  # noqa: E402
from lib.chapter13.islm import IsLmModel, plot_islm  # noqa: E402
from lib.chapter14.plot import plot_adas, plot_phillips_curve  # noqa: E402
from lib.chapter15.plot import (  # noqa: E402
    plot_cournot,
    plot_externality,
    plot_monopoly,
)

# 記事に載せる図。名前が、画像のファイル名（名前.png）になる
FIGURES: dict[str, Callable[[], Figure]] = {
    "ch01-demand": lambda: plot_demand_curve(100, 2),
    "ch02-elasticity": lambda: plot_elasticity_regions(100, 2),
    "ch03-schedules": lambda: plot_schedules(
        demand_schedule([0, 10, 20, 30], 100, 2),
        supply_schedule([0, 10, 20, 30], 0, 3),
    ),
    "ch05-price-paths": lambda: plot_price_paths(
        {
            f"step {step}": walras_path(lambda p: 100 - 2 * p, lambda p: 3 * p, 0, step)
            for step in (0.1, 0.3)
        },
        equilibrium_price=20,
    ),
    "ch06-bisection": lambda: plot_bisection(
        make_excess_demand(100, 2, 0, 3), 0, 100, steps=6
    ),
    "ch10-utility": lambda: plot_utility_maximization(2, 4, 40),
    "ch10-profit": lambda: plot_profit_maximization(15),
    "ch14-adas": lambda: plot_adas(IsLmModel(), 1250, after=IsLmModel(government=120)),
    "ch14-phillips": lambda: plot_phillips_curve(4, 2, 0.5, new_expected_inflation=3),
    "ch15-cournot": lambda: plot_cournot(100, 2, 10),
    "ch15-externality": lambda: plot_externality(100, 2, 0, 3, 5),
    "ch04-cost-curves": lambda: plot_cost_curves(),
    "ch07-market": lambda: draw_market(100, 2, 0, 3),
    "ch07-tax-wedge": lambda: draw_tax_wedge(100, 2, 0, 3, 5),
    "ch08-sample-means": lambda: plot_histogram(
        sample_means(30, 1000, random.Random(0)), bins=20
    ),
    "ch09-keynesian-cross": lambda: plot_keynesian_cross(
        20, 0.8, 30, new_investment=40
    ),
    "ch12-gdp": lambda: plot_gdp_chart(load_economy()),
    "ch12-growth": lambda: plot_growth_chart(load_economy()),
    "ch13-islm-fiscal": lambda: plot_islm(IsLmModel(), after=IsLmModel(government=120)),
    "ch13-islm-monetary": lambda: plot_islm(
        IsLmModel(), after=IsLmModel(money_supply=575)
    ),
    "ch15-monopoly": lambda: plot_monopoly(100, 2, 10),
}
