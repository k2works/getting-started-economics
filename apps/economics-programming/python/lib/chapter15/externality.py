"""外部不経済とピグー税。

需要曲線 Q = a - bP、私的な供給曲線 Q = c + dP、1 単位あたりの外部費用 e。
社会的限界費用 = 私的限界費用 + 外部費用 なので、社会的な供給曲線は e だけ上にずれる。
"""

from lib.chapter07.surplus import equilibrium


def social_optimum_quantity(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
    external_cost: float,
) -> float:
    """社会的に最適な数量。(a - Q) ÷ b = (Q - c) ÷ d + e を Q について解く。

    社会的な供給曲線は、私的な供給曲線を e だけ上にずらしたもの。
    Q = c + d(P - e) = (c - d·e) + dP なので、第 7 章の従量税（税額 e）と同じ形で、
    供給曲線の切片を c - d·e にずらした市場の均衡数量になる。
    外部費用が大きく、最適な数量が 0 以下になるときは、NoEquilibriumError にする。
    """
    if external_cost < 0:
        raise ValueError("外部費用は 0 以上でなければならない")
    _, quantity = equilibrium(
        demand_intercept,
        demand_slope,
        supply_intercept - supply_slope * external_cost,
        supply_slope,
    )
    return quantity


def externality_deadweight_loss(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
    external_cost: float,
) -> float:
    """放任したときに、外部費用のために失われる余剰（死荷重）。"""
    _, market_quantity = equilibrium(
        demand_intercept, demand_slope, supply_intercept, supply_slope
    )
    optimum = social_optimum_quantity(
        demand_intercept, demand_slope, supply_intercept, supply_slope, external_cost
    )
    return 0.5 * external_cost * (market_quantity - optimum)
