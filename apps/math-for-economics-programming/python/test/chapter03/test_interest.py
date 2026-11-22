import math
from fractions import Fraction

import pytest

from lib.chapter03.interest import (
    annual_growth_rate,
    compound_amount,
    continuous_compound_amount,
    discount_to_present,
    effective_annual_rate,
    exact_compound_amount,
    log_base,
    log_return,
    power_in_scientific_notation,
    rule_of_72_years,
    years_to_multiply,
)


def test_複利は利子にも利子がつく() -> None:
    assert compound_amount(100, 0.1, 1) == pytest.approx(110)
    assert compound_amount(100, 0.1, 2) == pytest.approx(121)
    assert compound_amount(200, 0.1, 3) == pytest.approx(266.2)
    assert compound_amount(100, 0.05, 10) == pytest.approx(162.889462677744)


def test_分数で計算すると複利はちょうどの値になる() -> None:
    assert exact_compound_amount(100, Fraction(1, 10), 2) == 121
    assert compound_amount(100, 0.1, 2) != 121
    exact = exact_compound_amount(100, Fraction(5, 100), 10)
    assert exact == Fraction("162.889462677744140625")


EXPONENT_PAIRS = [(3, 7), (0.5, 2), (2, -1), (0, 4)]


@pytest.mark.parametrize(("x", "y"), EXPONENT_PAIRS)
def test_x年運用してからy年運用するとx足すy年の運用と同じ(x: float, y: float) -> None:
    # 指数法則 a^x · a^y = a^(x+y)
    after_x = compound_amount(100, 0.05, x)
    assert compound_amount(after_x, 0.05, y) == pytest.approx(
        compound_amount(100, 0.05, x + y)
    )


@pytest.mark.parametrize(("x", "y"), EXPONENT_PAIRS)
def test_累乗の累乗は指数の掛け算(x: float, y: float) -> None:
    # 指数法則 (a^x)^y = a^(x·y)。1 + r = a^x となる利子率で y 年運用する
    rate = compound_amount(1, 0.05, x) - 1
    assert compound_amount(1, rate, y) == pytest.approx(compound_amount(1, 0.05, x * y))


def test_割引現在価値は複利の逆向き() -> None:
    assert discount_to_present(1000, 0.05, 3) == pytest.approx(863.837598531476)
    for future, rate, years in [(1000, 0.05, 3), (500, 0.2, 4), (80, 0.03, 0.5)]:
        present = discount_to_present(future, rate, years)
        assert compound_amount(present, rate, years) == pytest.approx(future)


@pytest.mark.parametrize("rate", [-1, -1.5])
def test_利子率がマイナス1以下では複利も割引もできない(rate: float) -> None:
    with pytest.raises(ValueError):
        compound_amount(100, rate, 2)
    with pytest.raises(ValueError):
        discount_to_present(100, rate, 2)
    with pytest.raises(ValueError):
        exact_compound_amount(100, Fraction(rate), 2)


def test_年m回の複利の実効年利() -> None:
    assert effective_annual_rate(0.05, 1) == pytest.approx(0.05)
    assert effective_annual_rate(0.1, 2) == pytest.approx(0.1025)
    assert effective_annual_rate(0.12, 4) == pytest.approx(0.12550881)
    assert effective_annual_rate(0.05, 12) == pytest.approx(0.0511618978817)


def test_複利の回数が増えると実効年利は増える() -> None:
    rates = [effective_annual_rate(0.05, m) for m in (1, 2, 4, 12, 365)]
    assert all(a < b for a, b in zip(rates, rates[1:], strict=False))


@pytest.mark.parametrize("times", [0, -1])
def test_複利の回数が1未満ならエラー(times: int) -> None:
    with pytest.raises(ValueError):
        effective_annual_rate(0.05, times)


def test_底を変えた対数() -> None:
    assert log_base(8, 2) == pytest.approx(3)
    assert log_base(0.25, 2) == pytest.approx(-2)
    assert log_base(9, 1 / 3) == pytest.approx(-2)
    for x, base in [(8, 2), (0.3, 10), (50, 1.05)]:
        assert log_base(x, base) == pytest.approx(math.log(x) / math.log(base))
        assert log_base(x, base) == pytest.approx(log_base(x, 7) / log_base(base, 7))


