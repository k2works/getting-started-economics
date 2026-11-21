"""全体レビュー（2026-11-21）の指摘: 部門が多くても、健全な経済を特異と誤らない。"""

import numpy as np
import pytest

from lib.chapter02.input_output import leontief_inverse, output_for_demand


def test_部門が多い健全な経済を特異と誤らない() -> None:
    # (I − A) の行列式は 0.5 の 50 乗（約 9e-16）と小さいが、条件数は 1 で、解ける
    a = np.eye(50) * 0.5
    assert output_for_demand(a, np.ones(50)) == pytest.approx(np.full(50, 2.0))
    assert leontief_inverse(a) == pytest.approx(np.eye(50) * 2)


def test_ほぼ特異な行列は条件数でエラー() -> None:
    a = np.array(
        [[0.5, 0.5], [0.5, 0.5 - 1e-14]]
    )  # 行列式は 5e-15 > 0 だが、条件数が巨大
    with pytest.raises(ValueError, match="特異"):
        leontief_inverse(a)


def test_並べた棒は重ならず幅が等しい() -> None:
    from matplotlib.patches import Rectangle

    from lib.chapter02.plot import plot_io_output

    ax = plot_io_output([[0.2, 0.3], [0.4, 0.1]], [100, 200], ["A", "B"]).axes[0]
    rects = [p for p in ax.patches if isinstance(p, Rectangle)]
    assert [r.get_width() for r in rects] == pytest.approx([0.4] * 4)
    # 最終需要（先の 2 本）は部門の位置の左、生産量（後の 2 本）は右で、隣り合って接する
    assert [r.get_x() for r in rects] == pytest.approx([-0.4, 0.6, 0.0, 1.0])
