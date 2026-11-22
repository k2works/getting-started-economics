"""積分の応用: 需要曲線の下の面積（消費者余剰）と、連続時間の割引現在価値。"""

import math
from collections.abc import Callable

from lib.chapter11.integral import midpoint_rule_integral


def area_under_demand(
    demand: Callable[[float], float],
    low_price: float,
    high_price: float,
    pieces: int = 1000,
) -> float:
    """需要曲線の下、価格 low から high までの面積 ∫ q(p) dp。"""
    if low_price > high_price:
        raise ValueError("下の価格は、上の価格以下でなければなりません")
    return midpoint_rule_integral(demand, low_price, high_price, pieces)


def continuous_present_value(flow: float, rate: float, horizon: float) -> float:
    """毎年 flow の流れを horizon 年受け取る現在価値 ∫₀ᵀ c·e^(−rt) dt。"""
    if horizon < 0:
        raise ValueError("期間は、0 以上でなければなりません")
    if rate == 0:
        return flow * horizon
    return flow * (1 - math.exp(-rate * horizon)) / rate
