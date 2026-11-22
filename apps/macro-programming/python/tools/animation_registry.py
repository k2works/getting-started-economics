"""記事に載せるアニメーション（GIF）の一覧。

名前が、画像のファイル名（名前.gif）になる。`python -m tools.render_animations` で、
記事の images/ に書き出す。静止画の図（figure_registry）とは別。
"""

from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

from matplotlib.animation import FuncAnimation  # noqa: E402

from lib.animations.adas import animate_adas_impulse  # noqa: E402
from lib.animations.difference import animate_difference  # noqa: E402
from lib.animations.ismppc import animate_ismppc_impulse  # noqa: E402
from lib.animations.loglinear import animate_loglinear_error  # noqa: E402
from lib.animations.rbc import animate_rbc_impulse  # noqa: E402
from lib.animations.solow import animate_solow_saving  # noqa: E402
from lib.animations.stochastic import animate_ar1  # noqa: E402

ANIMATIONS: dict[str, Callable[[], FuncAnimation]] = {
    "ch04-difference-coefficient": animate_difference,
    "ch05-solow-saving": animate_solow_saving,
    "ch08-ar1-persistence": animate_ar1,
    "ch14-impulse-slope": animate_adas_impulse,
    "ch15-impulse-policy": animate_ismppc_impulse,
    "ch17-approximation-error": animate_loglinear_error,
    "ch18-irf-persistence": animate_rbc_impulse,
}
