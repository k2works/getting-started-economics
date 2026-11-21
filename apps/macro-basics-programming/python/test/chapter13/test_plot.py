"""第 13 章: 貨幣量と物価、為替レートと純輸出の図のテスト。"""

import numpy as np
import pytest
from matplotlib.lines import Line2D

from lib.chapter13.plot import plot_money_and_prices, plot_net_exports


def xy(line: Line2D) -> tuple[list[float], list[float]]:
    xs = [float(v) for v in np.asarray(line.get_xdata())]
    ys = [float(v) for v in np.asarray(line.get_ydata())]
    return xs, ys


def test_貨幣量と物価の図は産出量ごとの直線() -> None:
    ax = plot_money_and_prices(4, [200, 400], [0, 100, 200]).axes[0]
    labels = [line.get_label() for line in ax.get_lines()]
    assert labels == ["Y = 200", "Y = 400"]


def test_物価は貨幣量に比例し産出量が大きいほど低い() -> None:
    ax = plot_money_and_prices(4, [200, 400], [0, 100, 200]).axes[0]
    xs, low_output = xy(ax.get_lines()[0])
    _, high_output = xy(ax.get_lines()[1])
    assert xs == [0, 100, 200]
    assert low_output == pytest.approx([0, 2, 4])
    assert high_output == pytest.approx([0, 1, 2])


def test_貨幣量と物価の図の軸の名前() -> None:
    ax = plot_money_and_prices(4, [200], [0, 100]).axes[0]
    assert ax.get_xlabel() == "Money supply M"
    assert ax.get_ylabel() == "Price level P"


def test_純輸出の図は為替レートが上がると右上がり() -> None:
    ax = plot_net_exports([105, 125, 145], 20, 125, 0.4).axes[0]
    xs, ys = xy(ax.get_lines()[0])
    assert xs == [105, 125, 145]
    assert ys == pytest.approx([12, 20, 28])


def test_純輸出の図は基準の点に印を付ける() -> None:
    ax = plot_net_exports([105, 125, 145], 20, 125, 0.4).axes[0]
    xs, ys = xy(ax.get_lines()[1])
    assert (xs, ys) == ([125], [20])


def test_純輸出の図の軸の名前() -> None:
    ax = plot_net_exports([105, 125], 20, 125, 0.4).axes[0]
    assert ax.get_xlabel() == "Exchange rate (yen per dollar)"
    assert ax.get_ylabel() == "Net exports"
