"""第 10 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter10.ad_as import AdEconomy
from lib.chapter10.labor import LaborCurves
from lib.chapter10.plot import plot_ad_as, plot_labor_market

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch10-labor-market": lambda: plot_labor_market(
        LaborCurves(
            demand_intercept=100,
            demand_slope=10,
            supply_intercept=20,
            supply_slope=10,
        ),
        sticky_wage=6,
        wage_max=10,
    ),
    "ch10-ad-as": lambda: plot_ad_as(
        AdEconomy(mpc=0.6, b=20, intercept=450, k=0.5, h=100, nominal_money=250),
        full_employment_income=1000,
        base_income=480,
        slope=400,
        delta_government=10,
        price_min=0.8,
        price_max=1.6,
    ),
}
