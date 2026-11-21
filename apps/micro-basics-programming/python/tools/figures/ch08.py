"""第 8 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter08.market import LinearMarket
from lib.chapter08.plot import plot_adjustment, plot_market, plot_shift

_MARKET = LinearMarket(
    demand_intercept=100, demand_slope=-1, supply_intercept=-10, supply_slope=1
)

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch08-market": lambda: plot_market(_MARKET, 100, 100),
    "ch08-demand-shift": lambda: plot_shift(_MARKET, 20, 100, 100),
    "ch08-adjustment": lambda: plot_adjustment(_MARKET, 80, 0, 0.25, 12),
}
