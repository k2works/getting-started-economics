"""第 13 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter13.plot import plot_money_and_prices, plot_net_exports

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch13-money-and-prices": lambda: plot_money_and_prices(
        4, [200, 400], [0, 100, 200, 300]
    ),
    "ch13-net-exports": lambda: plot_net_exports(
        [105, 115, 125, 135, 145], 20, 125, 0.4
    ),
}
