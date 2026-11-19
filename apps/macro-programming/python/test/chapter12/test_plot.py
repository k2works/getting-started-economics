"""第 12 章: 為替レートの図のテスト。"""

from typing import Any

import pandas as pd
import pytest
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from lib.chapter12.exchange import load_exchange
from lib.chapter12.plot import plot_exchange_rates, plot_regime_volatility


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def test_為替レートの図は名目と実質と切り替えの線() -> None:
    ax = plot_exchange_rates(load_exchange(), "1973Q1").axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Nominal",
        "Real",
        "Regime change",
    ]


def test_系列は最初の四半期を100にそろえる() -> None:
    ax = plot_exchange_rates(load_exchange(), "1973Q1").axes[0]
    assert xy(ax.lines[0])[0] == pytest.approx((0, 100))
    assert xy(ax.lines[1])[0] == pytest.approx((0, 100))


def test_切り替えの線は1973年第1四半期の位置() -> None:
    ax = plot_exchange_rates(load_exchange(), "1973Q1").axes[0]
    points = xy(ax.lines[2])
    assert points[0][0] == pytest.approx(52)
    assert points[1][0] == pytest.approx(52)


def test_変動の大きさの図は4本の棒() -> None:
    stats = pd.DataFrame(
        {"nominal_volatility": [0.1, 3.0], "real_volatility": [0.3, 3.1]},
        index=["fixed", "floating"],
    )
    ax = plot_regime_volatility(stats).axes[0]
    heights = [p.get_height() for p in ax.patches if isinstance(p, Rectangle)]
    assert heights == pytest.approx([0.1, 0.3, 3.0, 3.1])
