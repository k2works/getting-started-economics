"""第 14 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter14.plot import plot_bonus, plot_signal

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch14-signal": lambda: plot_signal(100, 60, 10, 20, 6),
    "ch14-bonus": lambda: plot_bonus(0.8, 0.4, 10, 60),
}
