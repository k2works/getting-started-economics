"""第 11 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter11.okun import OkunFit, synthetic_unemployment_change
from lib.chapter11.plot import plot_okun, plot_phillips

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch11-phillips-curve": lambda: plot_phillips(
        natural_rate=5, expected_inflations=[2, 4], beta=0.5, u_min=3, u_max=7
    ),
    "ch11-okun-law": lambda: plot_okun(
        [3.2, 1.5, 4.1, 0.8, 2.9, 5.0, -0.5, 3.6, 2.2, 4.5, 1.0, 3.0],
        synthetic_unemployment_change(
            [3.2, 1.5, 4.1, 0.8, 2.9, 5.0, -0.5, 3.6, 2.2, 4.5, 1.0, 3.0],
            slope=-0.4,
            intercept=1.2,
            noise=0.1,
            seed=0,
        ),
        OkunFit(slope=-0.4, intercept=1.2),
    ),
}
