"""第 5 章: ギャップと安定化政策のテスト。"""

import pytest

from lib.chapter04.multiplier import equilibrium_income, income_change
from lib.chapter05.stabilization import (
    classify_gap,
    income_swing,
    output_gap,
    required_spending_change,
    required_tax_change,
    stabilizer_multiplier,
    swing_reduction,
)

# 完全雇用国民所得 300。限界消費性向 0.6、独立支出 A = 100 の均衡所得は 250
FULL = 300
EQUILIBRIUM = 250


def test_ギャップは完全雇用所得から均衡所得を引いた値() -> None:
    assert output_gap(FULL, EQUILIBRIUM) == 50
    assert output_gap(200, EQUILIBRIUM) == -50


def test_正のギャップはデフレギャップで負はインフレギャップ() -> None:
    assert classify_gap(50) == "デフレギャップ"
    assert classify_gap(-50) == "インフレギャップ"


def test_小さなギャップでも0でなければギャップがある() -> None:
    assert classify_gap(0.5) == "デフレギャップ"
    assert classify_gap(-0.5) == "インフレギャップ"


def test_ギャップが0なら均衡() -> None:
    assert classify_gap(0) == "ギャップなし"
    assert classify_gap(1e-12) == "ギャップなし"


def test_デフレギャップを埋める政府支出の増加は20() -> None:
    assert required_spending_change(50, mpc=0.6) == pytest.approx(20)


def test_インフレギャップには支出削減が必要で符号は負() -> None:
    assert required_spending_change(-50, mpc=0.6) == pytest.approx(-20)


def test_デフレギャップを埋める租税の変化は減税で符号は負() -> None:
    assert required_tax_change(50, mpc=0.6) == pytest.approx(-50 / 1.5)
    assert required_tax_change(-50, mpc=0.6) > 0


def test_同じギャップを埋めるのに減税は支出増より大きな額が要る() -> None:
    spending = required_spending_change(50, mpc=0.6)
    tax = required_tax_change(50, mpc=0.6)
    assert abs(tax) > abs(spending)


def test_必要な政府支出増を実行すると均衡所得は完全雇用に届く() -> None:
    base = {
        "mpc": 0.6,
        "autonomous_consumption": 40,
        "investment": 30,
        "net_exports": 0,
    }
    y = equilibrium_income(**base, government=30)
    gap = output_gap(FULL, y)
    delta = required_spending_change(gap, 0.6)
    assert equilibrium_income(**base, government=30 + delta) == pytest.approx(FULL)
    assert income_change(0.6, delta_government=delta) == pytest.approx(gap)


def test_必要な減税を実行すると均衡所得は完全雇用に届く() -> None:
    delta_tax = required_tax_change(50, 0.6)
    assert income_change(0.6, delta_tax=delta_tax) == pytest.approx(50)


def test_税率0の乗数は通常の乗数に等しい() -> None:
    assert stabilizer_multiplier(0.6, 0.0) == pytest.approx(2.5)


def test_比例税があると乗数は小さくなる() -> None:
    assert stabilizer_multiplier(0.6, 0.2) == pytest.approx(1 / 0.52)
    assert stabilizer_multiplier(0.6, 0.2) < 2.5


def test_税率が高いほど乗数は小さい() -> None:
    low = stabilizer_multiplier(0.8, 0.1)
    high = stabilizer_multiplier(0.8, 0.3)
    assert high < low


def test_独立支出が変動したときの所得の振れ幅は比例税で小さくなる() -> None:
    assert income_swing(0.6, 0.0, 10) == pytest.approx(25)
    assert income_swing(0.6, 0.2, 10) == pytest.approx(10 / 0.52)
    assert income_swing(0.6, 0.2, 10) < income_swing(0.6, 0.0, 10)


def test_負の変動でも振れ幅は同じ大きさで符号だけ逆() -> None:
    assert income_swing(0.6, 0.2, -10) == pytest.approx(-income_swing(0.6, 0.2, 10))


def test_振れ幅の縮小の割合は乗数の比で決まる() -> None:
    assert swing_reduction(0.6, 0.0) == pytest.approx(0)
    assert swing_reduction(0.6, 0.2) == pytest.approx(1 - 0.4 / 0.52)
    assert 0 < swing_reduction(0.6, 0.2) < 1


def test_税率が範囲外ならエラー() -> None:
    with pytest.raises(ValueError, match="税率"):
        stabilizer_multiplier(0.6, -0.1)
    with pytest.raises(ValueError, match="税率"):
        stabilizer_multiplier(0.6, 1.0)


def test_限界消費性向が範囲外ならエラー() -> None:
    with pytest.raises(ValueError, match="1 未満"):
        stabilizer_multiplier(1.0, 0.2)
    with pytest.raises(ValueError, match="1 未満"):
        required_spending_change(50, mpc=1.0)
