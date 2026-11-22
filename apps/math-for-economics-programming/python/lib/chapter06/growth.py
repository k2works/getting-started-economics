"""指数関数・対数関数の微分と、連続時間の成長率、テイラー展開、e の極限。"""

import math
from collections.abc import Callable

from lib.chapter05.derivative import numerical_derivative


def instantaneous_growth_rate(
    path: Callable[[float], float], t: float, step: float = 1e-5
) -> float:
    """連続時間の成長率 g = d ln y ÷ dt（= y' ÷ y）。ln y(t) を数値微分する。"""
    if path(t) <= 0:
        raise ValueError("量が正の時点でだけ、成長率（ln y の傾き）を求めます")
    return numerical_derivative(lambda s: math.log(path(s)), t, step)


def taylor_exp_approximation(x: float, order: int) -> float:
    """e^x のテイラー展開を order 次まで足す: 1 + x + x²/2! + … + x^n/n!。"""
    if order < 0:
        raise ValueError("次数は、0 以上の整数でなければなりません")
    return sum(x**k / math.factorial(k) for k in range(order + 1))


def exponential_difference_quotient(base: float, step: float) -> float:
    """a^x の x = 0 での差分商 (a^h − 1) ÷ h。h → 0 で ln a に近づく。"""
    if step == 0:
        raise ValueError("刻み h は、0 であってはなりません")
    if base <= 0:
        raise ValueError("指数関数の底は、正でなければなりません")
    growth: float = base**step
    return (growth - 1) / step


def euler_limit_term(n: int) -> float:
    """(1 + 1/n)^n。n を大きくすると、e = 2.71828… に近づく。"""
    if n < 1:
        raise ValueError("n は、1 以上の整数でなければなりません")
    return (1 + 1 / n) ** n
