"""第 11 章の図の登録。"""

import math
from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter11.plot import (
    plot_auction_revenues,
    plot_integration_errors,
    plot_uniform_distribution,
)

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch11-uniform-distribution": lambda: plot_uniform_distribution(2, 6, 3, 5),
    "ch11-auction-revenues": lambda: plot_auction_revenues(2, 20_000, seed=1),
    "ch11-integration-errors": lambda: plot_integration_errors(
        math.exp, math.e - 1, 0, 1, [2**k for k in range(1, 11)]
    ),
}
