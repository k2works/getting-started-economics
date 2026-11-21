"""貨幣数量説（マネタリズム）: 交換方程式 MV = PY とマーシャルの k。"""

from lib.chapter01.validation import validate_positive


def price_level_from_quantity(money: float, velocity: float, output: float) -> float:
    """交換方程式 MV = PY から、物価水準 P = MV ÷ Y。"""
    if output == 0:
        raise ValueError("生産量が 0 のとき、物価水準は計算できない")
    return money * velocity / output


def marshall_k(velocity: float) -> float:
    """マーシャルの k = 1 ÷ V。貨幣需要は、名目所得の k 倍。"""
    validate_positive(velocity, "流通速度は、正にする")
    return 1 / velocity


def nominal_money_demand(k: float, price_level: float, output: float) -> float:
    """貨幣需要 M = k·P·Y。名目所得で決まり、利子率には依存しない。"""
    return k * price_level * output


def inflation_from_money_growth(
    money_growth: float, real_growth: float, velocity_change: float
) -> float:
    """変化率の近似 π ≈ μ + Δv − g（すべて % の値）。"""
    return money_growth + velocity_change - real_growth
