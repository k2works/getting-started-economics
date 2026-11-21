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
from lib.chapter06.plot import (  # noqa: E402
    plot_credit_creation,
    plot_money_multiplier,
)
from lib.chapter07.plot import plot_lm_curves, plot_money_market  # noqa: E402
from lib.chapter08.plot import plot_is_curves, plot_is_lm_equilibrium  # noqa: E402
from lib.chapter09.plot import (  # noqa: E402
    plot_liquidity_trap,
    plot_policy_shifts,
)
from lib.chapter10.ad_as import AdEconomy  # noqa: E402
from lib.chapter10.labor import LaborCurves  # noqa: E402
from lib.chapter10.plot import plot_ad_as, plot_labor_market  # noqa: E402
from lib.chapter11.okun import OkunFit, synthetic_unemployment_change  # noqa: E402
from lib.chapter11.plot import plot_okun, plot_phillips  # noqa: E402
from lib.chapter12.plot import (  # noqa: E402
    plot_accelerator,
    plot_consumption_theories,
)
from lib.chapter13.plot import (  # noqa: E402
    plot_money_and_prices,
    plot_net_exports,
)
from lib.chapter14.mundell_fleming import SmallOpenEconomy  # noqa: E402
from lib.chapter14.plot import (  # noqa: E402
    plot_fiscal_policy_by_regime,
    plot_policy_effects,
)

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
    "ch06-money-multiplier": lambda: plot_money_multiplier(
        [i / 100 for i in range(0, 51)], [0.01, 0.05, 0.1]
    ),
    "ch06-credit-creation": lambda: plot_credit_creation(
        base=110, cash_ratio=0.1, reserve_ratio=0.01, rounds=40
    ),
    "ch07-money-market": lambda: plot_money_market(
        income=1000, income_after=1200, real_money=250, k=0.5, h=100, interest_max=5
    ),
    "ch07-lm-curve": lambda: plot_lm_curves(
        incomes=list(range(600, 1501, 100)),
        real_money=250,
        real_money_after=300,
        k=0.5,
        h=100,
        floor=2.0,
    ),
    "ch08-is-curves": lambda: plot_is_curves(
        mpc=0.6, intercept=450, bs=[20, 40], interest_max=10
    ),
    "ch08-is-lm": lambda: plot_is_lm_equilibrium(
        mpc=0.6,
        b=20,
        intercept=450,
        k=0.5,
        h=100,
        real_money=250,
        income_min=600,
        income_max=1200,
    ),
    "ch09-policy-shifts": lambda: plot_policy_shifts(
        mpc=0.6,
        b=20,
        intercept=450,
        k=0.5,
        h=100,
        real_money=250,
        delta_government=10,
        delta_real_money=10,
        income_min=600,
        income_max=1200,
    ),
    "ch09-liquidity-trap": lambda: plot_liquidity_trap(
        mpc=0.6,
        b=20,
        intercept=450,
        trap_interest=2.5,
        delta_government=10,
        income_min=600,
        income_max=1200,
    ),
    "ch10-labor-market": lambda: plot_labor_market(
        LaborCurves(
            demand_intercept=100,
            demand_slope=10,
            supply_intercept=20,
            supply_slope=10,
        ),
        sticky_wage=6,
        wage_max=10,
    ),
    "ch10-ad-as": lambda: plot_ad_as(
        AdEconomy(mpc=0.6, b=20, intercept=450, k=0.5, h=100, nominal_money=250),
        full_employment_income=1000,
        base_income=480,
        slope=400,
        delta_government=10,
        price_min=0.8,
        price_max=1.6,
    ),
    "ch11-phillips-curve": lambda: plot_phillips(
        natural_rate=5, expected_inflations=[2, 4], beta=0.5, u_min=3, u_max=7
    ),
    "ch11-okun-law": lambda: plot_okun(
        [3.2, 1.5, 4.1, 0.8, 2.9, 5.0, -0.5, 3.6, 2.2, 4.5, 1.0, 3.0],
        synthetic_unemployment_change(
            [3.2, 1.5, 4.1, 0.8, 2.9, 5.0, -0.5, 3.6, 2.2, 4.5, 1.0, 3.0],
            slope=-0.4,
            intercept=1.2,
            noise=0.1,
            seed=0,
        ),
        OkunFit(slope=-0.4, intercept=1.2),
    ),
    "ch12-consumption-theories": lambda: plot_consumption_theories(
        [100, 100, 100, 130, 100, 100], 0.8, 0.2
    ),
    "ch12-accelerator": lambda: plot_accelerator(2, [100, 120, 140, 150, 155, 155]),
    "ch13-money-and-prices": lambda: plot_money_and_prices(
        4, [200, 400], [0, 100, 200, 300]
    ),
    "ch13-net-exports": lambda: plot_net_exports(
        [105, 115, 125, 135, 145], 20, 125, 0.4
    ),
    "ch14-fiscal-policy-by-regime": lambda: plot_fiscal_policy_by_regime(
        SmallOpenEconomy(
            mpc=0.6,
            b=20,
            intercept=400,
            n=50,
            k=0.5,
            h=100,
            real_money=250,
            world_rate=2.5,
            exchange_rate=1,
        ),
        delta_government=10,
        income_min=600,
        income_max=1200,
    ),
    "ch14-policy-effects": lambda: plot_policy_effects(
        SmallOpenEconomy(
            mpc=0.6,
            b=20,
            intercept=400,
            n=50,
            k=0.5,
            h=100,
            real_money=250,
            world_rate=2.5,
            exchange_rate=1,
        ),
        delta_government=10,
        delta_real_money=10,
    ),
}