@pytest.mark.parametrize(("x", "base"), [(0, 10), (-1, 10), (5, 1), (5, 0), (5, -2)])
def test_0や負の数の対数と1や正でない底の対数はない(x: float, base: float) -> None:
    with pytest.raises(ValueError):
        log_base(x, base)


def test_倍になる年数だけ運用するとちょうど倍になる() -> None:
    assert years_to_multiply(0.05, 2) == pytest.approx(14.2066990829)
    for rate, multiple in [(0.05, 2), (0.08, 3), (0.3, 10), (0.01, 1.5)]:
        years = years_to_multiply(rate, multiple)
        assert compound_amount(100, rate, years) == pytest.approx(100 * multiple)


def test_72の法則の誤差は年利8パーセントの近くで小さく離れると大きい() -> None:
    assert rule_of_72_years(0.05) == pytest.approx(14.4)

    def error(rate: float) -> float:
        return abs(rule_of_72_years(rate) - years_to_multiply(rate, 2))

    assert error(0.08) < 0.01
    assert error(0.01) > 2
    assert error(0.3) > 0.2


@pytest.mark.parametrize("rate", [0, -0.05])
def test_利子率が正でなければ倍にならない(rate: float) -> None:
    with pytest.raises(ValueError):
        years_to_multiply(rate, 2)
    with pytest.raises(ValueError):
        rule_of_72_years(rate)


LOG_PAIRS = [(2, 5), (0.5, 8), (0.1, 0.3), (1.05, 1.05), (1, 3)]


@pytest.mark.parametrize(("x", "y"), LOG_PAIRS)
def test_積の対数は対数の和で商の対数は対数の差(x: float, y: float) -> None:
    assert log_base(x * y, 10) == pytest.approx(log_base(x, 10) + log_base(y, 10))
    assert log_base(x / y, 10) == pytest.approx(log_base(x, 10) - log_base(y, 10))


@pytest.mark.parametrize(("x", "k"), [(2, 10), (0.5, 3), (1.05, 0.5), (3, -2)])
def test_累乗の対数は指数を前に出す(x: float, k: float) -> None:
    assert log_base(x**k, 10) == pytest.approx(k * log_base(x, 10))


def test_常用対数で累乗を指数表記にする() -> None:
    assert power_in_scientific_notation(2, 10) == (pytest.approx(1.024), 3)
    assert power_in_scientific_notation(2, 100) == (pytest.approx(1.2676506), 30)
    assert power_in_scientific_notation(1.05, 100) == (pytest.approx(1.31501258), 2)


@pytest.mark.parametrize(("base", "power"), [(2, 64), (3, 40), (7, 15), (12, 9)])
def test_指数表記の桁数は整数の累乗の桁数と一致する(base: int, power: int) -> None:
    mantissa, exponent = power_in_scientific_notation(base, power)
    assert 1 <= mantissa < 10
    assert exponent + 1 == len(str(base**power))
    assert mantissa * 10**exponent == pytest.approx(base**power)


def test_底の変換の誤差で10の累乗の桁を取り違えない() -> None:
    assert power_in_scientific_notation(1000, 1) == (1, 3)
    assert power_in_scientific_notation(100, 3) == (1, 6)


def test_連続複利と連続複利の実効年利() -> None:
    assert continuous_compound_amount(100, 0.05, 10) == pytest.approx(164.872127070)
    assert continuous_compound_amount(1, 0.05, 1) - 1 == pytest.approx(0.0512710964)


def test_複利の回数を増やすと連続複利に近づく() -> None:
    limit = continuous_compound_amount(1, 0.05, 1) - 1
    gaps = [limit - effective_annual_rate(0.05, m) for m in (1, 12, 365, 10_000)]
    assert all(a > b > 0 for a, b in zip(gaps, gaps[1:], strict=False))
    assert gaps[-1] < 1e-6


