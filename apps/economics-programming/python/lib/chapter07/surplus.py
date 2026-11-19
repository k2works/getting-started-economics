"""市場均衡・余剰・従量税。

需要曲線 Q = a - bP、供給曲線 Q = c + dP を前提にする。
"""

from dataclasses import dataclass

from lib.chapter01.demand import check_slope, choke_price
from lib.chapter06.bisection import NoEquilibriumError


def check_equilibrium_exists(price: float, quantity: float) -> None:
    """価格が 0 以上、数量が正の均衡があることを確かめる。なければ例外にする。

    第 1 章の「価格も需要量も負にならない」を、均衡にも課す。
    """
    if price < 0:
        raise NoEquilibriumError(
            "均衡価格が負になる。価格が 0 でも供給が需要を上回るので、均衡がない"
        )
    if quantity <= 0:
        raise NoEquilibriumError(
            "均衡数量が 0 以下になる。取引が成立しないので、均衡がない"
        )


def inverse_demand(quantity: float, intercept: float, slope: float) -> float:
    """需要曲線 Q = a - bP を P について解いた、逆需要曲線 P = (a - Q) / b を返す。"""
    check_slope(slope, "需要曲線の傾き")
    if quantity < 0:
        raise ValueError("数量は 0 以上でなければならない")
    return (intercept - quantity) / slope


def equilibrium(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
) -> tuple[float, float]:
    """均衡価格と均衡数量を返す。a - bP = c + dP を P について解く。

    傾きが 0 以下の曲線は受け付けない。価格が負、または数量が 0 以下になる市場には、
    均衡がないので、NoEquilibriumError にする。
    """
    check_slope(demand_slope, "需要曲線の傾き")
    check_slope(supply_slope, "供給曲線の傾き")
    price = (demand_intercept - supply_intercept) / (demand_slope + supply_slope)
    quantity = demand_intercept - demand_slope * price
    check_equilibrium_exists(price, quantity)
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
    highest_price = choke_price(demand_intercept, demand_slope)
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
    a - bP = c + d(P - tax) = (c - d·tax) + dP なので、供給曲線の切片を
    c - d·tax にずらした市場の均衡と同じ。税額が大きく、取引が成立しない
    ときは、NoEquilibriumError にする。
    """
    if tax < 0:
        raise ValueError("税額は 0 以上でなければならない")
    consumer_price, quantity = equilibrium(
        demand_intercept,
        demand_slope,
        supply_intercept - supply_slope * tax,
        supply_slope,
    )
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
