"""第 7 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter05.cost import CostCurve
from lib.chapter07.plot import plot_supply, plot_tax_supply

_CURVE = CostCurve(cubic=1, quadratic=-6, linear=15, fixed=32)

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch07-supply-curve": lambda: plot_supply(_CURVE, 30, 8, 40),
    "ch07-tax-supply": lambda: plot_tax_supply(_CURVE, 6, 0.2, 3, 6),
}
