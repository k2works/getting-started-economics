"""第 11 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter11.monopoly import Monopoly
from lib.chapter11.plot import plot_long_run, plot_monopoly

_MONOPOLY = Monopoly(demand_intercept=100, demand_slope=1, marginal_cost=10)

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch11-monopoly": lambda: plot_monopoly(_MONOPOLY, 100, 100),
    "ch11-long-run": lambda: plot_long_run(_MONOPOLY, 1000, 100, 100),
}
