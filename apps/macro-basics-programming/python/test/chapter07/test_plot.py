"""第 7 章: 貨幣市場と LM 曲線の図のテスト。"""

import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter07.plot import plot_lm_curves, plot_money_market


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_ydata())]


def money_market_axes() -> Axes:
    fig = plot_money_market(
        income=1000, income_after=1200, real_money=250, k=0.5, h=100, interest_max=5
    )
    return fig.axes[0]


def lm_axes() -> Axes:
    fig = plot_lm_curves(
        incomes=[600, 900, 1200],
        real_money=250,
        real_money_after=300,
        k=0.5,
        h=100,
        floor=2.0,
    )
    return fig.axes[0]


def test_貨幣市場の図は需要と需要のシフトと供給と均衡を描く() -> None:
    ax = money_market_axes()
    assert [line.get_label() for line in ax.lines] == [
        "Money demand (Y = 1000)",
        "Money demand (Y = 1200)",
        "Money supply (M/P)",
        "Equilibrium",
    ]


def test_貨幣需要曲線は右下がりで所得が増えると右にシフトする() -> None:
    ax = money_market_axes()
    assert xs(ax.lines[0]) == pytest.approx([500, 0])
    assert ys(ax.lines[0]) == pytest.approx([0, 5])
    assert xs(ax.lines[1]) == pytest.approx([600, 100])


def test_貨幣供給は垂直で均衡は供給と需要の交点() -> None:
    ax = money_market_axes()
    assert xs(ax.lines[2]) == pytest.approx([250, 250])
    assert ys(ax.lines[2]) == pytest.approx([0, 5])
    assert xs(ax.lines[3]) == pytest.approx([250])
    assert ys(ax.lines[3]) == pytest.approx([2.5])


def test_LMの図は通常のLMとシフト後とわなを描く() -> None:
    ax = lm_axes()
    assert [line.get_label() for line in ax.lines] == [
        "LM",
        "LM (M/P increased)",
        "LM with liquidity trap",
    ]


def test_LM曲線の座標とシフトとわなの水平部分() -> None:
    ax = lm_axes()
    assert xs(ax.lines[0]) == pytest.approx([600, 900, 1200])
    assert ys(ax.lines[0]) == pytest.approx([0.5, 2.0, 3.5])
    assert ys(ax.lines[1]) == pytest.approx([0.0, 1.5, 3.0])
    assert ys(ax.lines[2]) == pytest.approx([2.0, 2.0, 3.5])


def test_軸の名前() -> None:
    ax = money_market_axes()
    assert ax.get_xlabel() == "Real money balances"
    assert ax.get_ylabel() == "Interest rate r"
    ax2 = lm_axes()
    assert ax2.get_xlabel() == "Income Y"
    assert ax2.get_ylabel() == "Interest rate r"


def test_わなのあるLM曲線は破線で描く() -> None:
    ax = lm_axes()
    assert [line.get_linestyle() for line in ax.lines] == ["-", "-", "--"]
