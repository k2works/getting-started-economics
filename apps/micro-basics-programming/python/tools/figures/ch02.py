"""第 2 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter02.plot import plot_optimal_choice, plot_price_change

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch02-optimal-choice": lambda: plot_optimal_choice(80, 2, 1, [400, 800, 1200], 45),
    "ch02-price-change": lambda: plot_price_change(80, [4, 2, 1], 1),
}
