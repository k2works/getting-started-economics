"""第 5 章: ギャップとビルトイン・スタビライザーの図のテスト。"""

import matplotlib
import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

matplotlib.use("Agg")

from lib.chapter05.plot import plot_gap, plot_income_swing  # noqa: E402


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_ydata())]


def deflation_gap_axes() -> Axes:
    fig = plot_gap(mpc=0.6, autonomous=100, full_employment_income=300, income_max=400)
    return fig.axes[0]


def test_ギャップの図は45度線と総需要と完全雇用所得の線を描く() -> None:
    ax = deflation_gap_axes()
    labels = [line.get_label() for line in ax.lines]
    assert labels[:3] == [
        "45-degree line (Y)",
        "Aggregate demand",
        "Full-employment income",
    ]
    assert xs(ax.lines[2]) == pytest.approx([300, 300])


def test_45度線と総需要の線の座標() -> None:
    ax = deflation_gap_axes()
    assert ys(ax.lines[0]) == pytest.approx([0, 400])
    assert xs(ax.lines[1]) == pytest.approx([0, 400])
    assert ys(ax.lines[1]) == pytest.approx([100, 340])


def test_均衡点は250で総需要の線の上にある() -> None:
    point = deflation_gap_axes().lines[3]
    assert xs(point) == pytest.approx([250])
    assert ys(point) == pytest.approx([250])


def test_ギャップの線分は完全雇用所得の上で総需要から45度線までの長さ20() -> None:
    segment = deflation_gap_axes().lines[4]
    assert xs(segment) == pytest.approx([300, 300])
    assert ys(segment) == pytest.approx([280, 300])


def test_インフレギャップでは線分の向きが逆になる() -> None:
    fig = plot_gap(mpc=0.6, autonomous=100, full_employment_income=200, income_max=400)
    segment = fig.axes[0].lines[4]
    assert ys(segment) == pytest.approx([220, 200])


def test_振れ幅の図は2本の棒で比例税のほうが低い() -> None:
    ax = plot_income_swing(mpc=0.6, tax_rate=0.2, shock=10).axes[0]
    bars = [p for p in ax.patches if isinstance(p, Rectangle)]
    assert [t.get_text() for t in ax.get_xticklabels()] == [
        "No tax",
        "Proportional tax",
    ]
    assert [b.get_height() for b in bars] == pytest.approx([25, 10 / 0.52])


def test_軸の名前() -> None:
    ax = deflation_gap_axes()
    assert ax.get_xlabel() == "Income Y"
    assert ax.get_ylabel() == "Demand / Supply"
    ax2 = plot_income_swing(mpc=0.6, tax_rate=0.2, shock=10).axes[0]
    assert ax2.get_ylabel() == "Change in income"
