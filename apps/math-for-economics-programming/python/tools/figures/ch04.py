"""第 4 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter04.plot import plot_bond_prices, plot_partial_sums

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch04-partial-sums": lambda: plot_partial_sums(1, 0.5, 10),
    "ch04-bond-prices": lambda: plot_bond_prices(
        100, 5, 10, [k / 1000 for k in range(5, 101, 5)]
    ),
}
