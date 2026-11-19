"""市場の調整過程（ワルラス調整とマーシャル調整）。"""

from collections.abc import Callable


def market_state(excess_demand: float, tolerance: float = 1e-9) -> str:
    """超過需要から市場の状態（品不足・売れ残り・均衡）を返す。"""
    if abs(excess_demand) <= tolerance:
        return "均衡"
    if excess_demand > 0:
        return "品不足"
    return "売れ残り"


def walras_path(
    demand: Callable[[float], float],
    supply: Callable[[float], float],
    initial_price: float,
    step: float,
    tolerance: float = 1e-6,
    max_iterations: int = 1000,
) -> list[float]:
    """ワルラス調整: 超過需要に比例して価格を動かし、価格の推移を返す。"""
    price = initial_price
    path = [price]
    for _ in range(max_iterations):
        excess = demand(price) - supply(price)
        if abs(excess) < tolerance:
            return path
        price += step * excess
        path.append(price)
    raise RuntimeError("価格が収束しなかった。調整の速さ step を小さくする")


def marshall_path(
    demand_price: Callable[[float], float],
    supply_price: Callable[[float], float],
    initial_quantity: float,
    step: float,
    tolerance: float = 1e-6,
    max_iterations: int = 1000,
) -> list[float]:
    """マーシャル調整: 需要価格と供給価格の差に比例して数量を動かし、推移を返す。"""
    quantity = initial_quantity
    path = [quantity]
    for _ in range(max_iterations):
        gap = demand_price(quantity) - supply_price(quantity)
        if abs(gap) < tolerance:
            return path
        quantity += step * gap
        path.append(quantity)
    raise RuntimeError("数量が収束しなかった。調整の速さ step を小さくする")
