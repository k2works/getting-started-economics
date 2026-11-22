"""第 2 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter02.plot import plot_cournot_convergence, plot_monopoly_profit

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch02-monopoly-profit": lambda: plot_monopoly_profit(100, 1, 20),
    "ch02-cournot-convergence": lambda: plot_cournot_convergence(100, 1, 20, 10),
}