def test_年率で毎年増やすと最後の額になる() -> None:
    assert annual_growth_rate(100, 121, 2) == pytest.approx(0.1)
    for start, end, years in [(100, 121, 2), (80, 50, 3), (10, 30, 0.5)]:
        rate = annual_growth_rate(start, end, years)
        assert compound_amount(start, rate, years) == pytest.approx(end)


def test_対数収益率() -> None:
    assert log_return(100, 121) == pytest.approx(math.log(1.21))
    assert log_return(100, 121) == pytest.approx(2 * math.log(1.1))
    assert log_return(121, 100) == pytest.approx(-log_return(100, 121))


def test_対数収益率は期間をつなぐと足し算になる() -> None:
    path = [100, 110, 121, 90, 135]
    steps = [log_return(a, b) for a, b in zip(path, path[1:], strict=False)]
    assert sum(steps) == pytest.approx(log_return(path[0], path[-1]))


@pytest.mark.parametrize(("start", "end"), [(0, 100), (100, 0), (-100, 50)])
def test_0や負の額からは収益率を求めない(start: float, end: float) -> None:
    with pytest.raises(ValueError):
        log_return(start, end)
    with pytest.raises(ValueError):
        annual_growth_rate(start, end, 2)


@pytest.mark.parametrize("years", [0, -1])
def test_年数が正でなければ年率を求めない(years: float) -> None:
    with pytest.raises(ValueError):
        annual_growth_rate(100, 121, years)


@pytest.mark.parametrize("base", [0, -2])
def test_0や負の数の累乗は常用対数で表せない(base: float) -> None:
    with pytest.raises(ValueError):
        power_in_scientific_notation(base, 3)


def test_0年か利子率0なら元の額のまま() -> None:
    assert compound_amount(100, 0.05, 0) == 100
    assert discount_to_present(100, 0.05, 0) == 100
    assert exact_compound_amount(100, Fraction(1, 20), 0) == 100
    assert compound_amount(100, 0, 30) == 100
    assert discount_to_present(100, 0, 30) == 100
    assert continuous_compound_amount(100, 0, 30) == 100


def test_利子率が負なら減っていき半年なら平方根の倍率() -> None:
    assert compound_amount(100, -0.5, 2) == pytest.approx(25)
    assert exact_compound_amount(Fraction(1, 2), Fraction(-1, 4), 2) == Fraction(9, 32)
    assert discount_to_present(25, -0.5, 2) == pytest.approx(100)
    assert continuous_compound_amount(100, -0.05, 10) == pytest.approx(60.6530659713)
    assert compound_amount(100, 0.21, 0.5) == pytest.approx(110)


def test_倍率1なら0年で1未満なら負の年数で0なら求まらない() -> None:
    assert log_base(1, 10) == 0
    assert log_base(1, 0.5) == 0
    assert years_to_multiply(0.05, 1) == 0
    assert years_to_multiply(0.05, 0.5) == pytest.approx(-14.2066990829)
    with pytest.raises(ValueError):
        years_to_multiply(0.05, 0)


def test_1未満の数や10の累乗も指数表記にする() -> None:
    assert power_in_scientific_notation(0.5, 3) == (pytest.approx(1.25), -1)
    assert power_in_scientific_notation(10, 3) == (1, 3)
    assert power_in_scientific_notation(1, 5) == (1, 0)
    assert power_in_scientific_notation(7, 0) == (1, 0)


def test_1未満の額や変わらない額や減った額の収益率() -> None:
    assert log_return(0.5, 1) == pytest.approx(math.log(2))
    assert log_return(2, 1) == pytest.approx(-math.log(2))
    assert log_return(1, 0.25) == pytest.approx(-2 * math.log(2))
    assert annual_growth_rate(0.25, 1, 2) == pytest.approx(1)
    assert log_return(100, 100) == 0
    assert annual_growth_rate(100, 100, 5) == 0
    assert annual_growth_rate(100, 81, 2) == pytest.approx(-0.1)
