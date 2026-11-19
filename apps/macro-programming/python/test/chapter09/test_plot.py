"""第 9 章: トレンドと循環の図のテスト。"""

from typing import Any

import pandas as pd
import pytest
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from lib.chapter09.cycles import hp_trend, load_quarterly
from lib.chapter09.plot import plot_cycle, plot_trend, plot_volatility


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def test_トレンドの図は系列とトレンドの2本() -> None:
    gdp = pd.Series(load_quarterly()["gdp"])
    ax = plot_trend(gdp).axes[0]
    assert [line.get_label() for line in ax.lines] == ["Series", "HP trend"]


def test_トレンドの線はHPトレンドと一致する() -> None:
    gdp = pd.Series(load_quarterly()["gdp"])
    ax = plot_trend(gdp).axes[0]
    assert [y for _, y in xy(ax.lines[1])] == pytest.approx(
        hp_trend(gdp).to_numpy().tolist()
    )


def test_循環の図は複数の系列と0の線() -> None:
    cycles = pd.DataFrame({"a": [1.0, -1.0, 0.5], "b": [0.5, -0.5, 0.2]})
    ax = plot_cycle(cycles).axes[0]
    assert [line.get_label() for line in ax.lines] == ["a", "b", "Zero"]


def test_変動の大きさの図は変数ごとの棒() -> None:
    stats = pd.DataFrame(
        {"relative_to_gdp": [1.0, 0.7, 3.0]}, index=["gdp", "consumption", "investment"]
    )
    ax = plot_volatility(stats).axes[0]
    heights = [p.get_height() for p in ax.patches if isinstance(p, Rectangle)]
    assert heights == pytest.approx([1.0, 0.7, 3.0])
    assert [t.get_text() for t in ax.get_xticklabels()] == [
        "gdp",
        "consumption",
        "investment",
    ]


def test_0の線は高さ0() -> None:
    cycles = pd.DataFrame({"a": [1.0, -1.0, 0.5]})
    ax = plot_cycle(cycles).axes[0]
    ydata: Any = ax.lines[-1].get_ydata()
    assert [float(y) for y in ydata] == [0.0, 0.0]
