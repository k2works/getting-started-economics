"""第 15 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter11.monopoly import Monopoly
from lib.chapter15.plot import plot_natural_monopoly

_DEMAND = Monopoly(demand_intercept=100, demand_slope=1, marginal_cost=10)

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch15-natural-monopoly": lambda: plot_natural_monopoly(_DEMAND, 800, 100, 100),
}
