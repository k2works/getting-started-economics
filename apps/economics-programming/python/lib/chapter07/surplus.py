"""市場均衡・余剰・従量税。

需要曲線 Q = a - bP、供給曲線 Q = c + dP を前提にする。
"""

from dataclasses import dataclass


def equilibrium(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
) -> tuple[float, float]:
    """均衡価格と均衡数量を返す。a - bP = c + dP を P について解く。"""
    price = (demand_intercept - supply_intercept) / (demand_slope + supply_slope)
    quantity = demand_intercept - demand_slope * price
    return price, quantity


def consumer_surplus(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
) -> float:
    """消費者余剰: 需要曲線と均衡価格の間の三角形の面積。"""
    price, quantity = equilibrium(
        demand_intercept, demand_slope, supply_intercept, supply_slope
    )
    highest_price = demand_intercept / demand_slope
    return 0.5 * quantity * (highest_price - price)


def producer_surplus(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
) -> float:
    """生産者余剰: 均衡価格と供給曲線の間の三角形の面積。"""
    if supply_intercept > 0:
        raise ValueError("供給曲線の切片が正の場合は、この関数では求められない")
    price, quantity = equilibrium(
        demand_intercept, demand_slope, supply_intercept, supply_slope
    )
    lowest_price = -supply_intercept / supply_slope
    return 0.5 * quantity * (price - lowest_price)


@dataclass(frozen=True)
class TaxEquilibrium:
    """従量税を課したときの市場均衡。"""

    consumer_price: float
    producer_price: float
    quantity: float
    tax_revenue: float
    deadweight_loss: float


def equilibrium_with_tax(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
    tax: float,
) -> TaxEquilibrium:
    """売り手に 1 単位あたり tax の従量税を課したときの均衡を返す。

    買い手の払う価格を P とすると、売り手の受取は P - tax になる。
    a - bP = c + d(P - tax) を P について解く。
    """
    if tax < 0:
        raise ValueError("税額は 0 以上でなければならない")
    consumer_price = (demand_intercept - supply_intercept + supply_slope * tax) / (
        demand_slope + supply_slope
    )
    quantity = demand_intercept - demand_slope * consumer_price
    _, quantity_without_tax = equilibrium(
        demand_intercept, demand_slope, supply_intercept, supply_slope
    )
    return TaxEquilibrium(
        consumer_price=consumer_price,
        producer_price=consumer_price - tax,
        quantity=quantity,
        tax_revenue=tax * quantity,
        deadweight_loss=0.5 * tax * (quantity_without_tax - quantity),
    )
