"""記事に載せるアニメーション（GIF）の一覧。

名前が、画像のファイル名（名前.gif）になる。`python -m tools.render_animations` で、
記事の images/ に書き出す。静止画の図（figure_registry）とは別。
"""

from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

from matplotlib.animation import FuncAnimation  # noqa: E402

from lib.animations.endogenous import (  # noqa: E402
    animate_likelihood,
    animate_omitted_variable,
    animate_weak_instrument,
)
from lib.animations.inference import (  # noqa: E402
    animate_confidence_intervals,
    animate_consistency,
)
from lib.animations.regression import (  # noqa: E402
    animate_collinearity,
    animate_outlier,
)

ANIMATIONS: dict[str, Callable[[], FuncAnimation]] = {
    "ch02-outlier": animate_outlier,
    "ch03-collinearity": animate_collinearity,
    "ch05-confidence-intervals": animate_confidence_intervals,
    "ch06-consistency": animate_consistency,
    "ch11-omitted-variable": animate_omitted_variable,
    "ch12-weak-instrument": animate_weak_instrument,
    "ch14-likelihood": animate_likelihood,
}
