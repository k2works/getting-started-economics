"""IS 曲線と IS-LM の均衡。

財市場: Y = C + I + G、C = c(Y − T) + C0、I = I0 − b·r から、
IS 曲線 (1 − c)Y + b·r = A（A = C0 − c·T + I0 + G）が得られる。
"""

import math

import numpy as np

from lib.chapter04.multiplier import validate_mpc
from lib.chapter07.money_market import money_demand, validate_h, validate_k


def validate_b(b: float) -> None:
    """投資の利子感応度 b が、0 以上であることを確かめる。"""
    if b < 0:
        raise ValueError("投資の利子感応度 b は、0 以上にする")


def _check_b_positive(b: float) -> None:
    if b <= 0:
        raise ValueError(
            "投資の利子感応度 b が 0 の IS 曲線は垂直で、利子率が決まらない"
        )


def investment_demand(interest: float, autonomous_investment: float, b: float) -> float:
    """投資関数 I = I0 − b·r。利子率の減少関数。"""
    validate_b(b)
    return autonomous_investment - b * interest


def is_intercept(
    mpc: float,
    autonomous_consumption: float,
    autonomous_investment: float,
    government: float,
    tax: float = 0,
) -> float:
    """IS 曲線の右辺 A = C0 − c·T + I0 + G（利子率に依存しない支出）。"""
    return autonomous_consumption - mpc * tax + autonomous_investment + government


def is_income(interest: float, intercept: float, mpc: float, b: float) -> float:
    """IS 曲線: 財市場を均衡させる所得 Y = (A − b·r) ÷ (1 − c)。"""
    validate_mpc(mpc)
    validate_b(b)
    return (intercept - b * interest) / (1 - mpc)


def is_interest(income: float, intercept: float, mpc: float, b: float) -> float:
    """IS 曲線: 財市場を均衡させる利子率 r = (A − (1 − c)Y) ÷ b。"""
    validate_mpc(mpc)
    _check_b_positive(b)
    return (intercept - (1 - mpc) * income) / b


def is_slope(mpc: float, b: float) -> float:
    """IS 曲線の傾き dr/dY = −(1 − c) ÷ b（所得を横軸、利子率を縦軸にしたとき）。"""
    validate_mpc(mpc)
    _check_b_positive(b)
    return -(1 - mpc) / b


def is_shift_for_government(mpc: float, delta_government: float) -> float:
    """政府支出が ΔG 増えたときの、IS 曲線の右シフト幅 ΔG ÷ (1 − c)。"""
    validate_mpc(mpc)
    return delta_government / (1 - mpc)


def goods_market_state(
    income: float, interest: float, intercept: float, mpc: float, b: float
) -> str:
    """点 (Y, r) での財市場。IS の右上は供給超過、左下は需要超過。"""
    validate_mpc(mpc)
    validate_b(b)
    excess_supply = (1 - mpc) * income + b * interest - intercept
    if math.isclose(excess_supply, 0, abs_tol=1e-9):
        return "均衡"
    return "供給超過" if excess_supply > 0 else "需要超過"


def _check_lm_finite(k: float, h: float) -> None:
    validate_k(k)
    validate_h(h)
    if not math.isfinite(h):
        raise ValueError("連立方程式のソルバーは、有限の h だけ扱える")


def solve_is_lm(
    mpc: float,
    b: float,
    intercept: float,
    k: float,
    h: float,
    real_money: float,
) -> tuple[float, float]:
    """IS と LM の連立方程式を解いて、均衡の所得と利子率 (Y, r) を返す。

    (1 − c)Y + b·r = A
    k·Y − h·r = M/P
    """
    validate_mpc(mpc)
    validate_b(b)
    _check_lm_finite(k, h)
    coefficients = np.array([[1 - mpc, b], [k, -h]])
    constants = np.array([intercept, real_money])
    income, interest = np.linalg.solve(coefficients, constants)
    return float(income), float(interest)


def is_lm_residuals(
    income: float,
    interest: float,
    mpc: float,
    b: float,
    intercept: float,
    k: float,
    h: float,
    real_money: float,
) -> tuple[float, float]:
    """点 (Y, r) が IS の式と LM の式を満たさない量。均衡では、どちらも 0。"""
    validate_mpc(mpc)
    validate_b(b)
    is_residual = (1 - mpc) * income + b * interest - intercept
    lm_residual = money_demand(income, interest, k, h) - real_money
    return is_residual, lm_residual
