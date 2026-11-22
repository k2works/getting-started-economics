"""屈折需要曲線（寡占の価格の硬直性）。

値上げには、他社がついてこないので、需要は弾力的（傾きが緩やか）。
値下げには、他社もついてくるので、需要は非弾力的（傾きが急）。
屈折点で、限界収入が途切れ、限界費用がその範囲なら、価格は動かない。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class KinkedDemand:
    """屈折点 (数量, 価格) と、屈折点の上・下の需要曲線の傾き（大きさ）。"""

    kink_quantity: float
    kink_price: float
    upper_slope: float
    lower_slope: float

    def __post_init__(self) -> None:
        if self.kink_quantity <= 0 or self.kink_price <= 0:
            raise ValueError("屈折点の数量と価格は、正にする")
        if not 0 < self.upper_slope < self.lower_slope:
            raise ValueError("傾きは、0 < 上の傾き < 下の傾き にする")


def marginal_revenue_above(demand: KinkedDemand) -> float:
    """屈折点の、緩やかな側（上）の限界収入 P − b₁·Q。"""
    return demand.kink_price - demand.upper_slope * demand.kink_quantity


def marginal_revenue_below(demand: KinkedDemand) -> float:
    """屈折点の、急な側（下）の限界収入 P − b₂·Q。"""
    return demand.kink_price - demand.lower_slope * demand.kink_quantity


def marginal_revenue_gap(demand: KinkedDemand) -> float:
    """限界収入の途切れの大きさ (b₂ − b₁)·Q。"""
    return marginal_revenue_above(demand) - marginal_revenue_below(demand)


def price_stays(demand: KinkedDemand, marginal_cost: float) -> bool:
    """限界費用が、途切れの範囲の中なら、価格は、屈折点のまま。"""
    return (
        marginal_revenue_below(demand)
        <= marginal_cost
        <= marginal_revenue_above(demand)
    )


def price_when_cost_shifts(demand: KinkedDemand, marginal_cost: float) -> float:
    """限界費用が変わったときの価格。途切れの中なら、屈折点の価格のまま。"""
    if not price_stays(demand, marginal_cost):
        raise ValueError("限界費用が、途切れの範囲を出ると、屈折点では決まらない")
    return demand.kink_price
