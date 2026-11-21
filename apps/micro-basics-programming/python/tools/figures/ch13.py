"""第 13 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter11.monopoly import Monopoly
from lib.chapter13.externality import ExternalityMarket
from lib.chapter13.plot import plot_externality, plot_natural_monopoly

_POLLUTION = ExternalityMarket(
    demand_intercept=100,
    demand_slope=1,
    cost_intercept=10,
    cost_slope=1,
    external_cost=20,
)
_DEMAND = Monopoly(demand_intercept=100, demand_slope=1, marginal_cost=10)

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch13-externality": lambda: plot_externality(_POLLUTION, 100, 100),
    "ch13-natural-monopoly": lambda: plot_natural_monopoly(_DEMAND, 800, 100, 100),
}
