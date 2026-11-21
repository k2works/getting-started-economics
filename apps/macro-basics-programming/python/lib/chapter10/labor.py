"""労働市場。

労働需要 Ld = a − b·w（実質賃金 w の減少関数）、労働供給 Ls = c + d·w（増加関数）。
均衡の実質賃金 w* = (a − c) ÷ (b + d)。実質賃金が w* より高いと、供給が需要を上回り、
その差が非自発的失業になる。
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class LaborCurves:
    """労働需要 Ld = demand_intercept − demand_slope·w と、
    労働供給 Ls = supply_intercept + supply_slope·w。"""

    demand_intercept: float
    demand_slope: float
    supply_intercept: float
    supply_slope: float


def _check_curves(curves: LaborCurves) -> None:
    if curves.demand_slope <= 0:
        raise ValueError("労働需要の傾きは、正にする（需要は賃金の減少関数）")
    if curves.supply_slope <= 0:
        raise ValueError("労働供給の傾きは、正にする（供給は賃金の増加関数）")


def _check_wage(wage: float) -> None:
    if wage < 0:
        raise ValueError("実質賃金は、0 以上にする")


def real_wage(nominal_wage: float, price: float) -> float:
    """実質賃金 w = W ÷ P。"""
    if nominal_wage < 0:
        raise ValueError("名目賃金は、0 以上にする")
    if price <= 0:
        raise ValueError("物価は、正にする")
    return nominal_wage / price


def labor_demand(curves: LaborCurves, wage: float) -> float:
    """労働需要 Ld = a − b·w。実質賃金が高いほど、小さい。"""
    _check_curves(curves)
    _check_wage(wage)
    return curves.demand_intercept - curves.demand_slope * wage


def labor_supply(curves: LaborCurves, wage: float) -> float:
    """労働供給 Ls = c + d·w。実質賃金が高いほど、大きい。"""
    _check_curves(curves)
    _check_wage(wage)
    return curves.supply_intercept + curves.supply_slope * wage


def labor_equilibrium(curves: LaborCurves) -> tuple[float, float]:
    """需給が一致する、実質賃金と雇用量 (w*, L*)。"""
    _check_curves(curves)
    wage = (curves.demand_intercept - curves.supply_intercept) / (
        curves.demand_slope + curves.supply_slope
    )
    if wage < 0:
        raise ValueError("均衡の実質賃金が負になる。需要と供給の切片を見直す")
    return wage, labor_demand(curves, wage)


def involuntary_unemployment(curves: LaborCurves, wage: float) -> float:
    """非自発的失業 = 供給 − 需要。賃金が均衡より低いときは、超過需要で、失業は 0。"""
    return max(0.0, labor_supply(curves, wage) - labor_demand(curves, wage))


def effort_level(wage: float, subsistence: float) -> float:
    """努力水準 e(w) = √(w − 生存水準)。生存水準以下の賃金では、努力は 0。"""
    return math.sqrt(max(0.0, wage - subsistence))


def best_efficiency_wage(wages: Sequence[float], subsistence: float) -> float:
    """賃金 1 単位あたりの努力 e(w) ÷ w を、最大にする賃金。"""
    if not wages:
        raise ValueError("賃金の候補が空")
    if any(w <= 0 for w in wages):
        raise ValueError("賃金の候補は、すべて正にする")
    return max(wages, key=lambda w: effort_level(w, subsistence) / w)
