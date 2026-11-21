"""財政政策と金融政策の効果。

IS: (1 − c)Y + b·r = A、LM: k·Y − h·r = M/P を、r を消して解くと、
Y = (A + (b ÷ h)·M/P) ÷ [(1 − c) + b·k ÷ h]。
分母の b·k ÷ h が、クラウディングアウトの強さ。
h = math.inf（流動性のわな）も、閉じた式なら、扱える。
"""

from collections.abc import Sequence
from dataclasses import dataclass

from lib.chapter04.multiplier import spending_multiplier, validate_mpc
from lib.chapter07.money_market import validate_h, validate_k
from lib.chapter08.is_lm import solve_is_lm, validate_b


def _denominator(mpc: float, b: float, k: float, h: float) -> float:
    """分母 (1 − c) + b·k ÷ h。h = math.inf なら、第 2 項は 0。"""
    validate_mpc(mpc)
    validate_b(b)
    validate_k(k)
    validate_h(h)
    return (1 - mpc) + b * k / h


def fiscal_effect(
    mpc: float, b: float, k: float, h: float, delta_government: float
) -> float:
    """財政政策の効果 ΔY = ΔG ÷ [(1 − c) + b·k ÷ h]。単純な乗数より小さい。"""
    return delta_government / _denominator(mpc, b, k, h)


def monetary_effect(
    mpc: float, b: float, k: float, h: float, delta_real_money: float
) -> float:
    """金融政策の効果 ΔY = (b ÷ h)·Δ(M/P) ÷ [(1 − c) + b·k ÷ h]。"""
    return (b / h) * delta_real_money / _denominator(mpc, b, k, h)


def crowding_out(
    mpc: float, b: float, k: float, h: float, delta_government: float
) -> float:
    """クラウディングアウト = 単純な乗数による増加 − 実際の増加。"""
    simple = spending_multiplier(mpc) * delta_government
    return simple - fiscal_effect(mpc, b, k, h, delta_government)


def fiscal_effect_solved(
    mpc: float,
    b: float,
    intercept: float,
    k: float,
    h: float,
    real_money: float,
    delta_government: float,
) -> float:
    """財政政策の効果を、前後の均衡を連立方程式で解いて求める（有限の h だけ）。"""
    before, _ = solve_is_lm(mpc, b, intercept, k, h, real_money)
    after, _ = solve_is_lm(mpc, b, intercept + delta_government, k, h, real_money)
    return after - before


def monetary_effect_solved(
    mpc: float,
    b: float,
    intercept: float,
    k: float,
    h: float,
    real_money: float,
    delta_real_money: float,
) -> float:
    """金融政策の効果を、前後の均衡を連立方程式で解いて求める（有限の h だけ）。"""
    before, _ = solve_is_lm(mpc, b, intercept, k, h, real_money)
    after, _ = solve_is_lm(mpc, b, intercept, k, h, real_money + delta_real_money)
    return after - before


def policy_interest_change(
    k: float, h: float, delta_income: float, delta_real_money: float = 0
) -> float:
    """政策後の利子率の変化 Δr = (k·ΔY − Δ(M/P)) ÷ h（LM 曲線上の動き）。"""
    validate_k(k)
    validate_h(h)
    return (k * delta_income - delta_real_money) / h


@dataclass(frozen=True)
class PolicyRow:
    """条件 (h, b) ごとの、財政政策・金融政策の効果。"""

    h: float
    b: float
    fiscal: float
    monetary: float
    crowding_out: float


def policy_effectiveness(
    mpc: float,
    k: float,
    conditions: Sequence[tuple[float, float]],
    delta_government: float,
    delta_real_money: float,
) -> list[PolicyRow]:
    """条件 (h, b) を変えて、2 つの政策の効果を表にまとめる。"""
    return [
        PolicyRow(
            h,
            b,
            fiscal_effect(mpc, b, k, h, delta_government),
            monetary_effect(mpc, b, k, h, delta_real_money),
            crowding_out(mpc, b, k, h, delta_government),
        )
        for h, b in conditions
    ]
