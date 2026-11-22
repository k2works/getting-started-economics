"""記事に載せるアニメーション（GIF）の一覧。

名前が、画像のファイル名（名前.gif）になる。`python -m tools.render_animations` で、
記事の images/ に書き出す。静止画の図（figure_registry）とは別。
"""

from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

from matplotlib.animation import FuncAnimation  # noqa: E402

from lib.animations.ad_as import animate_ad_as  # noqa: E402
from lib.animations.income import animate_mpc_change  # noqa: E402
from lib.animations.is_lm import (  # noqa: E402
    animate_crowding_out,
    animate_fiscal_shift,
)
from lib.animations.money import (  # noqa: E402
    animate_credit_creation,
    animate_lm_shift,
)
from lib.animations.open_economy import animate_regimes  # noqa: E402
from lib.animations.phillips import animate_accelerating_inflation  # noqa: E402

ANIMATIONS: dict[str, Callable[[], FuncAnimation]] = {
    "ch04-mpc-change": animate_mpc_change,
    "ch06-credit-creation": animate_credit_creation,
    "ch07-lm-shift": animate_lm_shift,
    "ch08-fiscal-shift": animate_fiscal_shift,
    "ch09-crowding-out": animate_crowding_out,
    "ch10-ad-as": animate_ad_as,
    "ch11-accelerating-inflation": animate_accelerating_inflation,
    "ch14-regimes": animate_regimes,
}
