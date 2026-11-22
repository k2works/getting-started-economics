"""費用曲線: 総費用・限界費用・平均費用・平均可変費用。

総費用 C(q) = a·q³ + b·q² + c·q + F（F は固定費用）。逆 S 字の総費用曲線を表す。
- 限界費用 MC = C'(q)（総費用曲線の接線の傾き）
- 平均費用 AC = C(q) ÷ q（原点からの直線の傾き）
- 平均可変費用 AVC = (C(q) − F) ÷ q（固定費の切片からの直線の傾き）
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from lib.chapter01.validation import validate_non_negative, validate_positive


@dataclass(frozen=True)
class CostCurve:
    """総費用 C(q) = cubic·q³ + quadratic·q² + linear·q + fixed の係数。"""

    cubic: float
    quadratic: float
    linear: float
    fixed: float

    def __post_init__(self) -> None:
        validate_positive(self.cubic, "3 次の係数は、正にする")
        validate_non_negative(self.fixed, "固定費用は、0 以上にする")
        a, b, c = self.cubic, self.quadratic, self.linear
        if c < 0 or (b < 0 and b**2 > 3 * a * c):
            raise ValueError(
                "限界費用が負になる係数は、扱わない（c ≥ 0、b ≥ 0 または b² ≤ 3ac）"
            )


def _check_quantity(q: float) -> None:
    validate_non_negative(q, "生産量は、0 以上にする")


def variable_cost(curve: CostCurve, q: float) -> float:
    """可変費用 VC(q) = C(q) − F。生産量とともに増える。"""
    _check_quantity(q)
    return curve.cubic * q**3 + curve.quadratic * q**2 + curve.linear * q


def total_cost(curve: CostCurve, q: float) -> float:
    """総費用 C(q) = 可変費用 + 固定費用。"""
    return variable_cost(curve, q) + curve.fixed


def marginal_cost(curve: CostCurve, q: float) -> float:
    """限界費用 MC = C'(q) = 3a·q² + 2b·q + c。固定費用には依らない。"""
    _check_quantity(q)
    return 3 * curve.cubic * q**2 + 2 * curve.quadratic * q + curve.linear


def average_cost(curve: CostCurve, q: float) -> float:
    """平均費用 AC = C(q) ÷ q。生産量が 0 のときは、求められない。"""
    validate_positive(q, "平均費用の生産量は、正にする")
    return total_cost(curve, q) / q


def average_variable_cost(curve: CostCurve, q: float) -> float:
    """平均可変費用 AVC = VC(q) ÷ q。いつも、平均費用より、固定費用 ÷ q だけ低い。"""
    validate_positive(q, "平均可変費用の生産量は、正にする")
    return variable_cost(curve, q) / q


def marginal_cost_by_gradient(costs: ArrayLike, quantities: ArrayLike) -> list[float]:
    """総費用の並びから、数値微分（NumPy の勾配）で、限界費用を求める。"""
    y = np.asarray(costs, dtype=float)
    x = np.asarray(quantities, dtype=float)
    if y.shape != x.shape:
        raise ValueError("総費用と生産量は、同じ長さにする")
    return [float(v) for v in np.gradient(y, x)]


def argmin_of(values: ArrayLike, positions: ArrayLike) -> tuple[float, float]:
    """値の並びの最小値と、その位置 (位置, 最小値)。同じ値が複数あれば、先の位置。"""
    v = np.asarray(values, dtype=float)
    x = np.asarray(positions, dtype=float)
    if v.shape != x.shape:
        raise ValueError("値と位置は、同じ長さにする")
    index = int(np.argmin(v))
    return float(x[index]), float(v[index])


def cost_minima(
    curve: CostCurve, q_max: float = 10.0, points: int = 10001
) -> dict[str, tuple[float, float]]:
    """MC・AVC・AC の最低点 (生産量, 値) を、格子点の探索で求める。"""
    validate_positive(q_max, "探索の上限は、正にする")
    validate_positive(points - 2, "点の数は、3 以上にする")
    grid = np.linspace(0.0, q_max, points)
    positive = grid[1:]
    minima = {
        "MC": argmin_of([marginal_cost(curve, float(q)) for q in grid], grid),
        "AVC": argmin_of(
            [average_variable_cost(curve, float(q)) for q in positive], positive
        ),
        "AC": argmin_of([average_cost(curve, float(q)) for q in positive], positive),
    }
    if any(q >= q_max for q, _ in minima.values()):
        raise ValueError("最低点が探索の上限に届いた。上限 q_max を大きくする")
    return minima
