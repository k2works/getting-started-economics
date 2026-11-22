"""第 7 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter07.plot import plot_budget_set, plot_labor_leisure

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch07-budget-set": lambda: plot_budget_set(
        [3, 4], 120, [[12, 12], [20, 15], [28, 18], [8, 21], [36, 3]]
    ),
    "ch07-labor-leisure": lambda: plot_labor_leisure(8, 12, 24, 40),
}
