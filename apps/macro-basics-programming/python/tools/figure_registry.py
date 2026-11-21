"""記事に載せる図の一覧（シリーズごとに書く）。

名前が、画像のファイル名（名前.png）になる。図を足すときは、ここに登録する。
登録のない画像は、`article_tools.render_figures` の検査で、孤立として失敗する。
"""

from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

from matplotlib.figure import Figure  # noqa: E402

from lib.chapter01.gdp import growth_accounting  # noqa: E402
from lib.chapter01.plot import (  # noqa: E402
    plot_growth_accounting,
    plot_value_added,
)

# 記事に載せる図。名前が、画像のファイル名（名前.png）になる
FIGURES: dict[str, Callable[[], Figure]] = {
    "ch01-value-added": lambda: plot_value_added(
        ["Wheat", "Flour", "Bread"], [300, 700, 1000], [0, 300, 700]
    ),
    "ch01-growth-accounting": lambda: plot_growth_accounting(
        growth_accounting(6.0, 7.0, 0.4, 4.0, 0.6)
    ),
}
