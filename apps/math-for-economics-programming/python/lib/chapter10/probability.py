"""確率を、分数（Fraction）で厳密に扱う。標本空間・事象・条件付き確率・独立。"""

import itertools
from collections.abc import Callable, Set
from fractions import Fraction


def dice_sample_space(dice: int = 2, faces: int = 6) -> frozenset[tuple[int, ...]]:
    """サイコロ dice 個の目の組の集合（標本空間）。2 個なら 6 × 6 = 36 通り。"""
    if dice < 1 or faces < 1:
        raise ValueError("サイコロの個数と面の数は、1 以上でなければなりません")
    return frozenset(itertools.product(range(1, faces + 1), repeat=dice))


def outcomes_where[T](space: Set[T], condition: Callable[[T], bool]) -> frozenset[T]:
    """標本空間のうち、条件を満たす結果の集合（事象）。"""
    return frozenset(o for o in space if condition(o))


def equally_likely_probability[T](event: Set[T], space: Set[T]) -> Fraction:
    """どの結果も同じ確からしさのとき、P(A) = A の結果の数 ÷ 標本空間の結果の数。"""
    if not space:
        raise ValueError("標本空間が空では、確率は決まりません")
    if not event <= space:
        raise ValueError("事象は、標本空間の部分集合でなければなりません")
    return Fraction(len(event), len(space))


def conditional_probability[T](event: Set[T], given: Set[T], space: Set[T]) -> Fraction:
    """B が起きたと分かったときの A の確率 P(A|B) = P(A∩B) ÷ P(B)。"""
    p_given = equally_likely_probability(given, space)
    if p_given == 0:
        raise ValueError("確率 0 の事象を、条件にはできません")
    return equally_likely_probability(event & given, space) / p_given


def are_independent_events[T](a: Set[T], b: Set[T], space: Set[T]) -> bool:
    """A と B が独立か（P(A∩B) = P(A)·P(B)）。分数なので、== で厳密に比べられる。"""
    p_both = equally_likely_probability(a & b, space)
    p_a = equally_likely_probability(a, space)
    return p_both == p_a * equally_likely_probability(b, space)


def require_probability(p: Fraction) -> None:
    """確率は 0 以上 1 以下。外れていれば ValueError。"""
    if not 0 <= p <= 1:
        raise ValueError(f"確率は 0 以上 1 以下でなければなりません: {p}")
