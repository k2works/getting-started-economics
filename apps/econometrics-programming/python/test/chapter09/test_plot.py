"""第 9 章: 差分の差分の図のテスト。"""

from typing import Any

import pytest

from lib.chapter09.did import group_period_means
from lib.chapter09.plot import plot_did
from test.chapter09.test_did import CELLS


def ys(line: Any) -> list[float]:
    values: Any = line.get_ydata()
    return [float(v) for v in values]


def test_処置群と対照群と反事実を描く() -> None:
    ax = plot_did(group_period_means(CELLS)).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Control",
        "Treated",
        "Counterfactual",
    ]
    assert ys(ax.lines[0]) == [8, 10]
    assert ys(ax.lines[1]) == [10, 15]


def test_反事実は処置群の処置前から対照群と同じだけ動く() -> None:
    ax = plot_did(group_period_means(CELLS)).axes[0]
    assert ys(ax.lines[2]) == pytest.approx([10, 12])
    assert ax.lines[2].get_linestyle() == "--"


def test_軸の名前() -> None:
    ax = plot_did(group_period_means(CELLS)).axes[0]
    assert ax.get_ylabel() == "Mean of y"
    assert [t.get_text() for t in ax.get_xticklabels()] == ["Before", "After"]
