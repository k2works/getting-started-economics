"""個々の企業の供給関数と、経済全体の総供給関数。"""

from collections.abc import Sequence

from lib.chapter05.cost import profit_maximizing_quantity
from lib.chapter05.derivative import Polynomial


def aggregate_supply_quantity(price: float, costs: Sequence[Polynomial]) -> float:
    """総供給: 同じ価格での各企業の供給量（P = MC の数量）を、横に足す。"""
    return sum(profit_maximizing_quantity(price, cost) for cost in costs)
