"""記事に載せる図の一覧（シリーズごとに書く）。

名前が、画像のファイル名（名前.png）になる。図を足すときは、ここに登録する。
登録のない画像は、`tools/render_figures.py` の検査で、孤立として失敗する。
"""

from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

import pandas as pd  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

from lib.chapter01.accounting import income_gap, load_countries  # noqa: E402
from lib.chapter01.plot import (  # noqa: E402
    plot_gap_decomposition,
    plot_income_and_tfp,
)

# 記事に載せる図。名前が、画像のファイル名（名前.png）になる
FIGURES: dict[str, Callable[[], Figure]] = {
    "ch01-gap-decomposition": lambda: plot_gap_decomposition(
        pd.Series(income_gap(load_countries(), "C01", 1 / 3).loc["C24"])
    ),
    "ch01-income-and-tfp": lambda: plot_income_and_tfp(load_countries(), 1 / 3),
}
