"""第 8 章: 標準誤差の比較の図のテスト。"""

from typing import Any

import pytest

from lib.chapter08.plot import plot_standard_errors

VALUES = {"Actual (SD of estimates)": 0.28, "Classical": 0.22, "Robust (HC1)": 0.27}


def test_3本の棒を描く() -> None:
    ax = plot_standard_errors(VALUES).axes[0]
    bars: list[Any] = list(ax.patches)
    assert [p.get_height() for p in bars] == pytest.approx([0.28, 0.22, 0.27])
    assert [t.get_text() for t in ax.get_xticklabels()] == list(VALUES)


def test_軸の名前() -> None:
    ax = plot_standard_errors(VALUES).axes[0]
    assert ax.get_ylabel() == "Standard error of the slope"
