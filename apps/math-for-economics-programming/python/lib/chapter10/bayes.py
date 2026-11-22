"""ベイズの定理。検査の結果から、病気である確率を更新する（分数で厳密に）。"""

from collections.abc import Mapping
from fractions import Fraction

from lib.chapter10.probability import require_probability


def bayes_posteriors[K](
    priors: Mapping[K, Fraction], likelihoods: Mapping[K, Fraction]
) -> dict[K, Fraction]:
    """事後確率 P(H|E) = P(H)·P(E|H) ÷ Σ P(H')·P(E|H')（H は仮説、E は観測）。"""
    if priors.keys() != likelihoods.keys():
        raise ValueError("事前確率と尤度は、同じ仮説について与えます")
    for p in [*priors.values(), *likelihoods.values()]:
        require_probability(p)
    if sum(priors.values()) != 1:
        raise ValueError("事前確率の和は、1 でなければなりません")
    joint = {h: priors[h] * likelihoods[h] for h in priors}
    evidence = sum(joint.values(), Fraction(0))
    if evidence == 0:
        raise ValueError("観測の確率が 0 では、更新できません")
    return {h: p / evidence for h, p in joint.items()}


def positive_test_probability(
    prevalence: Fraction, sensitivity: Fraction, false_positive_rate: Fraction
) -> Fraction:
    """陽性になる確率（全確率の公式）。病気の人の陽性 ＋ 健康な人の陽性（偽陽性）。"""
    for p in (prevalence, sensitivity, false_positive_rate):
        require_probability(p)
    return prevalence * sensitivity + (1 - prevalence) * false_positive_rate


def disease_probability_given_positive(
    prevalence: Fraction, sensitivity: Fraction, false_positive_rate: Fraction
) -> Fraction:
    """陽性のとき病気である確率 P(病気|陽性) = P(病気)·P(陽性|病気) ÷ P(陽性)。"""
    positive = positive_test_probability(prevalence, sensitivity, false_positive_rate)
    if positive == 0:
        raise ValueError("陽性になる確率が 0 では、決まりません")
    return prevalence * sensitivity / positive
