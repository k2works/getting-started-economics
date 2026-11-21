"""第 1 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter01.plot import plot_indifference_curves, plot_special_utilities

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch01-indifference-curves": lambda: plot_indifference_curves(
        [400, 800, 1200], 5, 80
    ),
    "ch01-special-utilities": lambda: plot_special_utilities(),
}
