"""第 9 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter09.plot import plot_regression_with_residuals, plot_residuals_against_x
from lib.chapter09.regression import noisy_regression_sample, regression_design_matrix

# 需要 q = 120 − 2p に、標準偏差 5 の誤差を加えた架空のデータ（種 3 で固定）
_PRICES = [10, 15, 20, 25, 30, 35, 40, 45, 50]
_QUANTITIES = noisy_regression_sample(
    regression_design_matrix([_PRICES]), [120, -2], 5, seed=3
)

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch09-regression-line": lambda: plot_regression_with_residuals(
        _PRICES, _QUANTITIES
    ),
    "ch09-residual-orthogonality": lambda: plot_residuals_against_x(
        _PRICES, _QUANTITIES
    ),
}
