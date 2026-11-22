import math

import pytest

from lib.chapter03.interest import effective_annual_rate, log_return
from lib.chapter05.derivative import numerical_derivative
from lib.chapter06.growth import (
    euler_limit_term,
    exponential_difference_quotient,
    instantaneous_growth_rate,
    taylor_exp_approximation,
)


@pytest.mark.parametrize("x", [-1, 0, 0.5, 2])
def test_指数関数の導関数は自分自身(x: float) -> None:
    assert numerical_derivative(math.exp, x) == pytest.approx(math.exp(x))


@pytest.mark.parametrize("x", [0.5, 1, 4])
def test_対数関数の導関数は1分のx(x: float) -> None:
    assert numerical_derivative(math.log, x) == pytest.approx(1 / x)


def test_テイラー展開は1たすxたすxの2乗の2分の1と続く() -> None:
    assert taylor_exp_approximation(0.1, 0) == 1
    assert taylor_exp_approximation(0.1, 1) == pytest.approx(1.1)
    assert taylor_exp_approximation(0.1, 2) == pytest.approx(1.105)
    assert taylor_exp_approximation(0.1, 3) == pytest.approx(1.1051666667)
    assert taylor_exp_approximation(-0.5, 2) == pytest.approx(0.625)  # 1 − 0.5 + 0.125
    assert taylor_exp_approximation(2, 3) == pytest.approx(19 / 3)  # 1 + 2 + 2 + 4/3


@pytest.mark.parametrize("x", [-0.5, 0.1, 1])
def test_テイラー展開は次数を上げるほどeのx乗に近づく(x: float) -> None:
    errors = [abs(taylor_exp_approximation(x, n) - math.exp(x)) for n in range(8)]
    assert errors == sorted(errors, reverse=True)
    # n 次で打ち切った誤差は、次の項 |x|^(n+1) ÷ (n+1)! と同じくらい
    for n in [1, 2, 3]:
        next_term = abs(x) ** (n + 1) / math.factorial(n + 1)
        assert next_term / 2 < errors[n] < next_term * 2


def test_テイラー展開の次数は0以上() -> None:
    with pytest.raises(ValueError, match="次数"):
        taylor_exp_approximation(0.1, -1)


def test_指数的に増える量の瞬間の成長率は指数の係数() -> None:
    for t in [0, 5, 20]:
        rate = instantaneous_growth_rate(lambda s: 100 * math.exp(0.03 * s), t)
        assert rate == pytest.approx(0.03)
        decline = instantaneous_growth_rate(lambda s: 50 * math.exp(-0.02 * s), t)
        assert decline == pytest.approx(-0.02)


def test_年率10パーセントで増える量の連続の成長率はln1点1() -> None:
    rate = instantaneous_growth_rate(lambda t: 100 * 1.1**t, 3)
    assert rate == pytest.approx(math.log(1.1))  # 0.0953… < 0.1
    assert rate == pytest.approx(log_return(100, 110))  # 第 3 章の対数収益率


def test_積の成長率は成長率の和で商の成長率は差() -> None:
    def real(t: float) -> float:
        return 500 * math.exp(0.02 * t)

    def prices(t: float) -> float:
        return 1.2 * math.exp(0.01 * t)

    nominal = instantaneous_growth_rate(lambda t: real(t) * prices(t), 4)
    assert nominal == pytest.approx(0.03)
    deflated = instantaneous_growth_rate(lambda t: real(t) / prices(t), 4)
    assert deflated == pytest.approx(0.01)


def test_成長率は量が正の時点でだけ求める() -> None:
    with pytest.raises(ValueError, match="正"):
        instantaneous_growth_rate(lambda t: t - 1, 1)
    with pytest.raises(ValueError, match="正"):
        instantaneous_growth_rate(lambda t: -5.0, 0)
    small = instantaneous_growth_rate(lambda t: 0.5 * math.exp(0.03 * t), 0)
    assert small == pytest.approx(0.03)  # 0 < y < 1 でも、正なら求める


def test_底がaの指数関数の差分商はlnaに近づく() -> None:
    assert exponential_difference_quotient(2, 1) == 1  # (2 − 1) ÷ 1
    for base in [math.e, 2, 0.5, 10]:
        quotient = exponential_difference_quotient(base, 1e-6)
        assert quotient == pytest.approx(math.log(base), abs=1e-5)
    # 刻みを負にしても、同じ値に近づく
    assert exponential_difference_quotient(2, -1e-6) == pytest.approx(math.log(2))


def test_差分商は刻みが0でなく底が正のときだけ() -> None:
    with pytest.raises(ValueError, match="刻み"):
        exponential_difference_quotient(2, 0)
    with pytest.raises(ValueError, match="底"):
        exponential_difference_quotient(0, 0.1)


def test_1たす1分のnのn乗は増えながらeに近づく() -> None:
    assert euler_limit_term(1) == 2
    assert euler_limit_term(2) == 2.25
    terms = [euler_limit_term(n) for n in [1, 2, 10, 100, 1000]]
    assert terms == sorted(terms)
    assert all(term < math.e for term in terms)
    assert euler_limit_term(10**6) == pytest.approx(math.e, abs=2e-6)
    # 第 3 章の実効年利: 年利 100% を年 n 回の複利にすると、1 年で (1 + 1/n)^n 倍
    assert euler_limit_term(12) == pytest.approx(1 + effective_annual_rate(1, 12))


def test_eの極限の項はnが1以上() -> None:
    with pytest.raises(ValueError, match="n"):
        euler_limit_term(0)
