"""貨幣需要の分解・シフト・流動性のわな（中核は money_market.py）。"""

import math

from lib.chapter07.money_market import (
    lm_income,
    lm_interest,
    money_demand,
    validate_h,
    validate_k,
)

# 浮動小数点の誤差（下限が 0 のとき、0.1 + 0.2 − 0.3 は 5.6e-17 になる）を許す
_TOLERANCE = 1e-9


def transaction_demand(income: float, k: float) -> float:
    """取引需要 k·Y。所得の増加関数。"""
    validate_k(k)
    return k * income


def asset_demand(interest: float, h: float) -> float:
    """資産需要 −h·r。利子率の減少関数（定数項は、シフトに含めて考えない）。"""
    validate_h(h)
    return -h * interest


def money_demand_shift(income_before: float, income_after: float, k: float) -> float:
    """所得の変化による、貨幣需要曲線の右へのシフト幅 k·ΔY（利子率を縦軸にとる）。"""
    validate_k(k)
    return k * (income_after - income_before)


def lm_shift(real_money_before: float, real_money_after: float, k: float) -> float:
    """実質貨幣供給の変化による、LM 曲線の右へのシフト幅 Δ(M/P) ÷ k。"""
    validate_k(k)
    return (real_money_after - real_money_before) / k


def lm_interest_with_trap(
    income: float, real_money: float, k: float, h: float, floor: float
) -> float:
    """流動性のわなのある LM 曲線。利子率は、下限 floor を下回らない（水平になる）。"""
    return max(lm_interest(income, real_money, k, h), floor)


def trap_income(real_money: float, k: float, h: float, floor: float) -> float:
    """LM 曲線が、下限 floor で水平になる、所得の上限。"""
    return lm_income(floor, real_money, k, h)


def money_demand_with_trap(
    income: float, interest: float, k: float, h: float, floor: float
) -> float:
    """流動性のわなのある貨幣需要。利子率が下限なら、貨幣需要は無限大。"""
    if math.isclose(interest, floor, abs_tol=_TOLERANCE):
        return math.inf
    if interest < floor:
        raise ValueError("利子率は、下限を下回らない")
    return money_demand(income, interest, k, h)


def excess_money_demand(
    income: float, interest: float, real_money: float, k: float, h: float
) -> float:
    """貨幣の超過需要 L − M/P。正なら需要超過、負なら供給超過。"""
    return money_demand(income, interest, k, h) - real_money


def money_market_state(
    income: float, interest: float, real_money: float, k: float, h: float
) -> str:
    """点 (Y, r) が、LM 曲線の上側・下側・上のどれかを判定する。"""
    excess = excess_money_demand(income, interest, real_money, k, h)
    if math.isclose(excess, 0, abs_tol=1e-9):
        return "均衡"
    if excess < 0:
        return "供給超過（利子率が下がる）"
    return "需要超過（利子率が上がる）"
