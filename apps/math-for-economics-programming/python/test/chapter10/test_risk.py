import math
from fractions import Fraction

import pytest

from lib.chapter10.expectation import discrete_expected_value, discrete_variance
from lib.chapter10.risk import (
    absolute_risk_aversion,
    certainty_equivalent_of_lottery,
    classify_risk_attitude,
    expected_utility_of_lottery,
    relative_risk_aversion,
    risk_premium_of_lottery,
)

HALF = Fraction(1, 2)
COIN_FLIP = {0: HALF, 100: HALF}  # 50% で 0、50% で 100 の賭け
SIXTEEN_OR_HUNDRED = {16: HALF, 100: HALF}
UNEVEN = {0: Fraction(3, 4), 40: Fraction(1, 4)}


def _linear(x: float) -> float:
    return x


def _square(x: float) -> float:
    return x**2


def test_期待効用は効用かける確率の和() -> None:
    assert expected_utility_of_lottery(COIN_FLIP, math.sqrt) == 5
    assert expected_utility_of_lottery(SIXTEEN_OR_HUNDRED, math.sqrt) == 7
    eu = expected_utility_of_lottery(UNEVEN, math.sqrt)
    assert eu == pytest.approx(math.sqrt(40) / 4)
    assert expected_utility_of_lottery(COIN_FLIP, _linear) == 50


def test_確実性等価は期待効用と同じ効用を確実にくれる金額() -> None:
    assert certainty_equivalent_of_lottery(COIN_FLIP, math.sqrt) == pytest.approx(25)
    ce = certainty_equivalent_of_lottery(SIXTEEN_OR_HUNDRED, math.sqrt)
    assert ce == pytest.approx(49)
    # 効用 √x なら、確実性等価は期待効用の 2 乗（公式）。2 分法の数値と一致する
    expected = expected_utility_of_lottery(UNEVEN, math.sqrt) ** 2
    assert certainty_equivalent_of_lottery(UNEVEN, math.sqrt) == pytest.approx(expected)
    # 効用 ln x なら、確実性等価は e の期待効用乗（ここでは 25 と 100 の幾何平均 50）
    log_lottery = {25: HALF, 100: HALF}
    assert certainty_equivalent_of_lottery(log_lottery, math.log) == pytest.approx(50)


def test_危険プレミアムは期待値と確実性等価の差() -> None:
    assert risk_premium_of_lottery(COIN_FLIP, math.sqrt) == pytest.approx(25)
    assert risk_premium_of_lottery(SIXTEEN_OR_HUNDRED, math.sqrt) == pytest.approx(9)
    assert risk_premium_of_lottery(UNEVEN, math.sqrt) == pytest.approx(7.5)
    premium = risk_premium_of_lottery({25: HALF, 100: HALF}, math.log)
    assert premium == pytest.approx(12.5)


def test_凹の効用では期待値の効用が期待効用以上になる() -> None:
    for lottery in [COIN_FLIP, SIXTEEN_OR_HUNDRED, UNEVEN]:
        mean = float(discrete_expected_value(lottery))
        assert math.sqrt(mean) > expected_utility_of_lottery(lottery, math.sqrt)
        assert _square(mean) < expected_utility_of_lottery(lottery, _square)
        linear = expected_utility_of_lottery(lottery, _linear)
        assert _linear(mean) == pytest.approx(linear)


def test_効用の形で危険回避か危険中立か危険愛好かが決まる() -> None:
    assert classify_risk_attitude(COIN_FLIP, math.sqrt) == "averse"
    assert classify_risk_attitude(COIN_FLIP, _linear) == "neutral"
    assert classify_risk_attitude(COIN_FLIP, _square) == "loving"
    assert risk_premium_of_lottery(COIN_FLIP, _linear) == pytest.approx(0, abs=1e-9)
    # 凸の効用 x² では、確実性等価 √5000 ≈ 70.71 が期待値 50 を上回り、プレミアムは負
    ce = certainty_equivalent_of_lottery(COIN_FLIP, _square)
    assert ce == pytest.approx(math.sqrt(5000))
    assert risk_premium_of_lottery(COIN_FLIP, _square) < 0
    # 危険プレミアムが 1 より小さくても、正なら危険回避
    small = {90: HALF, 110: HALF}
    assert 0 < risk_premium_of_lottery(small, math.sqrt) < 1
    assert classify_risk_attitude(small, math.sqrt) == "averse"


