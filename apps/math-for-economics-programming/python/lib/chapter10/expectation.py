"""確率変数の分布・期待値・分散を、分数（Fraction）で厳密に計算する。"""

from collections.abc import Callable, Collection, Mapping, Set
from fractions import Fraction

from lib.chapter10.probability import equally_likely_probability, require_probability


def random_variable_distribution[T](
    space: Set[T], value: Callable[[T], int | Fraction]
) -> dict[int | Fraction, Fraction]:
    """均等確率の標本空間の、各結果に値を割り当てた確率変数の分布（値 → 確率）。"""
    groups: dict[int | Fraction, set[T]] = {}
    for outcome in space:
        groups.setdefault(value(outcome), set()).add(outcome)
    return {v: equally_likely_probability(e, space) for v, e in groups.items()}


def require_probability_distribution(probabilities: Collection[Fraction]) -> None:
    """分布の確率は、どれも 0 以上 1 以下で、合計がちょうど 1。違えば ValueError。"""
    if not probabilities:
        raise ValueError("空の分布は、扱えません")
    for p in probabilities:
        require_probability(p)
    if sum(probabilities) != 1:
        raise ValueError("確率の合計は、1 でなければなりません")


def discrete_expected_value[V: int | Fraction](
    distribution: Mapping[V, Fraction],
) -> Fraction:
    """期待値 E[X] = Σ x·P(X = x)。分布は、値 → その値をとる確率の辞書。"""
    require_probability_distribution(distribution.values())
    return sum((x * p for x, p in distribution.items()), Fraction(0))


def discrete_variance[V: int | Fraction](
    distribution: Mapping[V, Fraction],
) -> Fraction:
    """分散 Var[X] = E[(X − E[X])²]。期待値からのずれの 2 乗の期待値。"""
    mean = discrete_expected_value(distribution)
    return sum(((x - mean) ** 2 * p for x, p in distribution.items()), Fraction(0))
