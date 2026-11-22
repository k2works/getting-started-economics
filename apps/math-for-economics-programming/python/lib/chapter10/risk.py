"""期待効用・確実性等価・危険プレミアム。くじ（賭け）を、値 → 確率の分布で表す。"""

import math
from collections.abc import Callable, Mapping
from fractions import Fraction
from typing import Literal

from lib.chapter05.derivative import numerical_derivative
from lib.chapter10.expectation import (
    discrete_expected_value,
    require_probability_distribution,
)

UtilityFunction = Callable[[float], float]


def expected_utility_of_lottery[V: int | Fraction](
    lottery: Mapping[V, Fraction], utility: UtilityFunction
) -> float:
    """期待効用 E[u(X)] = Σ u(x)·P(X = x)。"""
    require_probability_distribution(lottery.values())
    return sum(float(p) * utility(float(x)) for x, p in lottery.items())


def certainty_equivalent_of_lottery[V: int | Fraction](
    lottery: Mapping[V, Fraction], utility: UtilityFunction
) -> float:
    """u(CE) = E[u(X)] となる確実な金額 CE を、2 分法で求める（u は増加関数）。"""
    target = expected_utility_of_lottery(lottery, utility)
    low, high = float(min(lottery)), float(max(lottery))
    for _ in range(100):
        middle = (low + high) / 2
        if utility(middle) < target:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def risk_premium_of_lottery[V: int | Fraction](
    lottery: Mapping[V, Fraction], utility: UtilityFunction
) -> float:
    """危険プレミアム = 期待値 − 確実性等価。リスクを避けるために、あきらめてよい額。"""
    mean = float(discrete_expected_value(lottery))
    return mean - certainty_equivalent_of_lottery(lottery, utility)


def classify_risk_attitude[V: int | Fraction](
    lottery: Mapping[V, Fraction], utility: UtilityFunction
) -> Literal["averse", "neutral", "loving"]:
    """危険プレミアムが正なら危険回避、0 なら危険中立、負なら危険愛好。"""
    premium = risk_premium_of_lottery(lottery, utility)
    if math.isclose(premium, 0, abs_tol=1e-9):
        return "neutral"
    return "averse" if premium > 0 else "loving"


def absolute_risk_aversion(utility: UtilityFunction, wealth: float) -> float:
    """アロー・プラットの絶対的危険回避度 −u''(w) ÷ u'(w)（数値微分を 2 回使う）。"""
    first = numerical_derivative(utility, wealth)
    if math.isclose(first, 0, abs_tol=1e-12):
        raise ValueError("限界効用が 0 の点では、危険回避度は決まりません")
    second = numerical_derivative(
        lambda w: numerical_derivative(utility, w), wealth, step=1e-3
    )
    return -second / first


def relative_risk_aversion(utility: UtilityFunction, wealth: float) -> float:
    """相対的危険回避度 −w·u''(w) ÷ u'(w)。富に対する割合で測ったリスクの嫌い方。"""
    return wealth * absolute_risk_aversion(utility, wealth)
