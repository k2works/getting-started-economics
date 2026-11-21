"""第 14 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter14.mundell_fleming import SmallOpenEconomy
from lib.chapter14.plot import plot_fiscal_policy_by_regime, plot_policy_effects

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch14-fiscal-policy-by-regime": lambda: plot_fiscal_policy_by_regime(
        SmallOpenEconomy(
            mpc=0.6,
            b=20,
            intercept=400,
            n=50,
            k=0.5,
            h=100,
            real_money=250,
            world_rate=2.5,
            exchange_rate=1,
        ),
        delta_government=10,
        income_min=600,
        income_max=1200,
    ),
    "ch14-policy-effects": lambda: plot_policy_effects(
        SmallOpenEconomy(
            mpc=0.6,
            b=20,
            intercept=400,
            n=50,
            k=0.5,
            h=100,
            real_money=250,
            world_rate=2.5,
            exchange_rate=1,
        ),
        delta_government=10,
        delta_real_money=10,
    ),
}
