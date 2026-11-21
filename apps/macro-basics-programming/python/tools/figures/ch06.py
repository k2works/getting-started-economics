"""第 6 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter06.plot import plot_credit_creation, plot_money_multiplier

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch06-money-multiplier": lambda: plot_money_multiplier(
        [i / 100 for i in range(0, 51)], [0.01, 0.05, 0.1]
    ),
    "ch06-credit-creation": lambda: plot_credit_creation(
        base=110, cash_ratio=0.1, reserve_ratio=0.01, rounds=40
    ),
}
