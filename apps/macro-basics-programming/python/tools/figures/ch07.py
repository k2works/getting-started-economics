"""第 7 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter07.plot import plot_lm_curves, plot_money_market

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch07-money-market": lambda: plot_money_market(
        income=1000, income_after=1200, real_money=250, k=0.5, h=100, interest_max=5
    ),
    "ch07-lm-curve": lambda: plot_lm_curves(
        incomes=list(range(600, 1501, 100)),
        real_money=250,
        real_money_after=300,
        k=0.5,
        h=100,
        floor=2.0,
    ),
}
