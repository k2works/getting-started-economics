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
from lib.chapter08.plot import plot_acf, plot_series  # noqa: E402
from lib.chapter08.stochastic import (  # noqa: E402
    ar1_autocorrelation,
    ar1_series,
    autocorrelation_function,
)
from lib.chapter09.cycles import (  # noqa: E402
    cycle,
    cycle_statistics,
    load_quarterly,
    log_cycle,
)
from lib.chapter09.plot import (  # noqa: E402
    plot_cycle,
    plot_trend,
    plot_volatility,
)
from lib.chapter10.okun_phillips import rolling_slope  # noqa: E402
from lib.chapter10.plot import plot_rolling_slope  # noqa: E402
from lib.chapter11.money import load_money_panel  # noqa: E402
from lib.chapter12.exchange import load_exchange, regime_statistics  # noqa: E402
from lib.chapter12.plot import (  # noqa: E402
    plot_exchange_rates,
    plot_regime_volatility,
)
from lib.chapter13.adas import (  # noqa: E402
    AdasParameters,
    adas_cycles,
    calibrate,
    data_features,
    load_adas_quarterly,
    model_moments,
)
from lib.chapter13.plot import plot_moment_comparison  # noqa: E402
from lib.chapter14.plot import plot_impulse_response, plot_simulation  # noqa: E402
from lib.chapter14.simulation import impulse_response, simulate  # noqa: E402
from lib.chapter15.ismppc import IsMpPcParameters  # noqa: E402
from lib.chapter15.ismppc import impulse_response as ismppc_impulse  # noqa: E402
from lib.chapter15.plot import plot_responses, plot_stance_comparison  # noqa: E402
from lib.chapter16.plot import plot_decomposition, plot_solow_simulation  # noqa: E402
from lib.chapter16.solow_stochastic import (  # noqa: E402
    SolowParameters,
    business_cycle_components,
    decompose_business_cycle,
    load_solow_quarterly,
    log_deviations,
    stochastic_solow,
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
    "ch08-ar1-paths": lambda: plot_series(
        {
            f"rho = {rho}": ar1_series(rho, 1.0, 100, np.random.default_rng(0))
            for rho in (0.0, 0.5, 0.95)
        }
    ),
    "ch08-acf": lambda: plot_acf(
        autocorrelation_function(
            ar1_series(0.8, 1.0, 5000, np.random.default_rng(1)), 10
        ),
        [ar1_autocorrelation(0.8, lag) for lag in range(11)],
    ),
    "ch09-gdp-trend": lambda: plot_trend(pd.Series(load_quarterly()["gdp"])),
    "ch09-cycles": lambda: plot_cycle(
        pd.DataFrame(
            {
                name: log_cycle(pd.Series(load_quarterly()[name]))
                for name in ("gdp", "consumption", "investment")
            }
        )
    ),
    "ch09-volatility": lambda: plot_volatility(cycle_statistics(load_quarterly())),
    "ch10-okun": lambda: plot_regression(
        log_cycle(pd.Series(load_quarterly()["gdp"])),
        cycle(pd.Series(load_quarterly()["unemployment"])),
        xlabel="GDP cycle (%)",
        ylabel="Unemployment cycle (pp)",
        label="Quarters",
    ),
    "ch10-phillips": lambda: plot_regression(
        cycle(pd.Series(load_quarterly()["unemployment"])),
        pd.Series(load_quarterly()["inflation"]),
        xlabel="Unemployment cycle (pp)",
        ylabel="Inflation (%)",
        label="Quarters",
    ),
    "ch10-rolling-slope": lambda: plot_rolling_slope(
        rolling_slope(
            cycle(pd.Series(load_quarterly()["unemployment"])),
            pd.Series(load_quarterly()["inflation"]),
            window=40,
        )
    ),
    "ch11-money-inflation": lambda: plot_regression(
        pd.Series(load_money_panel()["money_growth"]),
        pd.Series(load_money_panel()["inflation"]),
        xlabel="Money growth (% per year)",
        ylabel="Inflation (% per year)",
        label="Country-years",
    ),
    "ch11-money-inflation-moderate": lambda: plot_regression(
        pd.Series(
            load_money_panel()[load_money_panel()["inflation"] <= 100]["money_growth"]
        ),
        pd.Series(
            load_money_panel()[load_money_panel()["inflation"] <= 100]["inflation"]
        ),
        xlabel="Money growth (% per year)",
        ylabel="Inflation (% per year)",
        label="Country-years",
    ),
    "ch12-exchange-rates": lambda: plot_exchange_rates(load_exchange(), "1973Q1"),
    "ch12-regime-volatility": lambda: plot_regime_volatility(
        regime_statistics(load_exchange(), "1973Q1")
    ),
    "ch13-price-persistence": lambda: plot_regression(
        pd.Series(adas_cycles(load_adas_quarterly())["p"].shift().dropna()),
        pd.Series(adas_cycles(load_adas_quarterly())["p"].iloc[1:]),
        xlabel="Price deviation, previous quarter (%)",
        ylabel="Price deviation (%)",
        label="Quarters",
    ),
    "ch13-data-vs-model": lambda: plot_moment_comparison(
        data_features(
            adas_cycles(load_adas_quarterly())["y"],
            adas_cycles(load_adas_quarterly())["p"],
        ),
        model_moments(
            calibrate(
                adas_cycles(load_adas_quarterly())["y"],
                adas_cycles(load_adas_quarterly())["p"],
            )
        ),
    ),
    "ch14-impulse-demand": lambda: plot_impulse_response(
        impulse_response(AdasParameters(0.8, 0.3, 1.5, 1.2), u=1.0)
    ),
    "ch14-impulse-supply": lambda: plot_impulse_response(
        impulse_response(AdasParameters(0.8, 0.3, 1.5, 1.2), v=1.0)
    ),
    "ch14-simulation": lambda: plot_simulation(
        simulate(AdasParameters(0.8, 0.3, 1.5, 1.2), 100, np.random.default_rng(0))
    ),
    "ch15-impulse-pc": lambda: plot_responses(
        ismppc_impulse(IsMpPcParameters(), shock_pc=1.0)
    ),
    "ch15-impulse-mp": lambda: plot_responses(
        ismppc_impulse(IsMpPcParameters(), shock_mp=1.0)
    ),
    "ch15-policy-stance": lambda: plot_stance_comparison(
        ismppc_impulse(IsMpPcParameters(), shock_pc=1.0),
        ismppc_impulse(IsMpPcParameters(c=0.5, d=1.5), shock_pc=1.0),
    ),
    "ch16-decomposition": lambda: plot_decomposition(
        decompose_business_cycle(
            business_cycle_components(load_solow_quarterly(), 0.36), 0.36
        )
    ),
    "ch16-solow-simulation": lambda: plot_solow_simulation(
        log_deviations(
            stochastic_solow(
                SolowParameters(rho=0.6, sigma=0.008), 200, np.random.default_rng(123)
            ),
            SolowParameters(rho=0.6, sigma=0.008),
        )
    ),
    "ch03-regression": lambda: plot_regression(
        np.log(load_countries()["k"]),
        np.log(load_countries()["y"]),
        xlabel="Physical capital (log)",
        ylabel="Income per worker (log)",
    ),
}
