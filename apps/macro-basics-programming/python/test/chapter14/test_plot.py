"""第 14 章: マンデル・フレミングの図のテスト。"""

import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from lib.chapter14.mundell_fleming import SmallOpenEconomy
from lib.chapter14.plot import plot_fiscal_policy_by_regime, plot_policy_effects

ECONOMY = SmallOpenEconomy(
    mpc=0.6,
    b=20,
    intercept=400,
    n=50,
    k=0.5,
    h=100,
    real_money=250,
    world_rate=2.5,
    exchange_rate=1,
)


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_ydata())]


def fiscal_axes() -> list[Axes]:
    fig = plot_fiscal_policy_by_regime(ECONOMY, 10, 600, 1200)
    return fig.axes


def line(ax: Axes, label: str) -> Line2D:
    return next(item for item in ax.lines if item.get_label() == label)


def test_財政政策の図は固定相場と変動相場が左右に並ぶ() -> None:
    left, right = fiscal_axes()
    assert left.get_position().x1 < right.get_position().x0
    assert left.get_title() == "Fixed rate"
    assert right.get_title() == "Floating rate"


def test_BP曲線は世界の利子率の水平線() -> None:
    for ax in fiscal_axes():
        bp = line(ax, "BP")
        assert xs(bp) == [600, 1200]
        assert ys(bp) == [2.5, 2.5]


def test_固定相場の図は均衡が水平線の上を右へ動く() -> None:
    ax = fiscal_axes()[0]
    assert xs(line(ax, "Equilibrium before")) == pytest.approx([1000])
    assert xs(line(ax, "Equilibrium after")) == pytest.approx([1025])
    assert ys(line(ax, "Equilibrium after")) == pytest.approx([2.5])


def test_固定相場の図はISとLMの両方が右へ動く() -> None:
    ax = fiscal_axes()[0]
    labels = [item.get_label() for item in ax.lines]
    assert labels == [
        "IS",
        "IS after fiscal policy",
        "LM",
        "LM after fiscal policy",
        "BP",
        "Equilibrium before",
        "Equilibrium after",
    ]
    # IS: r = (A − (1 − c)Y) ÷ b。Y = 600 で (450 − 240) ÷ 20 = 10.5
    assert ys(line(ax, "IS"))[0] == pytest.approx(10.5)
    assert ys(line(ax, "IS after fiscal policy"))[0] == pytest.approx(11)
    # LM: r = (k·Y − M/P) ÷ h。Y = 600 で (300 − 250) ÷ 100 = 0.5
    assert ys(line(ax, "LM"))[0] == pytest.approx(0.5)
    assert ys(line(ax, "LM after fiscal policy"))[0] == pytest.approx(0.375)


def test_変動相場の図は均衡が動かない() -> None:
    ax = fiscal_axes()[1]
    labels = [item.get_label() for item in ax.lines]
    assert labels == [
        "IS",
        "IS after fiscal policy",
        "IS after exchange rate adjustment",
        "LM",
        "BP",
        "Equilibrium",
    ]
    assert xs(line(ax, "Equilibrium")) == pytest.approx([1000])
    assert ys(line(ax, "IS after exchange rate adjustment")) == pytest.approx(
        ys(line(ax, "IS"))
    )
    assert ys(line(ax, "IS after fiscal policy"))[0] == pytest.approx(11)


def test_軸の名前と下限() -> None:
    for ax in fiscal_axes():
        assert ax.get_xlabel() == "Income Y"
        assert ax.get_ylabel() == "Interest rate r"
        assert ax.get_ylim()[0] == 0


def test_4通りの効果の棒グラフ() -> None:
    fig = plot_policy_effects(ECONOMY, 10, 10)
    ax = fig.axes[0]
    heights = [p.get_height() for p in ax.patches if isinstance(p, Rectangle)]
    assert heights == pytest.approx([25, 0, 0, 20])
    labels = [tick.get_text() for tick in ax.get_xticklabels()]
    assert labels == [
        "Fixed\nfiscal",
        "Fixed\nmonetary",
        "Floating\nfiscal",
        "Floating\nmonetary",
    ]
    assert ax.get_ylabel() == "Change in income Y"
