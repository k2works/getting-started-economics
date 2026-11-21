"""第 4 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter04.plot import plot_keynesian_cross, plot_multiplier_slopes

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch04-keynesian-cross": lambda: plot_keynesian_cross(
        mpc=0.6,
        autonomous_consumption=40,
        investment=30,
        government=30,
        net_exports=0,
        income_max=400,
    ),
    "ch04-multiplier-slopes": lambda: plot_multiplier_slopes(
        [0.6, 0.8], autonomous=100, income_max=500
    ),
}
