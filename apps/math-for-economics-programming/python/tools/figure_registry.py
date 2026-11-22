"""記事に載せる図の一覧（シリーズごとに書く）。

名前が、画像のファイル名（名前.png）になる。図は、tools/figures/chNN.py に登録する。
登録のない画像は、`article_tools.render_figures` の検査で、孤立として失敗する。
章を足すときは、ここに import と、合成の 1 行を足す。
"""

from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

from matplotlib.figure import Figure  # noqa: E402

from tools.figures import (  # noqa: E402
    ch01,
    ch02,
    ch03,
    ch04,
    ch05,
    ch06,
    ch07,
    ch08,
    ch09,
    ch10,
    ch11,
    ch12,
)

FIGURES: dict[str, Callable[[], Figure]] = {
    **ch01.FIGURES,
    **ch02.FIGURES,
    **ch03.FIGURES,
    **ch04.FIGURES,
    **ch05.FIGURES,
    **ch06.FIGURES,
    **ch07.FIGURES,
    **ch08.FIGURES,
    **ch09.FIGURES,
    **ch10.FIGURES,
    **ch11.FIGURES,
    **ch12.FIGURES,
}
