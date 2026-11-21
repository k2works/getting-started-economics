"""第 8 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter08.plot import plot_is_curves, plot_is_lm_equilibrium

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch08-is-curves": lambda: plot_is_curves(
        mpc=0.6, intercept=450, bs=[20, 40], interest_max=10
    ),
    "ch08-is-lm": lambda: plot_is_lm_equilibrium(
        mpc=0.6,
        b=20,
        intercept=450,
        k=0.5,
        h=100,
        real_money=250,
        income_min=600,
        income_max=1200,
    ),
}
