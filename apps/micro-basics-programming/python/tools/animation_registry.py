"""記事に載せるアニメーション（GIF）の一覧。

名前が、画像のファイル名（名前.gif）になる。`python -m tools.render_animations` で、
記事の images/ に書き出す。静止画の図（figure_registry）とは別。
"""

from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

from matplotlib.animation import FuncAnimation  # noqa: E402

from lib.animations.consumer import animate_price_change  # noqa: E402
from lib.animations.externality import animate_externality  # noqa: E402
from lib.animations.firm import (  # noqa: E402
    animate_monopoly_cost,
    animate_supply_curve,
)
from lib.animations.game import animate_trigger_threshold  # noqa: E402
from lib.animations.market import (  # noqa: E402
    animate_price_adjustment,
    animate_tariff,
    animate_tax,
)

ANIMATIONS: dict[str, Callable[[], FuncAnimation]] = {
    "ch03-price-change": animate_price_change,
    "ch07-supply": animate_supply_curve,
    "ch08-adjustment": animate_price_adjustment,
    "ch09-tax": animate_tax,
    "ch10-tariff": animate_tariff,
    "ch11-monopoly-cost": animate_monopoly_cost,
    "ch13-trigger-threshold": animate_trigger_threshold,
    "ch14-externality-cost": animate_externality,
}
