"""独占と独占的競争。

逆需要 P = a − b·Q。独占企業は、価格を決められる（プライスメイカー）。
- 限界収入 MR = a − 2b·Q（需要曲線の 2 倍の傾き）
- 独占の数量は、MR = MC の点。価格は、その数量の、需要曲線の上
- 完全競争（P = MC）より、価格が高く、数量が少なく、死荷重が出る
"""

import math
from dataclasses import dataclass

from lib.chapter01.validation import validate_non_negative, validate_positive


@dataclass(frozen=True)
class Monopoly:
    """逆需要 P = a − b·Q と、一定の限界費用。"""

    demand_intercept: float
    demand_slope: float
    marginal_cost: float

    def __post_init__(self) -> None:
        validate_positive(self.demand_slope, "需要の傾きは、正にする")
        validate_non_negative(self.marginal_cost, "限界費用は、0 以上にする")
        if self.demand_intercept <= self.marginal_cost:
            raise ValueError("需要の切片（最高の価格）は、限界費用より大きくする")


@dataclass(frozen=True)
class MarketOutcome:
    """価格・数量・利潤・消費者余剰。総余剰 = 消費者余剰 + 利潤。"""

    price: float
    quantity: float
    profit: float
    consumer_surplus: float

    @property
    def total_surplus(self) -> float:
        """総余剰 = 消費者余剰 + 利潤。"""
        return self.consumer_surplus + self.profit


def price_at(monopoly: Monopoly, quantity: float) -> float:
    """数量 Q を買ってもらえる、最高の価格（逆需要）。P = a − b·Q。"""
    if quantity < 0 or quantity > monopoly.demand_intercept / monopoly.demand_slope:
        raise ValueError("数量は、0 以上、需要の数量の切片以下にする")
    return monopoly.demand_intercept - monopoly.demand_slope * quantity


def marginal_revenue(monopoly: Monopoly, quantity: float) -> float:
    """限界収入 MR = a − 2b·Q。1 単位多く売ると、価格が下がるので、価格より低い。"""
    validate_non_negative(quantity, "数量は、0 以上にする")
    return monopoly.demand_intercept - 2 * monopoly.demand_slope * quantity


def _outcome(monopoly: Monopoly, quantity: float) -> MarketOutcome:
    price = price_at(monopoly, quantity)
    return MarketOutcome(
        price,
        quantity,
        (price - monopoly.marginal_cost) * quantity,
        0.5 * (monopoly.demand_intercept - price) * quantity,
    )


def monopoly_outcome(monopoly: Monopoly) -> MarketOutcome:
    """独占の結果。MR = MC から、Q = (a − c) ÷ 2b。"""
    quantity = (monopoly.demand_intercept - monopoly.marginal_cost) / (
        2 * monopoly.demand_slope
    )
    return _outcome(monopoly, quantity)


def competitive_outcome(monopoly: Monopoly) -> MarketOutcome:
    """完全競争の結果。P = MC から、Q = (a − c) ÷ b。利潤は 0。"""
    quantity = (
        monopoly.demand_intercept - monopoly.marginal_cost
    ) / monopoly.demand_slope
    return _outcome(monopoly, quantity)


def deadweight_loss(monopoly: Monopoly) -> float:
    """独占の死荷重 = 完全競争の総余剰 − 独占の総余剰。"""
    return (
        competitive_outcome(monopoly).total_surplus
        - monopoly_outcome(monopoly).total_surplus
    )


def demand_elasticity(monopoly: Monopoly, quantity: float) -> float:
    """需要の価格弾力性（大きさ）e = P ÷ (b·Q)。"""
    validate_positive(quantity, "数量は、正にする")
    return price_at(monopoly, quantity) / (monopoly.demand_slope * quantity)


def lerner_index(monopoly: Monopoly, price: float) -> float:
    """ラーナー指数 (P − MC) ÷ P。独占力の大きさ。利潤最大なら、弾力性の逆数。"""
    validate_positive(price, "価格は、正にする")
    return (price - monopoly.marginal_cost) / price


def monopolistic_competition_profit(monopoly: Monopoly, fixed_cost: float) -> float:
    """独占的競争の、短期の利潤 = 独占の利潤 − 固定費用。正なら、新規参入が起きる。"""
    return monopoly_outcome(monopoly).profit - fixed_cost


@dataclass(frozen=True)
class LongRunResult:
    """独占的競争の長期均衡。参入で、需要が左へ動き、利潤が 0 になる。"""

    price: float
    quantity: float
    demand_intercept: float
    profit: float


def long_run_monopolistic_competition(
    marginal_cost: float, demand_slope: float, fixed_cost: float
) -> LongRunResult:
    """長期均衡。参入で、需要の切片が a' に下がり、独占の利潤が 0 になる。

    利潤 (a' − c)² ÷ 4b が、固定費用 F に等しいので、a' = c + 2√(b·F)。
    数量は √(F ÷ b)、価格は c + √(b·F)。価格は、平均費用 c + F ÷ q に等しい。
    """
    validate_non_negative(marginal_cost, "限界費用は、0 以上にする")
    validate_positive(demand_slope, "需要の傾きは、正にする")
    validate_positive(fixed_cost, "固定費用は、正にする")
    root = math.sqrt(demand_slope * fixed_cost)
    quantity = math.sqrt(fixed_cost / demand_slope)
    price = marginal_cost + root
    return LongRunResult(
        price,
        quantity,
        marginal_cost + 2 * root,
        (price - marginal_cost) * quantity - fixed_cost,
    )
