"""第 4 章: 45 度線と乗数の図のテスト。"""

import matplotlib
import numpy as np
import pytest
from matplotlib.lines import Line2D

matplotlib.use("Agg")

from lib.chapter04.plot import (  # noqa: E402
    plot_keynesian_cross,
    plot_multiplier_slopes,
)

BASE = {
    "mpc": 0.6,
    "autonomous_consumption": 40,
    "investment": 30,
    "government": 30,
    "net_exports": 0,
}


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_ydata())]


def test_45度線は原点を通る傾き1の線() -> None:
    ax = plot_keynesian_cross(**BASE, income_max=400).axes[0]
    line = ax.lines[0]
    assert line.get_label() == "45-degree line (Y)"
    assert xs(line) == pytest.approx([0, 400])
    assert ys(line) == pytest.approx([0, 400])


def test_総需要の線は切片が独立支出で傾きがc() -> None:
    ax = plot_keynesian_cross(**BASE, income_max=400).axes[0]
    line = ax.lines[1]
    assert line.get_label() == "Aggregate demand"
    assert ys(line) == pytest.approx([100, 100 + 0.6 * 400])


def test_均衡点は45度線上で所得250() -> None:
    ax = plot_keynesian_cross(**BASE, income_max=400).axes[0]
    point = ax.lines[2]
    assert xs(point) == pytest.approx([250])
    assert ys(point) == pytest.approx([250])


def test_課税で総需要の切片は下がる() -> None:
    ax = plot_keynesian_cross(**BASE, income_max=400, tax=50).axes[0]
    assert ys(ax.lines[1])[0] == pytest.approx(100 - 0.6 * 50)
    assert xs(ax.lines[2]) == pytest.approx([(100 - 0.6 * 50) / 0.4])


def test_乗数の図は限界消費性向ごとに総需要の線を描く() -> None:
    ax = plot_multiplier_slopes([0.6, 0.8], autonomous=100, income_max=500).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "45-degree line (Y)",
        "c = 0.6",
        "c = 0.8",
    ]
    assert xs(ax.lines[0]) == pytest.approx([0, 500])
    assert ys(ax.lines[0]) == pytest.approx([0, 500])
    assert ys(ax.lines[1]) == pytest.approx([100, 400])
    assert ys(ax.lines[2]) == pytest.approx([100, 500])


def test_軸の名前() -> None:
    ax = plot_keynesian_cross(**BASE, income_max=400).axes[0]
    assert ax.get_xlabel() == "Income Y"
    assert ax.get_ylabel() == "Demand / Supply"
    ax2 = plot_multiplier_slopes([0.6], autonomous=100, income_max=500).axes[0]
    assert ax2.get_xlabel() == "Income Y"
    assert ax2.get_ylabel() == "Aggregate demand"
