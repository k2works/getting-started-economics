"""第 7 章: 購買力平価の図のテスト。"""

from typing import Any

import pandas as pd
import pytest
from matplotlib.patches import Rectangle

from lib.chapter07.plot import plot_relative_price_levels


def levels() -> pd.Series:
    return pd.Series({"A": 1.2, "B": 0.5, "C": 0.9, "BASE": 1.0})


def test_棒は相対価格水準の低い順に並ぶ() -> None:
    ax = plot_relative_price_levels(levels()).axes[0]
    heights = [p.get_height() for p in ax.patches if isinstance(p, Rectangle)]
    assert heights == pytest.approx([0.5, 0.9, 1.0, 1.2])
    assert [t.get_text() for t in ax.get_xticklabels()] == ["B", "C", "BASE", "A"]


def test_一物一価の線は高さ1() -> None:
    ax = plot_relative_price_levels(levels()).axes[0]
    assert [line.get_label() for line in ax.lines] == ["Law of one price"]
    ydata: Any = ax.lines[0].get_ydata()
    assert [float(y) for y in ydata] == [1.0, 1.0]
