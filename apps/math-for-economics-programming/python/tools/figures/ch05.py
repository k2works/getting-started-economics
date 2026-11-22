"""第 5 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter05.derivative import Polynomial
from lib.chapter05.plot import plot_cost_curves, plot_derivative_errors

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch05-cost-curves": lambda: plot_cost_curves(Polynomial((50, 4, 0.5)), 20, 30),
    "ch05-derivative-errors": lambda: plot_derivative_errors(
        Polynomial((0, 0, 0, 1)), 3, 1, [10.0**-k for k in range(0, 15)]
    ),
}
