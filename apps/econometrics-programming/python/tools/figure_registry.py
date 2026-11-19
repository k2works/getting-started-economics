"""記事に載せる図の一覧（シリーズごとに書く）。

名前が、画像のファイル名（名前.png）になる。図を足すときは、ここに登録する。
登録のない画像は、`tools/render_figures.py` の検査で、孤立として失敗する。
"""

from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

from matplotlib.figure import Figure  # noqa: E402

from lib.chapter01.plot import plot_densities  # noqa: E402

# 記事に載せる図。名前が、画像のファイル名（名前.png）になる
FIGURES: dict[str, Callable[[], Figure]] = {
    "ch01-densities": plot_densities,
}
