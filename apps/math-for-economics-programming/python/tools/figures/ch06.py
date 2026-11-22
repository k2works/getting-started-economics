"""第 6 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter06.plot import plot_elasticity_regions, plot_taylor_exp

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch06-elasticity-regions": lambda: plot_elasticity_regions(100, 2),
    "ch06-taylor-exp": lambda: plot_taylor_exp(-2, 2, [1, 2, 3, 5], 1),
}
