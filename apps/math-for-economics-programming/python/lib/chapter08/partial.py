"""2 変数関数の偏微分（第 5 章の数値微分を、1 つの変数ずつ当てる）。"""

from collections.abc import Callable, Sequence
from itertools import combinations

from lib.chapter05.derivative import numerical_derivative

Surface = Callable[[float, float], float]


def numerical_partial_x(func: Surface, x: float, y: float, step: float = 1e-5) -> float:
    """y を固定して、x で微分する: ∂f/∂x。"""
    return numerical_derivative(lambda t: func(t, y), x, step)


def numerical_partial_y(func: Surface, x: float, y: float, step: float = 1e-5) -> float:
    """x を固定して、y で微分する: ∂f/∂y。"""
    return numerical_derivative(lambda t: func(x, t), y, step)


def numerical_hessian_2d(
    func: Surface, x: float, y: float, step: float = 1e-3
) -> tuple[float, float, float]:
    """2 階の偏微分 (f_xx, f_xy, f_yy) を、差分で近似する（ヘッセ行列の成分）。"""
    h = step
    center = func(x, y)
    fxx = (func(x + h, y) - 2 * center + func(x - h, y)) / h**2
    fyy = (func(x, y + h) - 2 * center + func(x, y - h)) / h**2
    fxy = (
        func(x + h, y + h)
        - func(x + h, y - h)
        - func(x - h, y + h)
        + func(x - h, y - h)
    ) / (4 * h**2)
    return fxx, fxy, fyy


def classify_critical_point_2d(
    fxx: float, fxy: float, fyy: float, tolerance: float = 1e-9
) -> str:
    """ヘッセ行列の行列式 D = f_xx·f_yy − f_xy² と f_xx の符号で、停留点を分ける。

    数値のヘッセ行列では D がちょうど 0 にならないので、成分の大きさに比べて
    |D| が tolerance 倍以下なら、0 とみなす（判定できない）。
    """
    determinant = fxx * fyy - fxy**2
    if abs(determinant) <= tolerance * (fxx**2 + fxy**2 + fyy**2):
        return "undetermined"
    if determinant < 0:
        return "saddle"
    return "maximum" if fxx < 0 else "minimum"


def quadratic_2d_critical_point(
    a: float, b: float, c: float, d: float, e: float
) -> tuple[float, float]:
    """f = ax² + bxy + cy² + dx + ey の停留点。f_x = f_y = 0 の連立方程式を解く。"""
    determinant = 4 * a * c - b**2
    if determinant == 0:
        raise ValueError("連立方程式の行列式が 0 で、停留点が 1 つに決まりません")
    x = (b * e - 2 * c * d) / determinant
    y = (b * d - 2 * a * e) / determinant
    return x, y


def euler_degree_of_homogeneity(func: Surface, x: float, y: float) -> float:
    """(x·f_x + y·f_y) ÷ f。k 次同次の関数なら、どの点でも k（オイラーの定理）。"""
    value = func(x, y)
    if value == 0:
        raise ValueError("関数の値が 0 の点では、比が決まりません")
    weighted = x * numerical_partial_x(func, x, y) + y * numerical_partial_y(func, x, y)
    return weighted / value


def is_quasi_concave_on_points(
    func: Surface, points: Sequence[tuple[float, float]], steps: int = 11
) -> bool:
    """どの 2 点を結ぶ線分上でも、f が両端の小さいほう以上か（準凹）を調べる。"""
    if len(points) < 2 or steps < 2:
        raise ValueError("点は 2 つ以上、分割は 2 つ以上必要です")
    weights = [i / (steps - 1) for i in range(steps)]
    for (x1, y1), (x2, y2) in combinations(points, 2):
        lowest = min(func(x1, y1), func(x2, y2))
        for t in weights:
            mixed = func(t * x1 + (1 - t) * x2, t * y1 + (1 - t) * y2)
            if mixed < lowest - 1e-12 * (1 + abs(lowest)):
                return False
    return True
