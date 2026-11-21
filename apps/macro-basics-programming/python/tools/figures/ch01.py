"""第 1 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter01.gdp import growth_accounting
from lib.chapter01.plot import plot_growth_accounting, plot_value_added

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch01-value-added": lambda: plot_value_added(
        ["Wheat", "Flour", "Bread"], [300, 700, 1000], [0, 300, 700]
    ),
    "ch01-growth-accounting": lambda: plot_growth_accounting(
        growth_accounting(6.0, 7.0, 0.4, 4.0, 0.6)
    ),
}
