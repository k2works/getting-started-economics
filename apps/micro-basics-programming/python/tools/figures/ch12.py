"""第 12 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter12.kinked import KinkedDemand
from lib.chapter12.plot import plot_kinked, plot_trigger

_KINKED = KinkedDemand(kink_quantity=40, kink_price=50, upper_slope=0.5, lower_slope=2)

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch12-kinked": lambda: plot_kinked(_KINKED, 100, 80, 10, 25),
    "ch12-trigger": lambda: plot_trigger(5, 3, 1, 0.95, 100, 60),
}
