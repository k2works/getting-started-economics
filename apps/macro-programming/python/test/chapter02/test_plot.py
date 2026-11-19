"""第 2 章: 成長会計の図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from lib.chapter02.growth import growth_contribution, load_panel
from lib.chapter02.plot import plot_growth_contributions, plot_tfp_growth

ALPHA = 1 / 3


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def test_寄与の図は所得_資本_人的資本_TFPの4本の棒() -> None:
    table = growth_contribution(load_panel(), 1990, 2019, ALPHA)
    ax = plot_growth_contributions(table).axes[0]
    bars = [p for p in ax.patches if isinstance(p, Rectangle)]
    assert len(bars) == 4
    assert [t.get_text() for t in ax.get_xticklabels()] == [
        "Output",
        "Capital",
        "Human capital",
        "TFP",
    ]


def test_棒の高さは各国の平均の寄与() -> None:
    table = growth_contribution(load_panel(), 1990, 2019, ALPHA)
    ax = plot_growth_contributions(table).axes[0]
    heights = [p.get_height() for p in ax.patches if isinstance(p, Rectangle)]
    assert heights == pytest.approx(
        [
            table["output"].mean(),
            table["capital"].mean(),
            table["human_capital"].mean(),
            table["tfp"].mean(),
        ]
    )


def test_3つの寄与の棒の和は所得の棒と等しい() -> None:
    table = growth_contribution(load_panel(), 1990, 2019, ALPHA)
    ax = plot_growth_contributions(table).axes[0]
    heights = [p.get_height() for p in ax.patches if isinstance(p, Rectangle)]
    assert sum(heights[1:]) == pytest.approx(heights[0])


def test_TFP成長率の図は国ごとの点と近似直線() -> None:
    table = growth_contribution(load_panel(), 1990, 2019, ALPHA)
    ax = plot_tfp_growth(table).axes[0]
    assert [line.get_label() for line in ax.lines] == ["Countries", "Fitted line"]


def test_点はTFPの成長率と所得の成長率の組() -> None:
    table = growth_contribution(load_panel(), 1990, 2019, ALPHA)
    ax = plot_tfp_growth(table).axes[0]
    points = xy(ax.lines[0])
    assert len(points) == 24
    assert points[0] == pytest.approx((table["tfp"].iloc[0], table["output"].iloc[0]))


def test_近似直線は右上がり() -> None:
    table = growth_contribution(load_panel(), 1990, 2019, ALPHA)
    ax = plot_tfp_growth(table).axes[0]
    (x0, y0), (x1, y1) = xy(ax.lines[1])
    assert (y1 - y0) / (x1 - x0) > 0
