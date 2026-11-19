"""第 13 章: データとモデルの比較の図のテスト。"""

import pytest
from matplotlib.patches import Rectangle

from lib.chapter13.plot import MOMENT_LABELS, plot_moment_comparison

DATA = {
    "y_std": 1.3,
    "p_std": 1.7,
    "y_autocorr": -0.1,
    "p_autocorr": 0.6,
    "correlation": 0.1,
}
MODEL = {
    "y_std": 1.4,
    "p_std": 2.3,
    "y_autocorr": 0.0,
    "p_autocorr": 0.8,
    "correlation": -0.05,
}


def test_比較の図はデータとモデルの棒が5組() -> None:
    ax = plot_moment_comparison(DATA, MODEL).axes[0]
    heights = [p.get_height() for p in ax.patches if isinstance(p, Rectangle)]
    assert heights == pytest.approx(
        [DATA[key] for key in MOMENT_LABELS] + [MODEL[key] for key in MOMENT_LABELS]
    )


def test_比較の図の凡例はデータとモデル() -> None:
    ax = plot_moment_comparison(DATA, MODEL).axes[0]
    legend = ax.get_legend()
    assert legend is not None
    assert [t.get_text() for t in legend.get_texts()] == ["Data", "Model"]


def test_比較の図の横軸は5つの特徴() -> None:
    ax = plot_moment_comparison(DATA, MODEL).axes[0]
    assert len(ax.get_xticklabels()) == 5


def test_データとモデルの棒は隣り合って重ならない() -> None:
    ax = plot_moment_comparison(DATA, MODEL).axes[0]
    bars = [p for p in ax.patches if isinstance(p, Rectangle)]
    data_bars, model_bars = bars[:5], bars[5:]
    for data_bar, model_bar in zip(data_bars, model_bars, strict=True):
        assert model_bar.get_x() == pytest.approx(
            data_bar.get_x() + data_bar.get_width()
        )


def test_横軸の名前は傾けて表示する() -> None:
    ax = plot_moment_comparison(DATA, MODEL).axes[0]
    assert ax.get_xticklabels()[0].get_rotation() == 20
