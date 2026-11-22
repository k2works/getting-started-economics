import pytest

from lib.chapter05.derivative import numerical_derivative
from lib.chapter12.recurrence import recurrence_half_life
from lib.chapter12.solow import (
    golden_rule_saving_by_grid,
    solow_capital_path,
    solow_convergence_factor,
    solow_next_capital,
    solow_next_capital_with_growth,
    solow_steady_state_capital,
    solow_steady_state_consumption,
    solow_steady_state_with_growth,
)

ALPHA = 1 / 3


def test_来期の資本は貯蓄と減耗後の資本の和() -> None:
    # k = 8 なら f(k) = 2。0.3 × 2 + 0.9 × 8 = 7.8
    assert solow_next_capital(8, 0.3, ALPHA, 0.1) == pytest.approx(7.8)
    # k = 16・α = 0.5 なら f(k) = 4。0.2 × 4 + 0.95 × 16 = 16
    assert solow_next_capital(16, 0.2, 0.5, 0.05) == pytest.approx(16)


def test_資本の経路は来期の資本を順に計算した列() -> None:
    path = solow_capital_path(8, 0.3, ALPHA, 0.1, 2)
    assert path == pytest.approx([8, 7.8, solow_next_capital(7.8, 0.3, ALPHA, 0.1)])


def test_定常状態の資本はsをδで割った値の1マイナスα分の1乗() -> None:
    assert solow_steady_state_capital(0.3, ALPHA, 0.1) == pytest.approx(3**1.5)
    assert solow_steady_state_capital(0.2, 0.5, 0.05) == pytest.approx(16)


def test_定常状態では貯蓄が減耗にちょうど等しい() -> None:
    for saving, alpha, delta in [(0.3, ALPHA, 0.1), (0.25, 0.4, 0.08), (0.6, 0.7, 0.3)]:
        k = solow_steady_state_capital(saving, alpha, delta)
        assert saving * k**alpha == pytest.approx(delta * k)
        assert solow_next_capital(k, saving, alpha, delta) == pytest.approx(k)


@pytest.mark.parametrize("start", [0.5, 1, 10, 30])
def test_初期値が定常状態より小さくても大きくても収束する(start: float) -> None:
    steady = solow_steady_state_capital(0.3, ALPHA, 0.1)
    path = solow_capital_path(start, 0.3, ALPHA, 0.1, 400)
    assert path[-1] == pytest.approx(steady, abs=1e-9)
    gaps = [k - steady for k in path[:100]]
    # 差の符号は変わらず（行き過ぎない）、大きさは毎期小さくなる
    assert all(g * gaps[0] > 0 for g in gaps)
    assert all(abs(g1) > abs(g2) for g1, g2 in zip(gaps, gaps[1:], strict=False))


def test_定常状態の消費は生産から減耗を引いた値() -> None:
    k = solow_steady_state_capital(0.3, ALPHA, 0.1)
    expected = k**ALPHA - 0.1 * k
    assert solow_steady_state_consumption(0.3, ALPHA, 0.1) == pytest.approx(expected)
    # 消費は、生産の 1 − s 倍でもある
    assert expected == pytest.approx(0.7 * k**ALPHA)
    assert solow_steady_state_consumption(0.2, 0.5, 0.05) == pytest.approx(3.2)


@pytest.mark.parametrize(("alpha", "delta"), [(ALPHA, 0.1), (0.4, 0.05), (0.25, 0.2)])
def test_定常状態の消費を最大にする貯蓄率は格子探索でもαになる(
    alpha: float, delta: float
) -> None:
    assert golden_rule_saving_by_grid(alpha, delta, 1001) == pytest.approx(
        alpha, abs=1e-3
    )


def test_黄金律では資本の限界生産物が減耗率に等しい() -> None:
    k = solow_steady_state_capital(ALPHA, ALPHA, 0.1)
    slope = numerical_derivative(lambda x: x**ALPHA, k)
    assert slope == pytest.approx(0.1)


def test_貯蓄率が黄金律より高くても低くても定常状態の消費は減る() -> None:
    best = solow_steady_state_consumption(ALPHA, ALPHA, 0.1)
    for saving in (0.2, 0.3, 0.4, 0.6):
        assert solow_steady_state_consumption(saving, ALPHA, 0.1) < best
    assert solow_steady_state_capital(0.6, ALPHA, 0.1) > solow_steady_state_capital(
        ALPHA, ALPHA, 0.1
    )


