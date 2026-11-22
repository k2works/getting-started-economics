"""逆需要 P = a − b·Q と一定の単位費用 c のもとでの、独占・完全競争・クールノー競争。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketOutcome:
    """市場全体の数量・価格・利潤（企業が複数なら、全企業の合計）。"""

    quantity: float
    price: float
    profit: float


def _validate_market(a: float, b: float, cost: float) -> None:
    if b <= 0:
        raise ValueError("需要の傾き b は、正でなければなりません")
    if cost < 0 or a <= cost:
        raise ValueError("費用 c は 0 以上で、価格の上限 a より低くなければなりません")


def inverse_demand_price(quantity: float, a: float, b: float) -> float:
    """逆需要: 市場全体の数量 Q のときの価格 P = a − b·Q。"""
    return a - b * quantity


def monopoly_profit(quantity: float, a: float, b: float, cost: float) -> float:
    """市場全体で Q 作ったときの利潤 π(Q) = (a − b·Q − c)·Q。Q の 2 次関数。"""
    return (inverse_demand_price(quantity, a, b) - cost) * quantity


def monopoly_outcome(a: float, b: float, cost: float) -> MarketOutcome:
    """独占: 利潤の放物線の頂点 Q* = (a − c) ÷ (2b) で、利潤が最大になる。"""
    _validate_market(a, b, cost)
    quantity = (a - cost) / (2 * b)
    return MarketOutcome(
        quantity=quantity,
        price=inverse_demand_price(quantity, a, b),
        profit=monopoly_profit(quantity, a, b, cost),
    )


def competitive_outcome(a: float, b: float, cost: float) -> MarketOutcome:
    """完全競争: 価格が費用に等しくなるまで作る。Q = (a − c) ÷ b、利潤は 0。"""
    _validate_market(a, b, cost)
    return MarketOutcome(quantity=(a - cost) / b, price=cost, profit=0)


def monopoly_deadweight_loss(a: float, b: float, cost: float) -> float:
    """死荷重: 独占で失われる総余剰 = ½·(P独占 − c)·(Q競争 − Q独占)。"""
    monopoly = monopoly_outcome(a, b, cost)
    competition = competitive_outcome(a, b, cost)
    return (monopoly.price - cost) * (competition.quantity - monopoly.quantity) / 2


def cournot_best_response(
    rival_quantity: float, a: float, b: float, cost: float
) -> float:
    """最適反応: 相手の数量を所与として、自社の利潤を最大にする数量（負なら 0）。"""
    return max((a - cost - b * rival_quantity) / (2 * b), 0)


def cournot_duopoly(
    a: float, b: float, cost1: float, cost2: float
) -> tuple[float, float]:
    """2 社のクールノー均衡: 2 つの最適反応を、連立方程式として解く。"""
    _validate_market(a, b, cost1)
    _validate_market(a, b, cost2)
    q1 = (a - 2 * cost1 + cost2) / (3 * b)
    q2 = (a - 2 * cost2 + cost1) / (3 * b)
    if q1 <= 0 or q2 <= 0:
        raise ValueError("2 社とも正の数量を作る均衡がありません")
    return q1, q2


def cournot_outcome(firms: int, a: float, b: float, cost: float) -> MarketOutcome:
    """n 社の対称なクールノー均衡: 1 社 q = (a − c) ÷ ((n + 1)·b)。"""
    if firms < 1:
        raise ValueError("企業の数は、1 以上でなければなりません")
    _validate_market(a, b, cost)
    quantity = firms * (a - cost) / ((firms + 1) * b)
    return MarketOutcome(
        quantity=quantity,
        price=inverse_demand_price(quantity, a, b),
        profit=monopoly_profit(quantity, a, b, cost),
    )
