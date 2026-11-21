"""第 6 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter06.plot import plot_cost_minimization, plot_marginal_product

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch06-cost-minimization": lambda: plot_cost_minimization([5, 10, 15], 10, 1, 4),
    "ch06-marginal-product": lambda: plot_marginal_product(5, 80),
}
