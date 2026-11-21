"""第 13 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

FIGURES: dict[str, Callable[[], Figure]] = {}
