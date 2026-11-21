"""記事に載せる図の一覧（シリーズごとに書く）。

名前が、画像のファイル名（名前.png）になる。図を足すときは、ここに登録する。
登録のない画像は、`article_tools.render_figures` の検査で、孤立として失敗する。
"""

from collections.abc import Callable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import pandas as pd  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

from lib.chapter01.gdp import growth_accounting  # noqa: E402
from lib.chapter01.plot import (  # noqa: E402
    plot_growth_accounting,
    plot_value_added,
)
from lib.chapter02.plot import (  # noqa: E402
    plot_io_output,
    plot_three_way,
)
from lib.chapter03.indicators import (  # noqa: E402
    composite_index,
    diffusion_index,
    load_indicators,
)
from lib.chapter03.plot import (  # noqa: E402
    plot_business_indexes,
    plot_price_indexes,
)
from lib.chapter03.price_index import price_indexes  # noqa: E402
from lib.chapter04.plot import (  # noqa: E402
    plot_keynesian_cross,
    plot_multiplier_slopes,
)
from lib.chapter05.plot import plot_gap, plot_income_swing  # noqa: E402

# data/ は、tools/ の 1 つ上（アプリの直下）にある
_INDICATORS = load_indicators(
    Path(__file__).resolve().parents[1] / "data" / "ch03_indicators.csv"
)

# 記事に載せる図。名前が、画像のファイル名（名前.png）になる
FIGURES: dict[str, Callable[[], Figure]] = {
    "ch01-value-added": lambda: plot_value_added(
        ["Wheat", "Flour", "Bread"], [300, 700, 1000], [0, 300, 700]
    ),
    "ch01-growth-accounting": lambda: plot_growth_accounting(
        growth_accounting(6.0, 7.0, 0.4, 4.0, 0.6)
    ),
    "ch02-three-way": lambda: plot_three_way(
        {
            "Production": {"Industry A": 100, "Industry B": 200, "Industry C": 200},
            "Distribution": {
                "Compensation": 280,
                "Operating surplus": 120,
                "Depreciation": 80,
                "Taxes less subsidies": 20,
            },
            "Expenditure": {
                "Consumption": 290,
                "Government": 80,
                "Investment": 100,
                "Inventory": 10,
                "Net exports": 20,
            },
        }
    ),
    "ch02-io-output": lambda: plot_io_output(
        [[0.2, 0.3], [0.4, 0.1]], [100, 200], ["Manufacturing", "Services"]
    ),
    "ch03-price-indexes": lambda: plot_price_indexes(
        price_indexes(
            pd.DataFrame(
                {"bread": [100, 110, 121], "milk": [200, 180, 170]},
                index=["2020", "2021", "2022"],
            ),
            pd.DataFrame(
                {"bread": [10, 12, 14], "milk": [5, 4, 3]},
                index=["2020", "2021", "2022"],
            ),
            base="2020",
        )
    ),
    "ch03-business-indexes": lambda: plot_business_indexes(
        diffusion_index(_INDICATORS), composite_index(_INDICATORS, base="2025-01")
    ),
    "ch04-keynesian-cross": lambda: plot_keynesian_cross(
        mpc=0.6,
        autonomous_consumption=40,
        investment=30,
        government=30,
        net_exports=0,
        income_max=400,
    ),
    "ch04-multiplier-slopes": lambda: plot_multiplier_slopes(
        [0.6, 0.8], autonomous=100, income_max=500
    ),
    "ch05-deflationary-gap": lambda: plot_gap(
        mpc=0.6, autonomous=100, full_employment_income=300, income_max=400
    ),
    "ch05-income-swing": lambda: plot_income_swing(mpc=0.6, tax_rate=0.2, shock=10),
}
