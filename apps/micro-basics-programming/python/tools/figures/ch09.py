"""第 9 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter08.market import LinearMarket
from lib.chapter09.plot import plot_surplus, plot_tax

_MARKET = LinearMarket(
    demand_intercept=100, demand_slope=-1, supply_intercept=-10, supply_slope=1
)

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch09-surplus": lambda: plot_surplus(_MARKET, 100, 100),
    "ch09-tax": lambda: plot_tax(_MARKET, 9, 100, 100),
}
