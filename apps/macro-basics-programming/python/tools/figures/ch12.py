"""第 12 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter12.plot import plot_accelerator, plot_consumption_theories

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch12-consumption-theories": lambda: plot_consumption_theories(
        [100, 100, 100, 130, 100, 100], 0.8, 0.2
    ),
    "ch12-accelerator": lambda: plot_accelerator(2, [100, 120, 140, 150, 155, 155]),
}
