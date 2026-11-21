"""第 3 章: 物価指数と景気動向指数の図のテスト。"""

import matplotlib

matplotlib.use("Agg")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from lib.chapter03.plot import plot_business_indexes, plot_price_indexes  # noqa: E402

TABLE = pd.DataFrame(
    {"laspeyres": [1.0, 1.0, 1.03], "paasche": [1.0, 1.02, 1.102]},
    index=["2020", "2021", "2022"],
)
MONTHS = ["m0", "m1", "m2", "m3"]
DI = pd.Series([float("nan"), 50.0, 200 / 3, 100.0], index=MONTHS)
CI = pd.Series([100.0, 101.0, 103.0, 108.0], index=MONTHS)


def test_物価指数の図はラスパイレスとパーシェの2本の線() -> None:
    ax = plot_price_indexes(TABLE).axes[0]
    assert len(ax.lines) == 2
    assert [line.get_label() for line in ax.lines] == ["Laspeyres", "Paasche"]
    assert np.asarray(ax.lines[0].get_ydata()).tolist() == pytest.approx(
        [1.0, 1.0, 1.03]
    )
    assert np.asarray(ax.lines[1].get_ydata()).tolist() == pytest.approx(
        [1.0, 1.02, 1.102]
    )
    assert [t.get_text() for t in ax.get_xticklabels()] == ["2020", "2021", "2022"]
    legend = ax.get_legend()
    assert legend is not None
    assert [t.get_text() for t in legend.get_texts()] == ["Laspeyres", "Paasche"]


def test_景気動向指数の図は上にCIの線と下にDIの棒() -> None:
    top, bottom = plot_business_indexes(DI, CI).axes
    assert np.asarray(top.lines[0].get_ydata()).tolist() == pytest.approx(
        [100, 101, 103, 108]
    )
    heights = [p.get_height() for p in bottom.patches if isinstance(p, Rectangle)]
    assert heights == pytest.approx([50, 200 / 3, 100])
    # 最初の月（NaN）には、棒がない。棒は、2〜4 番目の月の位置（1・2・3）に立つ
    bars = [p for p in bottom.patches if isinstance(p, Rectangle)]
    centers = [p.get_x() + p.get_width() / 2 for p in bars]
    assert centers == pytest.approx([1, 2, 3])
    assert top.get_shared_x_axes().joined(top, bottom)
    assert [t.get_text() for t in bottom.get_xticklabels()] == MONTHS


def test_DIの図は50の線を引く() -> None:
    bottom = plot_business_indexes(DI, CI).axes[1]
    assert [np.asarray(line.get_ydata()).tolist() for line in bottom.lines] == [
        [50, 50]
    ]


def test_軸の名前() -> None:
    assert plot_price_indexes(TABLE).axes[0].get_ylabel() == "Index (base = 1.0)"
    top, bottom = plot_business_indexes(DI, CI).axes
    assert top.get_ylabel() == "CI (base = 100)"
    assert bottom.get_ylabel() == "DI (%)"
