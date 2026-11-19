"""第 1 章: 発展会計の図のテスト。"""

from typing import Any

import numpy as np
import pandas as pd
import pytest
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from lib.chapter01.accounting import income_gap, load_countries, with_tfp
from lib.chapter01.plot import plot_gap_decomposition, plot_income_and_tfp

ALPHA = 1 / 3


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def test_分解の図は資本_人的資本_TFPの3本の棒() -> None:
    gap = income_gap(load_countries(), reference="C01", alpha=ALPHA)
    ax = plot_gap_decomposition(pd.Series(gap.loc["C24"])).axes[0]
    bars = [p for p in ax.patches if isinstance(p, Rectangle)]
    assert len(bars) == 3
    labels = [t.get_text() for t in ax.get_xticklabels()]
    assert labels == ["Capital", "Human capital", "TFP"]


def test_棒の高さは各寄与と等しい() -> None:
    gap = income_gap(load_countries(), reference="C01", alpha=ALPHA)
    row = pd.Series(gap.loc["C24"])
    ax = plot_gap_decomposition(row).axes[0]
    heights = [p.get_height() for p in ax.patches if isinstance(p, Rectangle)]
    assert heights == pytest.approx([row["capital"], row["human_capital"], row["tfp"]])


def test_所得とTFPの図は国ごとの点と近似直線の2本() -> None:
    ax = plot_income_and_tfp(load_countries(), ALPHA).axes[0]
    assert [line.get_label() for line in ax.lines] == ["Countries", "Fitted line"]


def test_点は対数のTFPと対数の所得の組() -> None:
    df = load_countries()
    ax = plot_income_and_tfp(df, ALPHA).axes[0]
    points = xy(ax.lines[0])
    assert len(points) == 24
    first = with_tfp(df, ALPHA).iloc[0]
    assert points[0] == pytest.approx((np.log(first["tfp"]), np.log(first["y"])))


def test_近似直線は右上がり() -> None:
    ax = plot_income_and_tfp(load_countries(), ALPHA).axes[0]
    (x0, y0), (x1, y1) = xy(ax.lines[1])
    assert (y1 - y0) / (x1 - x0) > 0
