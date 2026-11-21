"""第 5 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter05.plot import plot_gap, plot_income_swing

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch05-deflationary-gap": lambda: plot_gap(
        mpc=0.6, autonomous=100, full_employment_income=300, income_max=400
    ),
    "ch05-income-swing": lambda: plot_income_swing(mpc=0.6, tax_rate=0.2, shock=10),
}
