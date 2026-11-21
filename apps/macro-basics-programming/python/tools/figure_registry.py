"""記事に載せる図の一覧（シリーズごとに書く）。

名前が、画像のファイル名（名前.png）になる。図は、tools/figures/chNN.py に登録する。
登録のない画像は、`article_tools.render_figures` の検査で、孤立として失敗する。
"""

from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

from matplotlib.figure import Figure  # noqa: E402

from tools.figures import (
    ch01,  # noqa: E402
    ch02,  # noqa: E402
    ch03,  # noqa: E402
    ch04,  # noqa: E402
    ch05,  # noqa: E402
    ch06,  # noqa: E402
    ch07,  # noqa: E402
    ch08,  # noqa: E402
    ch09,  # noqa: E402
    ch10,  # noqa: E402
    ch11,  # noqa: E402
    ch12,  # noqa: E402
    ch13,  # noqa: E402
    ch14,  # noqa: E402
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
    **ch13.FIGURES,
    **ch14.FIGURES,
}
