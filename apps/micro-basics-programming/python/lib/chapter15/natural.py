"""自然独占（費用逓減産業）の価格規制。

総費用 C = F + c·Q（固定費用 F が大きい）。平均費用 AC = c + F ÷ Q は右下がりで、
限界費用 c より、常に高い。
- 限界費用価格形成: P = MC。効率的だが、固定費用の分だけ赤字（補助金が必要）
- 平均費用価格形成: P = AC。利潤 0。価格は MC より高く、数量は少ない
"""

import math
from dataclasses import replace

from lib.chapter01.validation import validate_positive
from lib.chapter11.monopoly import (
    MarketOutcome,
    Monopoly,
    competitive_outcome,
    monopoly_outcome,
)


def natural_average_cost(
    monopoly: Monopoly, fixed_cost: float, quantity: float
) -> float:
    """平均費用 AC = c + F ÷ Q。"""
    validate_positive(quantity, "数量は、正にする")
    return monopoly.marginal_cost + fixed_cost / quantity


def marginal_cost_pricing(monopoly: Monopoly, fixed_cost: float) -> MarketOutcome:
    """限界費用価格形成。利潤は、固定費用の分だけ、赤字。"""
    validate_positive(fixed_cost, "固定費用は、正にする")
    outcome = competitive_outcome(monopoly)
    return replace(outcome, profit=outcome.profit - fixed_cost)


def required_subsidy(monopoly: Monopoly, fixed_cost: float) -> float:
    """限界費用価格形成で、必要な補助金 = 固定費用。"""
    validate_positive(fixed_cost, "固定費用は、正にする")
    return -marginal_cost_pricing(monopoly, fixed_cost).profit


def average_cost_pricing(monopoly: Monopoly, fixed_cost: float) -> MarketOutcome:
    """平均費用価格形成。P = AC から b·Q² − (a − c)·Q + F = 0 の、大きい方の解。"""
    validate_positive(fixed_cost, "固定費用は、正にする")
    gap = monopoly.demand_intercept - monopoly.marginal_cost
    b = monopoly.demand_slope
    discriminant = gap**2 - 4 * b * fixed_cost
    if discriminant < 0:
        raise ValueError("固定費用が大きすぎて、平均費用が、需要曲線に届かない")
    quantity = (gap + math.sqrt(discriminant)) / (2 * b)
    price = monopoly.demand_intercept - b * quantity
    return MarketOutcome(
        price,
        quantity,
        (price - monopoly.marginal_cost) * quantity - fixed_cost,
        0.5 * (monopoly.demand_intercept - price) * quantity,
    )


def unregulated_outcome(monopoly: Monopoly, fixed_cost: float) -> MarketOutcome:
    """規制しない独占（MR = MC）。利潤は、固定費用を引いた値。"""
    validate_positive(fixed_cost, "固定費用は、正にする")
    outcome = monopoly_outcome(monopoly)
    return replace(outcome, profit=outcome.profit - fixed_cost)
