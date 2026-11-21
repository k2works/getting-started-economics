"""第 1 章: 付加価値と成長会計の図のテスト。"""

from collections.abc import Iterable

import pytest
from matplotlib.artist import Artist
from matplotlib.patches import Rectangle

from lib.chapter01.gdp import growth_accounting
from lib.chapter01.plot import plot_growth_accounting, plot_value_added

OUTPUT = [300, 700, 1000]
INTERMEDIATE = [0, 300, 700]


def heights(ax_patches: Iterable[Artist]) -> list[float]:
    return [p.get_height() for p in ax_patches if isinstance(p, Rectangle)]


def test_付加価値の図は段階ごとに中間投入と付加価値の2本の積み上げ() -> None:
    ax = plot_value_added(["Wheat", "Flour", "Bread"], OUTPUT, INTERMEDIATE).axes[0]
    assert len(ax.patches) == 6
    assert [t.get_text() for t in ax.get_xticklabels()] == ["Wheat", "Flour", "Bread"]


def test_積み上げた高さは生産額に等しい() -> None:
    ax = plot_value_added(["Wheat", "Flour", "Bread"], OUTPUT, INTERMEDIATE).axes[0]
    values = heights(ax.patches)
    intermediate, added = values[:3], values[3:]
    assert intermediate == pytest.approx(INTERMEDIATE)
    assert added == pytest.approx([300, 400, 300])
    totals = [i + a for i, a in zip(intermediate, added, strict=True)]
    assert totals == pytest.approx(OUTPUT)


def test_付加価値の棒は中間投入の上に積み上がる() -> None:
    ax = plot_value_added(["Wheat", "Flour", "Bread"], OUTPUT, INTERMEDIATE).axes[0]
    bars = [p for p in ax.patches if isinstance(p, Rectangle)]
    intermediate_bars, added_bars = bars[:3], bars[3:]
    assert [b.get_y() for b in intermediate_bars] == pytest.approx([0, 0, 0])
    assert [b.get_y() for b in added_bars] == pytest.approx(INTERMEDIATE)


def test_成長会計の図は3本の棒で高さは各寄与() -> None:
    result = growth_accounting(6.0, 7.0, 0.4, 4.0, 0.6)
    ax = plot_growth_accounting(result).axes[0]
    assert [t.get_text() for t in ax.get_xticklabels()] == [
        "Labor",
        "Capital",
        "Technology",
    ]
    assert heights(ax.patches) == pytest.approx([2.8, 2.4, 0.8])


def test_軸の名前() -> None:
    ax = plot_value_added(["A"], [1], [0]).axes[0]
    assert ax.get_ylabel() == "Value (10,000 yen)"
    result = growth_accounting(6.0, 7.0, 0.4, 4.0, 0.6)
    assert plot_growth_accounting(result).axes[0].get_ylabel() == "Growth (points)"
