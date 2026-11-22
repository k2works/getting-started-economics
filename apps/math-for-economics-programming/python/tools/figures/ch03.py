"""第 3 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter03.plot import plot_compound_growth

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch03-compound-growth": lambda: plot_compound_growth(100, 0.08, 40),
}
