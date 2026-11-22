"""第 12 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter12.plot import (
    plot_golden_rule,
    plot_linear_recurrence_paths,
    plot_solow_convergence,
)

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch12-recurrence-paths": lambda: plot_linear_recurrence_paths(
        [0.9, 1, 1.1], 1, 0, 25
    ),
    "ch12-solow-convergence": lambda: plot_solow_convergence(
        [1, 3, 8, 12], 0.3, 1 / 3, 0.1, 60
    ),
    "ch12-golden-rule": lambda: plot_golden_rule(
        1 / 3, 0.1, [k / 100 for k in range(1, 100)]
    ),
}
