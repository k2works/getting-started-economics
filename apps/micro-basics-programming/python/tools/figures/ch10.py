"""第 10 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter08.market import LinearMarket
from lib.chapter10.comparative import Country
from lib.chapter10.plot import plot_ppf, plot_tariff

_MARKET = LinearMarket(
    demand_intercept=100, demand_slope=-1, supply_intercept=-10, supply_slope=1
)

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch10-tariff": lambda: plot_tariff(_MARKET, 40, 10, 100, 100),
    "ch10-ppf": lambda: plot_ppf(
        Country("Large country", 4, 8), 80, Country("Small country", 20, 10), 40
    ),
}
