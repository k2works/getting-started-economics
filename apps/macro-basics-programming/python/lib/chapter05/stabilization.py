"""ギャップと安定化政策: ギャップ・必要な政策の大きさ・ビルトイン・スタビライザー。"""

import math

from lib.chapter04.multiplier import (
    spending_multiplier,
    tax_multiplier,
    validate_mpc,
)


def output_gap(full_employment_income: float, equilibrium_income: float) -> float:
    """ギャップ = 完全雇用所得 − 均衡所得。正がデフレギャップ、負がインフレギャップ。"""
    return full_employment_income - equilibrium_income


def classify_gap(gap: float) -> str:
    """ギャップの符号から、デフレギャップ・インフレギャップ・ギャップなしを返す。"""
    if math.isclose(gap, 0, abs_tol=1e-9):
        return "ギャップなし"
    return "デフレギャップ" if gap > 0 else "インフレギャップ"


def required_spending_change(gap: float, mpc: float) -> float:
    """ギャップを埋めるのに必要な政府支出の変化 = ギャップ ÷ 政府支出乗数。"""
    return gap / spending_multiplier(mpc)


def required_tax_change(gap: float, mpc: float) -> float:
    """ギャップを埋めるのに必要な租税の変化 = ギャップ ÷ 租税乗数。負なら減税。"""
    return gap / tax_multiplier(mpc)


def stabilizer_multiplier(mpc: float, tax_rate: float) -> float:
    """比例税（税率 t）のある乗数 1 ÷ (1 − c(1 − t))。"""
    validate_mpc(mpc)
    if not 0 <= tax_rate < 1:
        raise ValueError("税率は、0 以上 1 未満にする")
    return 1 / (1 - mpc * (1 - tax_rate))


def income_swing(mpc: float, tax_rate: float, shock: float) -> float:
    """独立支出が shock だけ変動したときの、均衡所得の変動。"""
    return stabilizer_multiplier(mpc, tax_rate) * shock


def swing_reduction(mpc: float, tax_rate: float) -> float:
    """比例税がないときと比べた、所得の振れ幅の縮小の割合（0〜1）。"""
    with_tax = stabilizer_multiplier(mpc, tax_rate)
    return 1 - with_tax / stabilizer_multiplier(mpc, 0)
