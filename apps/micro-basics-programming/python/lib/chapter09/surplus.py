"""余剰分析と課税。

- 消費者余剰: 需要曲線と価格の間（支払意思額 − 支払額の合計）
- 生産者余剰: 価格と供給曲線の間（価格 − 限界費用の合計）
- 総余剰: 消費者余剰 + 生産者余剰。市場均衡の数量で、最大になる
- 課税: 買い手の価格と、売り手の手取りに、税額の差ができる。取引が減り、死荷重が生まれる
"""

from dataclasses import dataclass

from lib.chapter01.validation import validate_non_negative
from lib.chapter08.market import (
    LinearMarket,
    equilibrium,
    quantity_demanded,
    quantity_supplied,
)


def choke_price(market: LinearMarket) -> float:
    """需要量が 0 になる価格（需要曲線の、価格の軸との切片）。"""
    return -market.demand_intercept / market.demand_slope


def reservation_price(market: LinearMarket) -> float:
    """供給が始まる価格（供給曲線の、価格の軸との切片）。"""
    return -market.supply_intercept / market.supply_slope


def consumer_surplus(market: LinearMarket, price: float) -> float:
    """消費者余剰 = ½ × (需要がなくなる価格 − 価格) × 需要量。"""
    gap = max(0.0, choke_price(market) - price)
    return 0.5 * gap * quantity_demanded(market, price)


def producer_surplus(market: LinearMarket, price: float) -> float:
    """生産者余剰 = ½ × (価格 − 供給が始まる価格) × 供給量。"""
    gap = max(0.0, price - reservation_price(market))
    return 0.5 * gap * quantity_supplied(market, price)


def total_surplus_at_quantity(market: LinearMarket, quantity: float) -> float:
    """数量 q を取引したときの総余剰 = 需要価格と供給価格の差の、0 から q までの合計。

    需要価格と供給価格は、どちらも q の 1 次式なので、差の面積は、q の 2 次式。
    """
    if quantity < 0 or quantity > market.demand_intercept:
        raise ValueError("数量は、0 以上、需要曲線の数量の切片以下にする")
    intercept_gap = choke_price(market) - reservation_price(market)
    slope_gap = 1 / market.demand_slope - 1 / market.supply_slope
    return intercept_gap * quantity + 0.5 * slope_gap * quantity**2


def deadweight_loss_at_quantity(market: LinearMarket, quantity: float) -> float:
    """均衡の数量でない数量での、総余剰の損失（三角形）。均衡より少なくても多くても出る。"""
    _, best = equilibrium(market)
    return total_surplus_at_quantity(market, best) - total_surplus_at_quantity(
        market, quantity
    )


@dataclass(frozen=True)
class TaxResult:
    """従量税のもとの、市場の結果。"""

    buyer_price: float
    seller_price: float
    quantity: float
    tax_revenue: float
    consumer_surplus: float
    producer_surplus: float
    deadweight_loss: float


def tax_equilibrium(market: LinearMarket, tax: float) -> TaxResult:
    """従量税（売り手に、1 単位あたり tax 円）のもとの、均衡と余剰。

    買い手の価格 P_d と、売り手の手取り P_s = P_d − tax で、需要量 = 供給量。
    a + s_d·P_d = c + s_s·(P_d − tax) から、P_d = (a − c + s_s·tax) ÷ (s_s − s_d)。
    """
    validate_non_negative(tax, "税額は、0 以上にする")
    buyer_price = (
        market.demand_intercept - market.supply_intercept + market.supply_slope * tax
    ) / (market.supply_slope - market.demand_slope)
    seller_price = buyer_price - tax
    quantity = quantity_demanded(market, buyer_price)
    if quantity <= 0:
        raise ValueError("税が大きすぎて、取引がなくなる")
    _, best_quantity = equilibrium(market)
    return TaxResult(
        buyer_price,
        seller_price,
        quantity,
        tax * quantity,
        consumer_surplus(market, buyer_price),
        producer_surplus(market, seller_price),
        0.5 * tax * (best_quantity - quantity),
    )


def tax_incidence(market: LinearMarket, tax: float) -> tuple[float, float]:
    """税の負担 (買い手の負担, 売り手の負担)。均衡価格からの、価格の動き。

    弾力性の小さい（曲線が急な）側が、多く負担する。2 つの和は、税額。
    """
    result = tax_equilibrium(market, tax)
    price, _ = equilibrium(market)
    return result.buyer_price - price, price - result.seller_price
