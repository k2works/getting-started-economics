"""2 次関数 y = a·x² + b·x + c: 平方完成・頂点・判別式・解の公式・格子探索。"""

import math
from collections.abc import Callable


def _require_quadratic(a: float) -> None:
    if a == 0:
        raise ValueError("x² の係数 a が 0 では、2 次関数ではありません")


def complete_the_square(a: float, b: float, c: float) -> tuple[float, float, float]:
    """平方完成: a·x² + b·x + c = a·(x − h)² + k の（a, h, k）を返す。"""
    _require_quadratic(a)
    h = -b / (2 * a)
    k = c - b**2 / (4 * a)
    return a, h, k


def parabola_vertex(a: float, b: float, c: float) -> tuple[float, float]:
    """放物線の頂点（h, k）。a < 0 なら最大値、a > 0 なら最小値。"""
    _, h, k = complete_the_square(a, b, c)
    return h, k


def quadratic_discriminant(a: float, b: float, c: float) -> float:
    """判別式 D = b² − 4ac。正なら実数解 2 つ、0 なら 1 つ、負ならなし。"""
    return b**2 - 4 * a * c


def quadratic_roots(a: float, b: float, c: float) -> tuple[float, ...]:
    """解の公式で、a·x² + b·x + c = 0 の実数解を、小さい順に返す。"""
    _require_quadratic(a)
    d = quadratic_discriminant(a, b, c)
    if d < 0:
        return ()
    if d == 0:
        return (-b / (2 * a),)
    root = math.sqrt(d)
    return tuple(sorted([(-b - root) / (2 * a), (-b + root) / (2 * a)]))


def argmax_on_grid(
    func: Callable[[float], float], low: float, high: float, points: int
) -> float:
    """low から high までを、等間隔の points 個の点に区切り、func が最大の点を返す。"""
    if points < 2:
        raise ValueError("格子の点は、2 つ以上必要です")
    step = (high - low) / (points - 1)
    grid = [low + i * step for i in range(points)]
    return max(grid, key=func)
