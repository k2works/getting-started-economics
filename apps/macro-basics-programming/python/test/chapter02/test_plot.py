"""第 2 章: 三面等価と産業連関表の図のテスト。"""

from collections.abc import Iterable

import matplotlib

matplotlib.use("Agg")

import pytest  # noqa: E402
from matplotlib.artist import Artist  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from lib.chapter02.plot import plot_io_output, plot_three_way  # noqa: E402

SIDES = {
    "Production": {"Industry A": 100, "Industry B": 200, "Industry C": 200},
    "Distribution": {"Compensation": 280, "Surplus": 120, "Others": 100},
    "Expenditure": {"Consumption": 290, "Investment": 110, "Others": 100},
}


def bars(patches: Iterable[Artist]) -> list[Rectangle]:
    return [p for p in patches if isinstance(p, Rectangle)]


def test_三面等価の図は3つの面の積み上げ棒() -> None:
    ax = plot_three_way(SIDES).axes[0]
    assert len(bars(ax.patches)) == 9
    assert [t.get_text() for t in ax.get_xticklabels()] == [
        "Production",
        "Distribution",
        "Expenditure",
    ]


def test_積み上げた高さは3つの面ですべて等しい() -> None:
    ax = plot_three_way(SIDES).axes[0]
    rectangles = bars(ax.patches)
    totals = [
        sum(r.get_height() for r in rectangles[start : start + 3])
        for start in (0, 3, 6)
    ]
    assert totals == pytest.approx([500, 500, 500])


def test_三面等価の棒は下の棒の上に積み上がる() -> None:
    ax = plot_three_way(SIDES).axes[0]
    rectangles = bars(ax.patches)
    assert [r.get_y() for r in rectangles[:3]] == pytest.approx([0, 100, 300])
    assert [r.get_height() for r in rectangles[3:6]] == pytest.approx([280, 120, 100])


def test_三面等価の図は部分に名前を付ける() -> None:
    ax = plot_three_way(SIDES).axes[0]
    labels = [t.get_text() for t in ax.texts]
    assert labels[:3] == ["Industry A", "Industry B", "Industry C"]
    assert len(labels) == 9
    # 名前は、各部分の真ん中（棒の位置 0 の、下から 50・200・400）に置く
    assert [t.get_position() for t in ax.texts[:3]] == [(0, 50), (0, 200), (0, 400)]
    assert ax.texts[3].get_position()[0] == 1


def test_産業連関表の図は最終需要と生産量の2本ずつ() -> None:
    a = [[0.2, 0.3], [0.4, 0.1]]
    ax = plot_io_output(a, [100, 200], ["Sector 1", "Sector 2"]).axes[0]
    heights = [r.get_height() for r in bars(ax.patches)]
    assert heights == pytest.approx([100, 200, 250, 1000 / 3])
    assert [t.get_text() for t in ax.get_xticklabels()] == ["Sector 1", "Sector 2"]
    legend = ax.get_legend()
    assert legend is not None
    assert [t.get_text() for t in legend.get_texts()] == ["Final demand", "Output"]


def test_軸の名前() -> None:
    assert plot_three_way(SIDES).axes[0].get_ylabel() == "GDP (100 million yen)"
    ax = plot_io_output([[0.2]], [1], ["A"]).axes[0]
    assert ax.get_ylabel() == "Value (100 million yen)"
