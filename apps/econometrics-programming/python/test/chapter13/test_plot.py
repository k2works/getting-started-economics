"""第 13 章: 検定の棄却率の図のテスト。"""

from typing import Any

import pytest

from lib.chapter13.plot import plot_rejection_rates

RATES = {"Valid (0)": 0.054, "Invalid (0.1)": 0.344, "Invalid (0.3)": 0.998}


def test_棄却率の棒と有意水準の線() -> None:
    ax = plot_rejection_rates(RATES, 0.05).axes[0]
    bars: list[Any] = list(ax.patches)
    assert [p.get_height() for p in bars] == pytest.approx([0.054, 0.344, 0.998])
    assert [t.get_text() for t in ax.get_xticklabels()] == list(RATES)
    assert [line.get_label() for line in ax.lines] == ["Significance level"]
    line_y: Any = ax.lines[0].get_ydata()
    assert [float(v) for v in line_y] == [0.05, 0.05]


def test_軸の名前と範囲() -> None:
    ax = plot_rejection_rates(RATES, 0.05).axes[0]
    assert ax.get_ylabel() == "Rejection rate"
    assert ax.get_ylim() == (0, 1)
