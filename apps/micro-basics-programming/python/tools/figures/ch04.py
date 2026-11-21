"""第 4 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter04.plot import plot_cross_price, plot_slutsky

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch04-slutsky": lambda: plot_slutsky(80, 2, 0.5, 1, 100),
    "ch04-cross-price": lambda: plot_cross_price(80, 2, [0.5, 1, 1.5, 2, 2.5, 3, 4]),
}
