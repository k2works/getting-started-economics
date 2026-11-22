"""1 変数の微分: 多項式の導関数（公式）と、中心差分による数値微分。"""

from collections.abc import Callable
from dataclasses import dataclass

from lib.chapter02.quadratic import quadratic_roots


@dataclass(frozen=True)
class Polynomial:
    """多項式 c₀ + c₁x + c₂x² + …。係数は、次数の低い順に並べる。"""

    coefficients: tuple[float, ...]

    def __post_init__(self) -> None:
        trimmed = list(self.coefficients)
        while len(trimmed) > 1 and trimmed[-1] == 0:
            trimmed.pop()
        object.__setattr__(self, "coefficients", tuple(trimmed or [0]))

    def __call__(self, x: float) -> float:
        """ホーナー法: ((c_n·x + c_{n−1})·x + …)·x + c₀。"""
        value: float = 0
        for c in reversed(self.coefficients):
            value = value * x + c
        return value

    def derivative(self) -> "Polynomial":
        """冪の公式 (x^n)' = n·x^(n−1) を、項ごとに当てる（和と定数倍の公式）。"""
        terms = [k * c for k, c in enumerate(self.coefficients)]
        return Polynomial(tuple(terms[1:]))

    def __add__(self, other: "Polynomial") -> "Polynomial":
        """和: 同じ次数の係数どうしを足す（短いほうは 0 で埋める）。"""
        size = max(len(self.coefficients), len(other.coefficients))
        left = self.coefficients + (0,) * (size - len(self.coefficients))
        right = other.coefficients + (0,) * (size - len(other.coefficients))
        return Polynomial(tuple(a + b for a, b in zip(left, right, strict=True)))

    def scale(self, factor: float) -> "Polynomial":
        """定数倍: すべての係数に factor を掛ける。"""
        return Polynomial(tuple(factor * c for c in self.coefficients))


def numerical_derivative(
    func: Callable[[float], float], x: float, step: float = 1e-5
) -> float:
    """中心差分 (f(x + h) − f(x − h)) ÷ (2h) で、x での傾きを近似する。"""
    if step <= 0:
        raise ValueError("刻み幅 h は、正でなければなりません")
    return (func(x + step) - func(x - step)) / (2 * step)


def difference_quotient_errors(
    func: Callable[[float], float], exact_slope: float, x: float, steps: list[float]
) -> list[float]:
    """刻み幅ごとの、数値微分と正しい傾きの差（絶対値）。"""
    return [abs(numerical_derivative(func, x, h) - exact_slope) for h in steps]


def stationary_points(poly: Polynomial) -> tuple[float, ...]:
    """f'(x) = 0 の点を、小さい順に返す（3 次以下の多項式。導関数が 2 次以下）。"""
    if len(poly.coefficients) > 4:
        raise ValueError("3 次以下の多項式だけを扱います")
    d0, d1, d2 = (poly.derivative().coefficients + (0, 0))[:3]
    if d2 != 0:
        return quadratic_roots(d2, d1, d0)
    if d1 != 0:
        return (-d0 / d1,)
    if d0 == 0:
        raise ValueError("定数関数は、すべての点で傾きが 0 です")
    return ()


def classify_stationary_point(poly: Polynomial, x: float) -> str:
    """2 階の導関数の符号で、極大（負）・極小（正）・判定できない（0）に分ける。"""
    curvature = poly.derivative().derivative()(x)
    if curvature < 0:
        return "maximum"
    if curvature > 0:
        return "minimum"
    return "undetermined"


def is_concave_on(poly: Polynomial, low: float, high: float, points: int = 101) -> bool:
    """区間を points 個の点に区切り、どの点でも 2 階の導関数が 0 以下なら凹。"""
    if points < 2 or low >= high:
        raise ValueError("区間は low < high で、点は 2 つ以上必要です")
    curvature = poly.derivative().derivative()
    step = (high - low) / (points - 1)
    return all(curvature(low + i * step) <= 0 for i in range(points))
