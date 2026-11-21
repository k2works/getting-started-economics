"""第 3 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter03.plot import plot_demand_curve, plot_income_consumption

# 価格を 0.25 から 0.125 刻みで 30 点（曲線をなめらかに見せる）
_PRICES = [0.25 + 0.125 * i for i in range(30)]

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch03-demand-curve": lambda: plot_demand_curve([80, 160], _PRICES, 1),
    "ch03-income-consumption": lambda: plot_income_consumption(
        [20, 40, 80, 120, 160], 2, 1
    ),
}
