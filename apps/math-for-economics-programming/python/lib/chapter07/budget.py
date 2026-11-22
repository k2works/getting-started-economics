"""予算制約を、価格ベクトルと数量ベクトルの内積で表す（NumPy を使う）。"""

import math
from collections.abc import Sequence
from typing import Literal

import numpy as np
from numpy.typing import NDArray


def _as_vector(values: Sequence[float]) -> NDArray[np.float64]:
    """リストを、浮動小数点数の NumPy の配列にする。"""
    return np.asarray(values, dtype=np.float64)


def _require_positive_prices(prices: Sequence[float]) -> None:
    """価格は、すべて正でなければならない。"""
    if np.any(_as_vector(prices) <= 0):
        raise ValueError("価格は、すべて正でなければなりません")


def budget_expenditure(prices: Sequence[float], bundle: Sequence[float]) -> float:
    """支出 p·x（価格ベクトルと数量ベクトルの内積）。"""
    return float(np.dot(_as_vector(prices), _as_vector(bundle)))


def budget_status(
    prices: Sequence[float], bundle: Sequence[float], income: float
) -> Literal["inside", "on", "outside"]:
    """財の組合せが、予算線上（p·x = m）・予算内（<）・予算外（>）のどれか。"""
    _require_positive_prices(prices)
    if np.any(_as_vector(bundle) < 0):
        raise ValueError("数量は 0 以上でなければなりません")
    spending = budget_expenditure(prices, bundle)
    # 0.1 + 0.2 = 0.30000000000000004 のような丸め誤差を、予算線上とみなす
    if math.isclose(spending, income):
        return "on"
    return "inside" if spending < income else "outside"


def budget_intercepts(prices: Sequence[float], income: float) -> list[float]:
    """所得をすべて 1 つの財に使ったときの数量 m ÷ pᵢ（予算線と各軸の交点）。"""
    _require_positive_prices(prices)
    return [float(q) for q in income / _as_vector(prices)]


def budget_line_quantity(
    prices: Sequence[float], income: float, first_quantity: float
) -> float:
    """2 財の予算線 p₁x₁ + p₂x₂ = m の上で、財 1 が first_quantity のときの財 2。"""
    if len(prices) != 2:
        raise ValueError("予算線の式は、2 財のときだけ使います")
    _require_positive_prices(prices)
    second_quantity = (income - prices[0] * first_quantity) / prices[1]
    if first_quantity < 0 or second_quantity < 0:
        raise ValueError("予算線上で、数量が負になる点はありません")
    return second_quantity


def full_income(wage: float, total_hours: float, nonlabor_income: float = 0) -> float:
    """すべての時間を働いたときの所得 w·T + 非労働所得（消費と余暇の予算）。"""
    return wage * total_hours + nonlabor_income


def consumption_given_leisure(
    leisure: float, wage: float, total_hours: float, nonlabor_income: float = 0
) -> float:
    """余暇 l のときの消費 c = w·(T − l) + 非労働所得。"""
    if not 0 <= leisure <= total_hours:
        raise ValueError("余暇は、0 時間以上、総時間以下でなければなりません")
    return wage * (total_hours - leisure) + nonlabor_income


def _require_rate(rate: float) -> None:
    """利子率が −100% 以下では、割り引けない。"""
    if rate <= -1:
        raise ValueError("利子率が −100% 以下では、割り引けません")


def second_period_consumption(
    first_consumption: float, income1: float, income2: float, rate: float
) -> float:
    """2 期間の予算で、今期 c₁ 消費したときの来期の消費 (y₁ − c₁)(1 + r) + y₂。"""
    _require_rate(rate)
    second = (income1 - first_consumption) * (1 + rate) + income2
    if second < 0:
        raise ValueError("来期に返せないほど、今期に借りることはできません")
    return second


def lifetime_income_present_value(income1: float, income2: float, rate: float) -> float:
    """2 期間の所得の現在価値 y₁ + y₂ ÷ (1 + r)。"""
    _require_rate(rate)
    return income1 + income2 / (1 + rate)


def security_price(payoffs: Sequence[float], state_prices: Sequence[float]) -> float:
    """証券の価格 = ペイオフのベクトルと状態価格のベクトルの内積。"""
    if np.any(_as_vector(state_prices) < 0):
        raise ValueError("状態価格は 0 以上でなければなりません")
    return float(np.dot(_as_vector(payoffs), _as_vector(state_prices)))