def test_確実なくじの確実性等価はその金額でプレミアムは0() -> None:
    sure = {40: Fraction(1)}
    assert expected_utility_of_lottery(sure, math.sqrt) == pytest.approx(math.sqrt(40))
    assert certainty_equivalent_of_lottery(sure, math.sqrt) == 40
    assert risk_premium_of_lottery(sure, math.sqrt) == 0
    assert classify_risk_attitude(sure, math.sqrt) == "neutral"
    # 確率 0 の賞金は、確実性等価に効かない
    assert certainty_equivalent_of_lottery(
        {40: Fraction(1), 100: Fraction(0)}, math.sqrt
    ) == pytest.approx(40)


def test_確実性等価は最小の賞金と最大の賞金の間にある() -> None:
    lottery = {9: Fraction(1, 3), 36: Fraction(1, 3), 81: Fraction(1, 3)}
    for utility in (math.sqrt, _linear, _square, math.log):
        value = certainty_equivalent_of_lottery(lottery, utility)
        assert 9 < value < 81
    assert certainty_equivalent_of_lottery(lottery, math.sqrt) == pytest.approx(36)


def test_くじの確率は0以上1以下で合計は1() -> None:
    for bad in [{0: HALF}, {0: HALF, 100: Fraction(3, 2)}]:
        with pytest.raises(ValueError):
            expected_utility_of_lottery(bad, math.sqrt)
        with pytest.raises(ValueError):
            certainty_equivalent_of_lottery(bad, math.sqrt)
        with pytest.raises(ValueError):
            risk_premium_of_lottery(bad, math.sqrt)


def _exponential_utility(x: float) -> float:
    return -math.exp(-0.5 * x)


def test_絶対的危険回避度は2階微分を1階微分で割って符号を変える() -> None:
    # √x の絶対的危険回避度は 1 ÷ (2x)。富が増えるほど小さい
    assert absolute_risk_aversion(math.sqrt, 25) == pytest.approx(0.02, rel=1e-4)
    assert absolute_risk_aversion(math.sqrt, 4) == pytest.approx(0.125, rel=1e-4)
    # −e^(−0.5x) は、どの富でも 0.5（絶対的危険回避度一定）
    for wealth in (1, 3, 0.5):
        assert absolute_risk_aversion(_exponential_utility, wealth) == pytest.approx(
            0.5, rel=1e-4
        )
    assert absolute_risk_aversion(_linear, 10) == pytest.approx(0, abs=1e-6)
    assert absolute_risk_aversion(_square, 10) == pytest.approx(-0.1, rel=1e-4)


def test_相対的危険回避度は富かける絶対的危険回避度() -> None:
    for wealth in (4, 25, 100):
        assert relative_risk_aversion(math.sqrt, wealth) == pytest.approx(0.5, rel=1e-4)
        assert relative_risk_aversion(math.log, wealth) == pytest.approx(1, rel=1e-4)
    assert relative_risk_aversion(_exponential_utility, 3) == pytest.approx(
        1.5, rel=1e-4
    )


def test_小さなリスクの危険プレミアムは2分の1かける危険回避度かける分散() -> None:
    small = {90: HALF, 110: HALF}
    approximation = (
        absolute_risk_aversion(math.sqrt, 100) * float(discrete_variance(small)) / 2
    )
    assert approximation == pytest.approx(0.25, rel=1e-4)
    assert risk_premium_of_lottery(small, math.sqrt) == pytest.approx(
        approximation, rel=0.01
    )


def test_限界効用が0の点では危険回避度は決まらない() -> None:
    with pytest.raises(ValueError):
        absolute_risk_aversion(lambda x: 5.0, 10)
    with pytest.raises(ValueError):
        relative_risk_aversion(lambda x: (x - 10) ** 2, 10)
