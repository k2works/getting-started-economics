"""連続確率変数: 一様分布の密度関数・分布関数と、積分で求める期待値。"""

from collections.abc import Callable
from fractions import Fraction

from lib.chapter11.integral import midpoint_rule_integral


def _require_interval(low: float, high: float) -> None:
    if low >= high:
        raise ValueError("区間は、下端より上端が大きくなければなりません")


def uniform_density(x: float, low: float = 0, high: float = 1) -> float:
    """一様分布の密度 f(x) = 1 ÷ (high − low)（区間の中）、区間の外では 0。"""
    _require_interval(low, high)
    return 1 / (high - low) if low <= x <= high else 0


def uniform_cdf(x: float, low: float = 0, high: float = 1) -> float:
    """一様分布の分布関数 F(x) = P(X ≤ x)。区間の中では (x − low) ÷ (high − low)。"""
    _require_interval(low, high)
    return min(max((x - low) / (high - low), 0), 1)


def continuous_expectation(
    value: Callable[[float], float],
    density: Callable[[float], float],
    low: float,
    high: float,
    pieces: int = 10_000,
) -> float:
    """E[g(X)] = ∫ g(x)·f(x) dx。離散の Σ g(x)·P(x) の、和を積分に替えたもの。"""
    return midpoint_rule_integral(lambda x: value(x) * density(x), low, high, pieces)


def continuous_expected_value(
    density: Callable[[float], float], low: float, high: float, pieces: int = 10_000
) -> float:
    """連続確率変数の期待値 E[X] = ∫ x·f(x) dx。"""
    return continuous_expectation(lambda x: x, density, low, high, pieces)


def discretized_uniform_distribution(points: int) -> dict[Fraction, Fraction]:
    """[0, 1] の一様分布を、1/n, 2/n, …, 1 の n 個の値（どれも確率 1/n）で近似する。"""
    if points < 1:
        raise ValueError("点の数は、1 以上でなければなりません")
    return {Fraction(k, points): Fraction(1, points) for k in range(1, points + 1)}
