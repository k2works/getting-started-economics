"""第 4 章: 費用曲線の図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D

from lib.chapter04.cost import average_cost, average_variable_cost, marginal_cost
from lib.chapter04.plot import plot_cost_curves


def points(line: Line2D) -> dict[float, float]:
    data: Any = line.get_xydata()
    return {round(float(x), 6): float(y) for x, y in data}


def test_費用曲線の図にはMC_AVC_ACの3本の線と操業停止点がある() -> None:
    ax = plot_cost_curves().axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "MC",
        "AVC",
        "AC",
        "Shutdown point",
    ]


def test_限界費用の線は費用関数の限界費用と同じ値() -> None:
    mc = points(plot_cost_curves().axes[0].lines[0])
    assert mc[2.0] == pytest.approx(marginal_cost(2.0))
    assert mc[5.0] == pytest.approx(marginal_cost(5.0))


def test_MCとAVCは生産量3で交わる() -> None:
    ax = plot_cost_curves().axes[0]
    mc, avc = points(ax.lines[0]), points(ax.lines[1])
    assert mc[3.0] == pytest.approx(avc[3.0])
    assert avc[3.0] == pytest.approx(average_variable_cost(3.0))


def test_操業停止点は生産量3_価格6() -> None:
    marker: Any = plot_cost_curves().axes[0].lines[3].get_xydata()
    assert (float(marker[0][0]), float(marker[0][1])) == pytest.approx((3, 6))


def test_平均費用の線は平均費用関数と同じ値でAVCより常に上にある() -> None:
    ax = plot_cost_curves().axes[0]
    ac, avc = points(ax.lines[2]), points(ax.lines[1])
    assert ac[2.0] == pytest.approx(average_cost(2.0))
    assert all(ac[q] > avc[q] for q in ac)
