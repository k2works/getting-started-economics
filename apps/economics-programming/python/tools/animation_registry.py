"""記事に載せるアニメーション（GIF）の一覧。

名前が、画像のファイル名（名前.gif）になる。`python -m tools.render_animations` で、
記事の images/ に書き出す。静止画の図（figure_registry）とは別。
"""

from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

from matplotlib.animation import FuncAnimation  # noqa: E402

from lib.animations.firm import (  # noqa: E402
    animate_cournot_steps,
    animate_monopoly_cost,
    animate_profit_price,
)
from lib.animations.macro import (  # noqa: E402
    animate_adas_fiscal,
    animate_islm_fiscal,
    animate_multiplier,
)
from lib.animations.market import animate_tax_wedge, animate_walras  # noqa: E402

ANIMATIONS: dict[str, Callable[[], FuncAnimation]] = {
    "ch05-walras": animate_walras,
    "ch07-tax-wedge": animate_tax_wedge,
    "ch09-multiplier": animate_multiplier,
    "ch10-profit-price": animate_profit_price,
    "ch13-islm-fiscal": animate_islm_fiscal,
    "ch14-adas-fiscal": animate_adas_fiscal,
    "ch15-monopoly-cost": animate_monopoly_cost,
    "ch15-cournot-steps": animate_cournot_steps,
}
