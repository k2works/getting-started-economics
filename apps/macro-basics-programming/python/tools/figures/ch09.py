"""第 9 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter09.plot import plot_liquidity_trap, plot_policy_shifts

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch09-policy-shifts": lambda: plot_policy_shifts(
        mpc=0.6,
        b=20,
        intercept=450,
        k=0.5,
        h=100,
        real_money=250,
        delta_government=10,
        delta_real_money=10,
        income_min=600,
        income_max=1200,
    ),
    "ch09-liquidity-trap": lambda: plot_liquidity_trap(
        mpc=0.6,
        b=20,
        intercept=450,
        trap_interest=2.5,
        delta_government=10,
        income_min=600,
        income_max=1200,
    ),
}
