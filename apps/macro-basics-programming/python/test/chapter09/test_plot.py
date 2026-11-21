"""第 9 章: 政策の効果の図のテスト。"""

import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter09.plot import plot_liquidity_trap, plot_policy_shifts

SPEC = {
    "mpc": 0.6,
    "b": 20,
    "intercept": 450,
    "k": 0.5,
    "h": 100,
    "real_money": 250,
}


def xs(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_xdata())]


def ys(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_ydata())]


def policy_axes() -> list[Axes]:
    fig = plot_policy_shifts(
        **SPEC,
        delta_government=10,
        delta_real_money=10,
        income_min=600,
        income_max=1200,
    )
    return fig.axes


def test_政策の図は財政政策と金融政策の2枚が左右に並ぶ() -> None:
    left, right = policy_axes()
    assert left.get_position().x1 < right.get_position().x0
    assert left.get_position().y0 == pytest.approx(right.get_position().y0)


def test_財政政策の図はISだけが動く() -> None:
    ax = policy_axes()[0]
    labels = [line.get_label() for line in ax.lines]
    assert labels == [
        "IS",
        "IS after fiscal policy",
        "LM",
        "Equilibrium before",
        "Equilibrium after",
    ]
    is_line, is_after, lm_line, before, after = ax.lines
    assert ys(is_line) == pytest.approx([10.5, -1.5])
    assert ys(is_after) == pytest.approx([11, -1])
    assert ys(lm_line) == pytest.approx([0.5, 3.5])
    assert xs(before) == pytest.approx([1000])
    assert ys(before) == pytest.approx([2.5])
    assert xs(after) == pytest.approx([1020])
    assert ys(after) == pytest.approx([2.6])


def test_金融政策の図はLMだけが動く() -> None:
    ax = policy_axes()[1]
    labels = [line.get_label() for line in ax.lines]
    assert labels == [
        "IS",
        "LM",
        "LM after monetary policy",
        "Equilibrium before",
        "Equilibrium after",
    ]
    is_line, lm_line, lm_after, before, after = ax.lines
    assert ys(is_line) == pytest.approx([10.5, -1.5])
    assert ys(lm_line) == pytest.approx([0.5, 3.5])
    assert ys(lm_after) == pytest.approx([0.4, 3.4])
    assert xs(before) == pytest.approx([1000])
    assert xs(after) == pytest.approx([1004])
    assert ys(after) == pytest.approx([2.42])


def test_政策の図の軸の名前() -> None:
    for ax in policy_axes():
        assert ax.get_xlabel() == "Income Y"
        assert ax.get_ylabel() == "Interest rate r"
        assert ax.get_ylim()[0] == 0


def test_流動性のわなの図はLMが水平() -> None:
    fig = plot_liquidity_trap(
        0.6, 20, 450, 2.5, delta_government=10, income_min=600, income_max=1200
    )
    ax = fig.axes[0]
    labels = [line.get_label() for line in ax.lines]
    assert labels == [
        "IS",
        "IS after fiscal policy",
        "LM (liquidity trap)",
        "Equilibrium before",
        "Equilibrium after",
    ]
    is_line, is_after, lm_line, before, after = ax.lines
    assert ys(lm_line) == pytest.approx([2.5, 2.5])
    assert xs(lm_line) == pytest.approx([600, 1200])
    assert ys(is_line) == pytest.approx([10.5, -1.5])
    assert ys(is_after) == pytest.approx([11, -1])
    assert xs(before) == pytest.approx([1000])
    assert xs(after) == pytest.approx([1025])
    assert ys(before) == pytest.approx([2.5])
    assert ys(after) == pytest.approx([2.5])


def test_流動性のわなの図の軸の名前() -> None:
    ax = plot_liquidity_trap(0.6, 20, 450, 2.5, 10, 600, 1200).axes[0]
    assert ax.get_xlabel() == "Income Y"
    assert ax.get_ylabel() == "Interest rate r"
    assert ax.get_ylim()[0] == 0
