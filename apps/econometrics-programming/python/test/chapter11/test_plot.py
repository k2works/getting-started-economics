"""第 11 章: 市場のデータと、需要・供給・OLS の直線の図のテスト。"""

from typing import Any

import numpy as np
import pytest

from lib.chapter02.simple import fit_simple
from lib.chapter11.endogeneity import draw_market
from lib.chapter11.plot import plot_market


def xs(line: Any) -> list[float]:
    values: Any = line.get_xdata()
    return [float(v) for v in values]


def ys(line: Any) -> list[float]:
    values: Any = line.get_ydata()
    return [float(v) for v in values]


def test_データと3本の直線() -> None:
    market = draw_market(50, 1.0, 1.0, np.random.default_rng(0))
    ax = plot_market(market).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Data",
        "OLS fit",
        "Demand (slope -1)",
        "Supply (slope +1)",
    ]
    assert ys(ax.lines[0]) == pytest.approx(market["q"].tolist())


def test_OLSの直線の傾きはOLSの推定値() -> None:
    market = draw_market(50, 2.0, 1.0, np.random.default_rng(0))
    ax = plot_market(market).axes[0]
    x, y = xs(ax.lines[1]), ys(ax.lines[1])
    assert (y[1] - y[0]) / (x[1] - x[0]) == pytest.approx(
        fit_simple(market["p"], market["q"]).slope
    )


def test_需要の直線と供給の直線は真の式() -> None:
    market = draw_market(50, 1.0, 1.0, np.random.default_rng(0))
    ax = plot_market(market).axes[0]
    demand_x, demand_y = xs(ax.lines[2]), ys(ax.lines[2])
    supply_x, supply_y = xs(ax.lines[3]), ys(ax.lines[3])
    assert demand_y == pytest.approx([10 - p for p in demand_x])
    assert supply_y == pytest.approx(supply_x)


def test_軸の名前() -> None:
    ax = plot_market(draw_market(20, 1.0, 1.0, np.random.default_rng(0))).axes[0]
    assert ax.get_xlabel() == "Price"
    assert ax.get_ylabel() == "Quantity"