def test_収束の速さは定常状態での漸化式の傾き() -> None:
    factor = solow_convergence_factor(ALPHA, 0.1)
    assert factor == pytest.approx(1 - 0.1 * (2 / 3))
    k = solow_steady_state_capital(0.3, ALPHA, 0.1)
    slope = numerical_derivative(lambda x: solow_next_capital(x, 0.3, ALPHA, 0.1), k)
    assert slope == pytest.approx(factor)
    assert solow_convergence_factor(0.5, 0.05) == pytest.approx(0.975)


def test_定常状態の近くでは差が毎期ほぼ収束の速さ倍になる() -> None:
    steady = solow_steady_state_capital(0.3, ALPHA, 0.1)
    path = solow_capital_path(steady * 1.001, 0.3, ALPHA, 0.1, 2)
    ratio = (path[2] - steady) / (path[1] - steady)
    assert ratio == pytest.approx(solow_convergence_factor(ALPHA, 0.1), abs=1e-4)
    assert recurrence_half_life(solow_convergence_factor(ALPHA, 0.1)) == pytest.approx(
        10.05, abs=0.01
    )


def test_人口成長も技術進歩もなければ基本のモデルと同じ() -> None:
    assert solow_next_capital_with_growth(8, 0.3, ALPHA, 0.1, 0, 0) == pytest.approx(
        solow_next_capital(8, 0.3, ALPHA, 0.1)
    )
    assert solow_steady_state_with_growth(0.3, ALPHA, 0.1, 0, 0) == pytest.approx(
        solow_steady_state_capital(0.3, ALPHA, 0.1)
    )


def test_人口成長と技術進歩がある定常状態は反復の行き着く先() -> None:
    # 分母 δ + n + g + n·g = 0.1 + 0.02 + 0.01 + 0.0002 = 0.1302
    steady = solow_steady_state_with_growth(0.3, ALPHA, 0.1, 0.02, 0.01)
    assert steady == pytest.approx((0.3 / 0.1302) ** 1.5)
    k = 1.0
    for _ in range(400):
        k = solow_next_capital_with_growth(k, 0.3, ALPHA, 0.1, 0.02, 0.01)
    assert k == pytest.approx(steady)
    assert steady < solow_steady_state_capital(0.3, ALPHA, 0.1)


def test_資本が0なら生産も貯蓄も0で0のまま() -> None:
    assert solow_capital_path(0, 0.3, ALPHA, 0.1, 3) == [0, 0, 0, 0]


def test_減耗率が1なら来期の資本は貯蓄だけ() -> None:
    assert solow_next_capital(27, 0.3, ALPHA, 1) == pytest.approx(0.9)


def test_貯蓄率0なら定常状態は0で貯蓄率1なら消費は0() -> None:
    assert solow_steady_state_capital(0, ALPHA, 0.1) == 0
    assert solow_steady_state_consumption(0, ALPHA, 0.1) == 0
    assert solow_steady_state_consumption(1, ALPHA, 0.1) == pytest.approx(0)


def test_0期の経路は初期値だけ() -> None:
    assert solow_capital_path(5, 0.3, ALPHA, 0.1, 0) == [5]


@pytest.mark.parametrize(
    ("saving", "alpha", "delta"),
    [
        (-0.1, ALPHA, 0.1),
        (1.1, ALPHA, 0.1),
        (0.3, 0, 0.1),
        (0.3, 1, 0.1),
        (0.3, ALPHA, 0),
        (0.3, ALPHA, 1.2),
    ],
)
def test_貯蓄率とαと減耗率の範囲の外では計算しない(
    saving: float, alpha: float, delta: float
) -> None:
    with pytest.raises(ValueError):
        solow_next_capital(8, saving, alpha, delta)
    with pytest.raises(ValueError):
        solow_steady_state_capital(saving, alpha, delta)


def test_負の資本や負の期数では計算しない() -> None:
    with pytest.raises(ValueError):
        solow_next_capital(-1, 0.3, ALPHA, 0.1)
    with pytest.raises(ValueError):
        solow_capital_path(5, 0.3, ALPHA, 0.1, -1)


def test_格子探索には2点以上が必要で3点なら真ん中の貯蓄率() -> None:
    with pytest.raises(ValueError):
        golden_rule_saving_by_grid(ALPHA, 0.1, 1)
    # 格子 0・0.5・1 のうち、両端の消費は 0（何も貯めない・全部貯める）
    assert golden_rule_saving_by_grid(ALPHA, 0.1, 3) == 0.5


def test_人口が減りすぎて分母が正でなければ定常状態は決まらない() -> None:
    with pytest.raises(ValueError):
        solow_steady_state_with_growth(0.3, ALPHA, 0.1, -0.1, 0)
    with pytest.raises(ValueError):
        solow_next_capital_with_growth(8, 0.3, ALPHA, 0.1, -1, 0)
