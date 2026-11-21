"""外部効果（ピグー税・コースの定理・排出権取引）。

逆需要 P = a − b·Q、私的限界費用 MC = c + d·Q、外部費用は 1 単位あたり e。
外部費用 e が負なら、外部便益（外部経済）を表す。
- 市場の数量: P = 私的 MC（外部費用を、考えない）
- 最適な数量: P = 社会的 MC = 私的 MC + e
- ピグー税: 外部費用に等しい税 e（負なら補助金）
"""

from collections.abc import Sequence
from dataclasses import dataclass

from lib.chapter01.validation import validate_non_negative, validate_positive


@dataclass(frozen=True)
class ExternalityMarket:
    """逆需要 P = a − b·Q、私的限界費用 MC = c + d·Q、外部費用 e（1 単位あたり）。"""

    demand_intercept: float
    demand_slope: float
    cost_intercept: float
    cost_slope: float
    external_cost: float

    def __post_init__(self) -> None:
        validate_positive(self.demand_slope, "需要の傾きは、正にする")
        validate_positive(self.cost_slope, "費用の傾きは、正にする")
        if self.demand_intercept <= self.cost_intercept:
            raise ValueError("需要の切片は、費用の切片より大きくする")


def _quantity(market: ExternalityMarket, extra: float) -> float:
    """P = MC + extra の数量 (a − c − extra) ÷ (b + d)。"""
    return (market.demand_intercept - market.cost_intercept - extra) / (
        market.demand_slope + market.cost_slope
    )


def market_quantity(market: ExternalityMarket) -> float:
    """外部費用を考えない、市場の数量。"""
    return _quantity(market, 0)


def socially_optimal_quantity(market: ExternalityMarket) -> float:
    """社会的に最適な数量（P = 社会的限界費用）。"""
    quantity = _quantity(market, market.external_cost)
    if quantity <= 0:
        raise ValueError("最適な数量が、0 以下になる市場は、扱わない")
    return quantity


def pigou_tax(market: ExternalityMarket) -> float:
    """ピグー税 = 外部費用。負なら補助金。"""
    return market.external_cost


def quantity_with_tax(market: ExternalityMarket, tax: float) -> float:
    """1 単位あたり tax の税（負なら補助金）をかけたときの、市場の数量。"""
    quantity = _quantity(market, tax)
    if quantity <= 0:
        raise ValueError("税が大きすぎて、数量が 0 以下になる")
    return quantity


def externality_deadweight_loss(market: ExternalityMarket) -> float:
    """外部効果を放置した死荷重 = ½ × |外部費用| × |市場の数量 − 最適な数量|。"""
    gap = abs(market_quantity(market) - socially_optimal_quantity(market))
    return 0.5 * abs(market.external_cost) * gap


@dataclass(frozen=True)
class CoaseResult:
    """コースの交渉の結果。汚染が起きるか、補償（交渉）の範囲。"""

    pollution: bool
    payment_range: tuple[float, float] | None


def coase_outcome(gain: float, damage: float, victim_has_right: bool) -> CoaseResult:
    """取引費用が 0 の交渉。権利をどちらに与えても、汚染は、利益 > 被害のときだけ。

    payment_range は、権利を持たない側が、持つ側へ払う金額の範囲。
    """
    validate_non_negative(gain, "利益は、0 以上にする")
    validate_non_negative(damage, "被害は、0 以上にする")
    pollution = gain > damage
    if victim_has_right:
        return CoaseResult(pollution, (damage, gain) if pollution else None)
    return CoaseResult(pollution, None if pollution else (gain, damage))


def _check_firms(slopes: Sequence[float]) -> None:
    if not slopes:
        raise ValueError("企業が、1 社もありません")
    for slope in slopes:
        validate_positive(slope, "限界削減費用の傾きは、正にする")


def emissions_trading(
    slopes: Sequence[float], total_reduction: float
) -> tuple[float, list[float]]:
    """排出権取引。限界削減費用 m_i·x_i を、全社で等しくする（= 排出権の価格）。

    価格 = 総削減量 ÷ Σ(1 ÷ m_i)。各社の削減量 x_i = 価格 ÷ m_i。
    """
    _check_firms(slopes)
    validate_non_negative(total_reduction, "総削減量は、0 以上にする")
    price = total_reduction / sum(1 / slope for slope in slopes)
    return price, [price / slope for slope in slopes]


def uniform_reduction(slopes: Sequence[float], total_reduction: float) -> list[float]:
    """一律規制。全社が、同じ量を、削減する。"""
    _check_firms(slopes)
    return [total_reduction / len(slopes)] * len(slopes)


def abatement_cost(slopes: Sequence[float], reductions: Sequence[float]) -> float:
    """削減費用の合計 Σ ½·m_i·x_i²。"""
    return sum(0.5 * m * x**2 for m, x in zip(slopes, reductions, strict=True))
