"""積分: 区間を細かく分けて面積を足す数値積分（中点法・台形法）と、多項式の公式。"""

from collections.abc import Callable, Sequence

from lib.chapter05.derivative import Polynomial

IntegrationRule = Callable[[Callable[[float], float], float, float, int], float]


def _require_pieces(pieces: int) -> None:
    if pieces < 1:
        raise ValueError("分割数は、1 以上でなければなりません")


def midpoint_rule_integral(
    func: Callable[[float], float], low: float, high: float, pieces: int
) -> float:
    """中点法: 区間を pieces 等分し、各小区間の中点の高さ × 幅を足す。"""
    _require_pieces(pieces)
    width = (high - low) / pieces
    return sum(func(low + (i + 0.5) * width) for i in range(pieces)) * width


def trapezoid_rule_integral(
    func: Callable[[float], float], low: float, high: float, pieces: int
) -> float:
    """台形法: 各小区間の両端の高さの平均 × 幅を足す（両端の点は半分だけ数える）。"""
    _require_pieces(pieces)
    width = (high - low) / pieces
    inner = sum(func(low + i * width) for i in range(1, pieces))
    return (func(low) / 2 + inner + func(high) / 2) * width


def quadrature_errors(
    rule: IntegrationRule,
    func: Callable[[float], float],
    exact: float,
    low: float,
    high: float,
    pieces: Sequence[int],
) -> list[float]:
    """分割数ごとの、数値積分と正しい値の差（絶対値）。"""
    if not pieces:
        raise ValueError("分割数を、1 つ以上与えてください")
    return [abs(rule(func, low, high, n) - exact) for n in pieces]


def polynomial_antiderivative(poly: Polynomial) -> Polynomial:
    """不定積分: x^k を x^(k+1) ÷ (k + 1) にする（冪の公式の逆。積分定数は 0）。"""
    terms = [c / (k + 1) for k, c in enumerate(poly.coefficients)]
    return Polynomial((0, *terms))


def polynomial_definite_integral(poly: Polynomial, low: float, high: float) -> float:
    """定積分 ∫ f(x) dx = F(high) − F(low)。F は不定積分。"""
    antiderivative = polynomial_antiderivative(poly)
    return antiderivative(high) - antiderivative(low)
