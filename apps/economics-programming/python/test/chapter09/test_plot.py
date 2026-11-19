"""第 9 章: 45 度線分析（ケインズの交差図）の図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D

from lib.chapter09.linear import income_determination, multiplier
from lib.chapter09.plot import plot_keynesian_cross

MODEL = {"autonomous_consumption": 20, "mpc": 0.8, "investment": 30}


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def test_交差図には45度線と総支出の線と均衡点がある() -> None:
    ax = plot_keynesian_cross(**MODEL).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "45-degree line",
        "Expenditure",
        "Equilibrium",
    ]


def test_45度線は所得と支出が等しい点の集まり() -> None:
    ax = plot_keynesian_cross(**MODEL).axes[0]
    assert all(x == pytest.approx(y) for x, y in xy(ax.lines[0]))


def test_総支出の線は切片が消費と投資の和で傾きが限界消費性向() -> None:
    (x0, y0), (x1, y1) = xy(plot_keynesian_cross(**MODEL).axes[0].lines[1])[:2]
    assert y0 == pytest.approx(20 + 30)  # 所得 0 のときの支出 C0 + I
    assert (y1 - y0) / (x1 - x0) == pytest.approx(0.8)


def test_均衡点は45度線と総支出の線の交点で所得250() -> None:
    ax = plot_keynesian_cross(**MODEL).axes[0]
    income, _ = income_determination(**MODEL)
    assert xy(ax.lines[2])[0] == pytest.approx((income, income))
    assert income == pytest.approx(250)


def test_投資が増えると総支出の線が上にずれ均衡所得は乗数倍に増える() -> None:
    ax = plot_keynesian_cross(**MODEL, new_investment=40).axes[0]
    assert [line.get_label() for line in ax.lines][-2:] == [
        "Expenditure (after)",
        "Equilibrium (after)",
    ]
    before = xy(ax.lines[2])[0][0]
    after = xy(ax.lines[4])[0][0]
    assert after - before == pytest.approx((40 - 30) * multiplier(0.8))


def test_投資が増えた後の総支出の線は切片が60で傾きは変わらない() -> None:
    ax = plot_keynesian_cross(**MODEL, new_investment=40).axes[0]
    (x0, y0), (x1, y1) = xy(ax.lines[3])[:2]
    assert y0 == pytest.approx(20 + 40)
    assert (y1 - y0) / (x1 - x0) == pytest.approx(0.8)
