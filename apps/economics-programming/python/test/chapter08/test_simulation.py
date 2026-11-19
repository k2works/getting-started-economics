"""第 8 章: 乱数とシミュレーションのテスト。"""

import random
import statistics

import pytest
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from lib.chapter08.simulation import (
    plot_histogram,
    roll_dice,
    running_means,
    sample_means,
    simulate_demand,
)


def test_同じ種なら同じ乱数列になる() -> None:
    first = simulate_demand(10, 100, 2, 10, 5, random.Random(0))
    second = simulate_demand(10, 100, 2, 10, 5, random.Random(0))
    assert first == second


def test_種が違えば乱数列も違う() -> None:
    first = simulate_demand(10, 100, 2, 10, 5, random.Random(0))
    second = simulate_demand(10, 100, 2, 10, 5, random.Random(1))
    assert first != second


def test_需要量の観測値は指定した個数だけ作られる() -> None:
    assert len(simulate_demand(10, 100, 2, 10, 250, random.Random(0))) == 250


def test_ばらつきが0なら需要は需要曲線のとおりになる() -> None:
    assert simulate_demand(10, 100, 2, 0, 3, random.Random(0)) == [80, 80, 80]


def test_負のばらつきは受け付けない() -> None:
    with pytest.raises(ValueError):
        simulate_demand(10, 100, 2, -1, 3, random.Random(0))


def test_累積平均は1個目なら観測値そのもの() -> None:
    assert running_means([4, 8, 6]) == pytest.approx([4, 6, 6])


def test_大数の法則_観測値が増えると平均は需要曲線の値80に近づく() -> None:
    values = simulate_demand(10, 100, 2, 10, 10_000, random.Random(0))
    means = running_means(values)
    assert abs(means[-1] - 80) < 0.5


def test_サイコロの目は1から6() -> None:
    rolls = roll_dice(1000, random.Random(0))
    assert set(rolls) == {1, 2, 3, 4, 5, 6}


def test_標本平均を試行回数だけ作る() -> None:
    assert len(sample_means(30, 200, random.Random(0))) == 200


def test_中心極限定理_標本平均の平均は3_5に近い() -> None:
    means = sample_means(30, 1000, random.Random(0))
    assert statistics.mean(means) == pytest.approx(3.5, abs=0.05)


def test_中心極限定理_標本平均の標準偏差は母集団の標準偏差を平方根nで割った値に近い() -> (
    None
):
    # サイコロの標準偏差は約 1.7078。n = 30 のとき 1.7078 / sqrt(30) = 約 0.3118
    means = sample_means(30, 1000, random.Random(0))
    assert statistics.stdev(means) == pytest.approx(0.3118, abs=0.03)


def test_ヒストグラムの棒の高さの合計は観測値の個数() -> None:
    values = sample_means(30, 500, random.Random(0))
    fig = plot_histogram(values, bins=20)
    ax = fig.axes[0]
    assert isinstance(fig, Figure)
    assert sum(p.get_height() for p in ax.patches if isinstance(p, Rectangle)) == 500
