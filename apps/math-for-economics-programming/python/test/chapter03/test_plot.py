import math

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes

from lib.chapter03.interest import compound_amount, continuous_compound_amount
from lib.chapter03.plot import plot_compound_growth


def _series(ax: Axes, label: str) -> tuple[list[float], list[float]]:
    line = next(x for x in ax.lines if x.get_label() == label)
    xs = np.asarray(line.get_xdata(), dtype=float).tolist()
    ys = np.asarray(line.get_ydata(), dtype=float).tolist()
    return xs, ys


def _log_steps(ys: list[float]) -> list[float]:
    """隣り合う値の、常用対数の差（対数目盛での、1 年あたりの上がり幅）。"""
    return [math.log10(b) - math.log10(a) for a, b in zip(ys, ys[1:], strict=False)]


def test_図は線形目盛と対数目盛の2つで軸と凡例がある() -> None:
    linear, logarithmic = plot_compound_growth(100, 0.05, 50).axes
    assert linear.get_yscale() == "linear"
    assert logarithmic.get_yscale() == "log"
    for ax in (linear, logarithmic):
        assert ax.get_xlabel() == "Years"
        assert ax.get_ylabel().startswith("Amount")
        assert ax.get_legend() is not None
    plt.close("all")


def test_年1回の複利は毎年の点で元利合計に等しい() -> None:
    for ax in plot_compound_growth(100, 0.05, 50).axes:
        xs, ys = _series(ax, "Annual compounding")
        assert xs == list(range(51))
        assert ys == pytest.approx([compound_amount(100, 0.05, t) for t in xs])


def test_連続複利の曲線は0年から最後の年まで() -> None:
    ax = plot_compound_growth(100, 0.05, 50).axes[0]
    xs, ys = _series(ax, "Continuous compounding")
    assert (xs[0], xs[-1]) == (0, 50)
    assert ys[0] == pytest.approx(100)
    assert ys[-1] == pytest.approx(continuous_compound_amount(100, 0.05, 50))


def test_単利は毎年同じ額ずつ増え対数目盛では増え方が鈍る() -> None:
    linear, logarithmic = plot_compound_growth(100, 0.05, 50).axes
    xs, ys = _series(linear, "Simple interest")
    assert xs == list(range(51))
    assert (ys[0], ys[-1]) == (100, 350)
    assert [b - a for a, b in zip(ys, ys[1:], strict=False)] == pytest.approx([5] * 50)
    steps = _log_steps(_series(logarithmic, "Simple interest")[1])
    assert all(a > b for a, b in zip(steps, steps[1:], strict=False))


def test_対数目盛では複利の点が一直線に並ぶ() -> None:
    ax = plot_compound_growth(100, 0.05, 50).axes[1]
    steps = _log_steps(_series(ax, "Annual compounding")[1])
    assert steps == pytest.approx([math.log10(1.05)] * 50)


def test_1年だけの図は描けて0年の図は描かない() -> None:
    ax = plot_compound_growth(100, 0.05, 1).axes[0]
    assert _series(ax, "Annual compounding") == ([0, 1], pytest.approx([100, 105]))
    with pytest.raises(ValueError):
        plot_compound_growth(100, 0.05, 0)
