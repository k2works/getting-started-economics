"""第 6 章: 標本の大きさごとの、推定値の分布の図のテスト。"""

from typing import Any

import numpy as np
import pytest

from lib.chapter06.plot import plot_estimate_distributions

ESTIMATES = {
    30: np.array([0.2, 0.5, 0.8, 0.5]),
    500: np.array([0.45, 0.5, 0.55, 0.5]),
}


def test_標本の大きさごとにヒストグラムを描き真の値の線を引く() -> None:
    ax = plot_estimate_distributions(ESTIMATES, 0.5).axes[0]
    assert len(ax.patches) == 2 * 30
    legend = ax.get_legend()
    assert legend is not None
    assert [t.get_text() for t in legend.get_texts()] == [
        "n = 30",
        "n = 500",
        "True value",
    ]
    assert [line.get_label() for line in ax.lines] == ["True value"]


def test_ヒストグラムは密度で描き面積は1() -> None:
    ax = plot_estimate_distributions(ESTIMATES, 0.5).axes[0]
    bars: list[Any] = list(ax.patches)
    for patches in (bars[:30], bars[30:]):
        area = sum(p.get_height() * p.get_width() for p in patches)
        assert area == pytest.approx(1)


def test_軸の名前() -> None:
    ax = plot_estimate_distributions(ESTIMATES, 0.5).axes[0]
    assert ax.get_xlabel() == "Estimated slope"
    assert ax.get_ylabel() == "Density"
