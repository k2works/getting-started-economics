"""第 10 章の図の登録。"""

import math
from collections.abc import Callable
from fractions import Fraction

from matplotlib.figure import Figure

from lib.chapter10.plot import plot_bayes_update, plot_certainty_equivalent

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch10-certainty-equivalent": lambda: plot_certainty_equivalent(
        {16: Fraction(1, 2), 100: Fraction(1, 2)}, math.sqrt
    ),
    "ch10-bayes-update": lambda: plot_bayes_update(
        {"Disease": Fraction(1, 100), "Healthy": Fraction(99, 100)},
        {"Disease": Fraction(9, 10), "Healthy": Fraction(5, 100)},
    ),
}
