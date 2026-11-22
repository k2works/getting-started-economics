"""記事に載せる図の一覧（シリーズごとに書く）。

名前が、画像のファイル名（名前.png）になる。図は、tools/figures/chNN.py に登録する。
登録のない画像は、`article_tools.render_figures` の検査で、孤立として失敗する。
章を足すときは、ここに import と、合成の 1 行を足す。
"""

from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

from matplotlib.figure import Figure  # noqa: E402

from tools.figures import ch01  # noqa: E402

FIGURES: dict[str, Callable[[], Figure]] = {
    **ch01.FIGURES,
}
