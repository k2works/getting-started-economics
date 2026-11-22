"""市場均衡と調整過程（直線の需要曲線・供給曲線）。

需要 Q = a + s_d·P（s_d < 0）、供給 Q = c + s_s·P（s_s > 0）。
均衡は、需要量 = 供給量の点。
- ワルラス的調整: 価格が、超過需要に応じて動く（超過需要なら上がり、超過供給なら下がる）
- マーシャル的調整: 数量が、需要価格と供給価格の差に応じて動く
"""

from dataclasses import dataclass, replace
from typing import Literal

from lib.chapter01.validation import validate_non_negative, validate_positive
from lib.chapter03.demand import linear_demand_quantity

# 均衡の判定で、同じ値と見なす誤差
_TOLERANCE = 1e-9


@dataclass(frozen=True)
class LinearMarket:
    """直線の需要曲線と供給曲線。Q = 切片 + 傾き × P。"""

    demand_intercept: float
    demand_slope: float
    supply_intercept: float
    supply_slope: float

    def __post_init__(self) -> None:
        if self.demand_slope >= 0:
            raise ValueError("需要の傾きは、負にする（価格が上がると、需要量が減る）")
        validate_positive(
            self.supply_slope,
            "供給の傾きは、正にする（価格が上がると、供給量が増える）",
        )


def quantity_demanded(market: LinearMarket, price: float) -> float:
    """価格 P での需要量。負にならない。"""
    return linear_demand_quantity(market.demand_intercept, market.demand_slope, price)


def quantity_supplied(market: LinearMarket, price: float) -> float:
    """価格 P での供給量。負にならない。"""
    return linear_demand_quantity(market.supply_intercept, market.supply_slope, price)


def equilibrium(market: LinearMarket) -> tuple[float, float]:
    """均衡の価格と数量 (P*, Q*)。

    a + s_d·P = c + s_s·P から、P* = (a − c) ÷ (s_s − s_d)。
    """
    price = (market.demand_intercept - market.supply_intercept) / (
        market.supply_slope - market.demand_slope
    )
    quantity = market.demand_intercept + market.demand_slope * price
    if price <= 0 or quantity <= 0:
        raise ValueError("価格も数量も正になる均衡が、存在しない")
    return price, quantity


def excess_demand(market: LinearMarket, price: float) -> float:
    """超過需要 = 需要量 − 供給量。正なら需要超過、負なら供給超過。"""
    return quantity_demanded(market, price) - quantity_supplied(market, price)


def price_state(
    market: LinearMarket, price: float
) -> Literal["均衡", "供給超過（価格が下がる）", "需要超過（価格が上がる）"]:
    """価格が、均衡より高いか低いかを、超過需要で判定する。"""
    excess = excess_demand(market, price)
    if abs(excess) <= _TOLERANCE:
        return "均衡"
    if excess < 0:
        return "供給超過（価格が下がる）"
    return "需要超過（価格が上がる）"


def _check_adjustment(speed: float, steps: int) -> None:
    validate_positive(speed, "調整の速さは、正にする")
    validate_non_negative(steps, "調整の回数は、0 以上にする")


def walras_adjustment(
    market: LinearMarket, price0: float, speed: float, steps: int
) -> list[float]:
    """ワルラス的調整。P' = P + 速さ × 超過需要。初期値を含む、steps + 1 個の価格。"""
    _check_adjustment(speed, steps)
    prices = [price0]
    for _ in range(steps):
        prices.append(prices[-1] + speed * excess_demand(market, prices[-1]))
    return prices


def marshall_adjustment(
    market: LinearMarket, quantity0: float, speed: float, steps: int
) -> list[float]:
    """マーシャル的調整。Q' = Q + 速さ × (需要価格 − 供給価格)。

    初期値を含む、steps + 1 個の数量を返す。需要価格は、その数量を買ってもらえる、
    最高の価格。供給価格は、その数量を作る、最低の価格。
    """
    _check_adjustment(speed, steps)
    quantities = [quantity0]
    for _ in range(steps):
        q = quantities[-1]
        demand_price = (q - market.demand_intercept) / market.demand_slope
        supply_price = (q - market.supply_intercept) / market.supply_slope
        quantities.append(q + speed * (demand_price - supply_price))
    return quantities


def shift_demand(market: LinearMarket, delta: float) -> LinearMarket:
    """需要曲線を、数量の方向に delta だけ動かす（正なら右へ）。元の市場は変えない。"""
    return replace(market, demand_intercept=market.demand_intercept + delta)


def shift_supply(market: LinearMarket, delta: float) -> LinearMarket:
    """供給曲線を、数量の方向に delta だけ動かす（正なら右へ。費用の低下）。"""
    return replace(market, supply_intercept=market.supply_intercept + delta)
