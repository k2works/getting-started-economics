"""指数・対数で表した、複利・割引現在価値・収益率。"""

import math
from fractions import Fraction


def _require_growth_factor(rate: float | Fraction) -> None:
    """1 + r が正でなければ、累乗（複利・割引）の意味がない。"""
    if rate <= -1:
        raise ValueError("利子率は −1 より大きくなければなりません（1 + r > 0）")


def compound_amount(principal: float, rate: float, years: float) -> float:
    """複利の元利合計 A = P·(1 + r)^n（浮動小数点で計算する）。"""
    _require_growth_factor(rate)
    factor: float = (1 + rate) ** years
    return principal * factor


def exact_compound_amount(
    principal: Fraction | int, rate: Fraction, years: int
) -> Fraction:
    """複利の元利合計を、分数で厳密に計算する（年数は整数）。"""
    _require_growth_factor(rate)
    return principal * (1 + rate) ** years


def discount_to_present(future: float, rate: float, years: float) -> float:
    """割引現在価値 PV = F ÷ (1 + r)^n。n 年後の F を、今の額に換算する。"""
    _require_growth_factor(rate)
    factor: float = (1 + rate) ** years
    return future / factor


def effective_annual_rate(annual_rate: float, times_per_year: int) -> float:
    """年 m 回の複利の実効年利 (1 + r/m)^m − 1。1 年で、実際に何 % 増えるか。"""
    if times_per_year < 1:
        raise ValueError("複利の回数は、年 1 回以上でなければなりません")
    return compound_amount(1, annual_rate / times_per_year, times_per_year) - 1


def log_base(x: float, base: float) -> float:
    """底を base とする対数 log_base(x)。底の変換で、自然対数の比にする。"""
    if x <= 0:
        raise ValueError("0 や負の数の対数は、ありません")
    if base <= 0 or base == 1:
        raise ValueError("対数の底は、1 でない正の数でなければなりません")
    return math.log(x) / math.log(base)


def _require_positive_rate(rate: float) -> None:
    if rate <= 0:
        raise ValueError("利子率が正でなければ、元本は増えません")


def years_to_multiply(rate: float, multiple: float) -> float:
    """元本が multiple 倍になる年数 n。(1 + r)^n = 倍率 を、対数で解く。"""
    _require_positive_rate(rate)
    return log_base(multiple, 1 + rate)


def rule_of_72_years(rate: float) -> float:
    """72 の法則: 倍になる年数 ≈ 72 ÷ 年利（% の数字）。"""
    _require_positive_rate(rate)
    return 72 / (rate * 100)


def power_in_scientific_notation(base: float, exponent: float) -> tuple[float, int]:
    """base^exponent を、常用対数で 仮数 × 10^指数（1 ≤ 仮数 < 10）に直す。"""
    if base <= 0:
        raise ValueError("0 や負の数の累乗は、常用対数で表せません")
    # 常用対数は math.log10 で直接求める（底の変換 ln x ÷ ln 10 は、誤差が出る）
    digits = exponent * math.log10(base)
    order = math.floor(digits)
    return 10 ** (digits - order), order


def continuous_compound_amount(principal: float, rate: float, years: float) -> float:
    """連続複利の元利合計 A = P·e^(r·t)。"""
    return principal * math.exp(rate * years)


def log_return(start: float, end: float) -> float:
    """対数収益率 ln(終わりの額 ÷ 始めの額)。期間をつなぐと、足し算になる。"""
    if start <= 0 or end <= 0:
        raise ValueError("収益率は、始めと終わりの額が正のときだけ求めます")
    return math.log(end / start)


def annual_growth_rate(start: float, end: float, years: float) -> float:
    """毎年同じ率で増えたとみなした年率 (終わり ÷ 始め)^(1/n) − 1。"""
    if years <= 0:
        raise ValueError("年数は正でなければなりません")
    return math.exp(log_return(start, end) / years) - 1
