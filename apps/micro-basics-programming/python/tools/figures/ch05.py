"""第 5 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter05.cost import CostCurve
from lib.chapter05.plot import plot_cost_curves, plot_total_cost

_CURVE = CostCurve(cubic=1, quadratic=-6, linear=15, fixed=32)

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch05-cost-curves": lambda: plot_cost_curves(_CURVE, 8, 40),
    "ch05-total-cost": lambda: plot_total_cost(_CURVE, 8),
}
