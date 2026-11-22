"""第 8 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter08.plot import plot_income_expansion_paths, plot_utility_maximization

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch08-utility-maximum": lambda: plot_utility_maximization([3, 4], 120, 0.3),
    "ch08-income-expansion": lambda: plot_income_expansion_paths(
        [1, 2], [8, 16, 24, 32, 40], 0.5, 4
    ),
}
