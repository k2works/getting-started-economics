"""1 次関数で表した需要・供給と、市場均衡・余剰。"""

from collections.abc import Sequence
from dataclasses import dataclass


def line_through(
    first: tuple[float, float], second: tuple[float, float]
) -> tuple[float, float]:
    """2 点を通る直線 y = 傾き × x + 切片 の（傾き, 切片）を返す。"""
    (x1, y1), (x2, y2) = first, second
    if x1 == x2:
        raise ValueError("x が同じ 2 点では、直線の式が決まりません")
    slope = (y2 - y1) / (x2 - x1)
    return slope, y1 - slope * x1


def demand_quantity(price: float, a: float, b: float) -> float:
    """需要量 q = a − b·p。価格が高すぎて負になるときは 0。"""
    return max(a - b * price, 0)


def supply_quantity(price: float, c: float, d: float) -> float:
    """供給量 q = c + d·p。負になるときは 0。"""
    return max(c + d * price, 0)


@dataclass(frozen=True)
class Equilibrium:
    """市場均衡（価格と数量）。"""

    price: float
    quantity: float

    @property
    def revenue(self) -> float:
        """売り手の収入 = 価格 × 数量。"""
        return self.price * self.quantity


def _validate_slopes(b: float, d: float) -> None:
    if b <= 0 or d <= 0:
        raise ValueError("需要の傾き b と供給の傾き d は、正でなければなりません")


def equilibrium(a: float, b: float, c: float, d: float) -> Equilibrium:
    """均衡: 需要 q = a − b·p と供給 q = c + d·p の交点（p について解く）。"""
    _validate_slopes(b, d)
    price = (a - c) / (b + d)
    quantity = a - b * price
    if price <= 0 or quantity <= 0:
        raise ValueError("価格も数量も正になる均衡がありません")
    return Equilibrium(price=price, quantity=quantity)


def consumer_surplus(price: float, a: float, b: float) -> float:
    """消費者余剰: 需要曲線の下で、価格の上の三角形の面積。"""
    top = a / b
    if price >= top:
        return 0
    return (top - price) * demand_quantity(price, a, b) / 2


def producer_surplus(price: float, c: float, d: float) -> float:
    """生産者余剰: 価格の下で、供給曲線の上の面積（供給量を足す）。"""
    low = max(-c / d, 0)
    if price <= low:
        return 0
    return c * (price - low) + d * (price**2 - low**2) / 2


def total_surplus(a: float, b: float, c: float, d: float) -> float:
    """均衡での総余剰 = 消費者余剰 + 生産者余剰。"""
    price = equilibrium(a, b, c, d).price
    return consumer_surplus(price, a, b) + producer_surplus(price, c, d)


def market_demand(price: float, individuals: Sequence[tuple[float, float]]) -> float:
    """個人の需要 q = a − b·p を、横に（数量を）足した市場の需要。"""
    return sum(demand_quantity(price, a, b) for a, b in individuals)


def constant_cost_equilibrium(a: float, b: float, unit_cost: float) -> Equilibrium:
    """単位あたり費用が一定のとき、供給は水平で、価格は費用に等しい。"""
    quantity = demand_quantity(unit_cost, a, b)
    if unit_cost <= 0 or quantity <= 0:
        raise ValueError("費用が正で、需要の上限より低いときだけ、均衡があります")
    return Equilibrium(price=unit_cost, quantity=quantity)
