"""第 1 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter01.plot import plot_harvest_paradox, plot_market

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch01-market-surplus": lambda: plot_market(120, 2, 0, 1),
    "ch01-harvest-paradox": lambda: plot_harvest_paradox(100, 0.5, 10, 1, 40),
}
