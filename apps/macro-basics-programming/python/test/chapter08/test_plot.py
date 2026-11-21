"""第 8 章: IS 曲線と IS-LM の均衡の図のテスト。"""

import numpy as np
import pytest
from matplotlib.lines import Line2D

from lib.chapter08.plot import plot_is_curves, plot_is_lm_equilibrium


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_ydata())]


def test_IS曲線の図は利子感応度ごとに1本ずつ() -> None:
    fig = plot_is_curves(0.6, 450, [20, 40], interest_max=10)
    lines = fig.axes[0].lines
    assert [line.get_label() for line in lines] == ["b = 20", "b = 40"]


def test_IS曲線は利子率0と最大の2点を結ぶ() -> None:
    ax = plot_is_curves(0.6, 450, [20, 40], interest_max=10).axes[0]
    first, second = ax.lines
    assert ys(first) == pytest.approx([0, 10])
    assert xs(first) == pytest.approx([1125, 625])
    assert xs(second) == pytest.approx([1125, 125])


def test_IS曲線は利子感応度が大きいほど緩やか() -> None:
    ax = plot_is_curves(0.6, 450, [20, 40], interest_max=10).axes[0]
    first, second = ax.lines
    drop_steep = xs(first)[0] - xs(first)[1]
    drop_flat = xs(second)[0] - xs(second)[1]
    assert drop_flat > drop_steep


def test_IS曲線の図の軸の名前() -> None:
    ax = plot_is_curves(0.6, 450, [20], interest_max=10).axes[0]
    assert ax.get_xlabel() == "Income Y"
    assert ax.get_ylabel() == "Interest rate r"


def test_IS_LMの図はISとLMと均衡点() -> None:
    ax = plot_is_lm_equilibrium(0.6, 20, 450, 0.5, 100, 250, 600, 1200).axes[0]
    is_line, lm_line, point = ax.lines
    assert [line.get_label() for line in ax.lines] == ["IS", "LM", "Equilibrium"]
    assert xs(is_line) == pytest.approx([600, 1200])
    assert ys(is_line) == pytest.approx([10.5, -1.5])
    assert xs(lm_line) == pytest.approx([600, 1200])
    assert ys(lm_line) == pytest.approx([0.5, 3.5])
    assert xs(point) == pytest.approx([1000])
    assert ys(point) == pytest.approx([2.5])


def test_IS_LMの図の軸の名前と下限() -> None:
    ax = plot_is_lm_equilibrium(0.6, 20, 450, 0.5, 100, 250, 600, 1200).axes[0]
    assert ax.get_xlabel() == "Income Y"
    assert ax.get_ylabel() == "Interest rate r"
    assert ax.get_ylim()[0] == 0
