"""第 14 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter14.externality import ExternalityMarket
from lib.chapter14.plot import plot_externality

_POLLUTION = ExternalityMarket(
    demand_intercept=100,
    demand_slope=1,
    cost_intercept=10,
    cost_slope=1,
    external_cost=20,
)

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch14-externality": lambda: plot_externality(_POLLUTION, 100, 100),
}
