"""第 12 章の図の登録（この章は、利得表の表だけで、図はない）。"""

from collections.abc import Callable

from matplotlib.figure import Figure

FIGURES: dict[str, Callable[[], Figure]] = {}
