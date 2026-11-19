"""独占。需要曲線 Q = a - bP、限界費用 MC は一定とする。"""

from dataclasses import dataclass

from lib.chapter01.demand import check_slope, choke_price
from lib.chapter07.surplus import inverse_demand


def _check_cost(demand_intercept: float, demand_slope: float, cost: float) -> None:
    if cost < 0:
        raise ValueError("限界費用は 0 以上でなければならない")
    if cost >= choke_price(demand_intercept, demand_slope):
        raise ValueError("限界費用が需要曲線の切片以上なので、生産しない")


def marginal_revenue(
    quantity: float, demand_intercept: float, demand_slope: float
) -> float:
    """限界収入 MR = (a - 2Q) ÷ b。逆需要曲線 P = (a - Q) ÷ b の 2 倍の傾き。"""
    check_slope(demand_slope, "需要曲線の傾き")
    return (demand_intercept - 2 * quantity) / demand_slope


def competitive_quantity(
    demand_intercept: float, demand_slope: float, marginal_cost: float
) -> float:
    """完全競争の数量: 価格が限界費用に等しくなる点の需要量。"""
    _check_cost(demand_intercept, demand_slope, marginal_cost)
    return demand_intercept - demand_slope * marginal_cost


@dataclass(frozen=True)
class MonopolyOutcome:
    """独占の結果。"""

    quantity: float
    price: float
    profit: float
    consumer_surplus: float
    deadweight_loss: float


def monopoly_outcome(
    demand_intercept: float, demand_slope: float, marginal_cost: float
) -> MonopolyOutcome:
    """MR = MC で数量を決め、価格は需要曲線の上で決まる。"""
    competitive = competitive_quantity(demand_intercept, demand_slope, marginal_cost)
    quantity = (demand_intercept - demand_slope * marginal_cost) / 2
    price = inverse_demand(quantity, demand_intercept, demand_slope)
    highest_price = choke_price(demand_intercept, demand_slope)
    return MonopolyOutcome(
        quantity=quantity,
        price=price,
        profit=(price - marginal_cost) * quantity,
        consumer_surplus=0.5 * quantity * (highest_price - price),
        deadweight_loss=0.5 * (competitive - quantity) * (price - marginal_cost),
    )


def lerner_index(price: float, marginal_cost: float) -> float:
    """ラーナー指数 (P - MC) ÷ P。独占力の大きさで、独占では弾力性の逆数に等しい。"""
    if price <= 0:
        raise ValueError("価格は正でなければならない")
    return (price - marginal_cost) / price
