"""記事に載せるアニメーション（GIF）の一覧。

名前が、画像のファイル名（名前.gif）になる。`python -m tools.render_animations` で、
記事の images/ に書き出す。静止画の図（figure_registry）とは別。
アニメーションは、lib/animations/chNN.py に登録する。
"""

from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

from matplotlib.animation import FuncAnimation  # noqa: E402

from lib.animations import (
    ch02,  # noqa: E402
    ch03,  # noqa: E402
    ch04,  # noqa: E402
    ch05,  # noqa: E402
    ch06,  # noqa: E402
    ch08,  # noqa: E402
    ch11,  # noqa: E402
    ch12,  # noqa: E402
)

ANIMATIONS: dict[str, Callable[[], FuncAnimation]] = {
    **ch02.ANIMATIONS,
    **ch03.ANIMATIONS,
    **ch04.ANIMATIONS,
    **ch05.ANIMATIONS,
    **ch06.ANIMATIONS,
    **ch08.ANIMATIONS,
    **ch11.ANIMATIONS,
    **ch12.ANIMATIONS,
}
