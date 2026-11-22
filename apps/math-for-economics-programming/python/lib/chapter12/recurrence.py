"""1 次の漸化式 x(t + 1) = a·x(t) + b の閉じた解と、ふるまいの分類。"""

import math

from lib.chapter04.sequence import affine_fixed_point


def recurrence_closed_form(a: float, b: float, start: float, t: int) -> float:
    """t 期の値 x(t) = a^t·(x(0) − x*) + x*。a = 1 なら、等差数列 x(0) + b·t。"""
    if t < 0:
        raise ValueError("期 t は 0 以上でなければなりません")
    if a == 1:
        return start + b * t
    fixed = affine_fixed_point(a, b)
    return a**t * (start - fixed) + fixed


def classify_linear_recurrence(a: float) -> str:
    """不動点からの差が、毎期 a 倍になることから、ふるまいを分ける。"""
    if a == 1:
        return "arithmetic"
    if a == -1:
        return "two-cycle"
    kind = "converges" if abs(a) < 1 else "diverges"
    return kind + " with oscillation" if a < 0 else kind


def recurrence_half_life(a: float) -> float:
    """不動点からの差が、半分になるまでの期数 n。|a|^n = 1/2 を、対数で解く。"""
    if not 0 < abs(a) < 1:
        raise ValueError("差が半分になるのは、0 < |a| < 1 のときだけです")
    return math.log(2) / -math.log(abs(a))
