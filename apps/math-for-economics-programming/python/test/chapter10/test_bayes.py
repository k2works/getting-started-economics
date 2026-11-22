from fractions import Fraction

import pytest

from lib.chapter10.bayes import (
    bayes_posteriors,
    disease_probability_given_positive,
    positive_test_probability,
)

PREVALENCE = Fraction(1, 100)
SENSITIVITY = Fraction(9, 10)
FALSE_POSITIVE = Fraction(5, 100)


def test_陽性になる確率は病気の人と健康な人の陽性を足す() -> None:
    p = positive_test_probability(PREVALENCE, SENSITIVITY, FALSE_POSITIVE)
    assert p == Fraction(1, 100) * Fraction(9, 10) + Fraction(99, 100) * Fraction(
        5, 100
    )
    assert p == Fraction(117, 2000)


def test_陽性のとき病気である確率は感度の90パーセントよりずっと低い() -> None:
    p = disease_probability_given_positive(PREVALENCE, SENSITIVITY, FALSE_POSITIVE)
    assert p == Fraction(2, 13)
    assert float(p) == pytest.approx(0.1538, abs=1e-4)
    assert p < SENSITIVITY


def test_事後確率は事前確率かける尤度を全体で割る() -> None:
    priors = {"disease": PREVALENCE, "healthy": 1 - PREVALENCE}
    likelihoods = {"disease": SENSITIVITY, "healthy": FALSE_POSITIVE}
    posteriors = bayes_posteriors(priors, likelihoods)
    assert posteriors == {"disease": Fraction(2, 13), "healthy": Fraction(11, 13)}
    assert sum(posteriors.values()) == 1
    # 2 つの関数（一般の形と、検査の形）が、同じ答えを出す
    assert posteriors["disease"] == disease_probability_given_positive(
        PREVALENCE, SENSITIVITY, FALSE_POSITIVE
    )


def test_2回続けて陽性なら事後確率を事前確率にして更新する() -> None:
    likelihoods = {"disease": SENSITIVITY, "healthy": FALSE_POSITIVE}
    once = bayes_posteriors(
        {"disease": PREVALENCE, "healthy": 1 - PREVALENCE}, likelihoods
    )
    twice = bayes_posteriors(once, likelihoods)
    assert twice["disease"] == Fraction(36, 47)
    assert float(twice["disease"]) == pytest.approx(0.766, abs=1e-3)


def test_仮説が3つでも尤度の比で事後確率が決まる() -> None:
    priors = {"A": Fraction(1, 2), "B": Fraction(3, 10), "C": Fraction(1, 5)}
    likelihoods = {"A": Fraction(1, 10), "B": Fraction(1, 2), "C": Fraction(1, 4)}
    posteriors = bayes_posteriors(priors, likelihoods)
    assert posteriors == {"A": Fraction(1, 5), "B": Fraction(3, 5), "C": Fraction(1, 5)}


def test_有病率が高いほど陽性の意味は大きく0と1では動かない() -> None:
    def posterior(prevalence: Fraction) -> Fraction:
        return disease_probability_given_positive(
            prevalence, SENSITIVITY, FALSE_POSITIVE
        )

    assert posterior(Fraction(1, 10)) == Fraction(2, 3)
    assert posterior(Fraction(0)) == 0
    assert posterior(Fraction(1)) == 1


def test_どの仮説でも尤度が同じなら事後確率は事前確率のまま() -> None:
    priors = {"disease": PREVALENCE, "healthy": 1 - PREVALENCE}
    same = {"disease": Fraction(3, 10), "healthy": Fraction(3, 10)}
    assert bayes_posteriors(priors, same) == priors


def test_確率は0以上1以下で事前確率の和は1() -> None:
    p, s, f = PREVALENCE, SENSITIVITY, FALSE_POSITIVE
    for bad in [Fraction(-1, 10), Fraction(11, 10)]:
        for args in [(bad, s, f), (p, bad, f), (p, s, bad)]:
            with pytest.raises(ValueError):
                disease_probability_given_positive(*args)
    halves = {"A": Fraction(1, 2), "B": Fraction(1, 2)}
    with pytest.raises(ValueError):
        bayes_posteriors({"A": Fraction(1, 2), "B": Fraction(1, 4)}, halves)


def test_仮説がそろい観測の確率が0でないときだけ更新する() -> None:
    with pytest.raises(ValueError):
        bayes_posteriors({"A": Fraction(1)}, {"B": Fraction(1, 2)})
    with pytest.raises(ValueError):
        bayes_posteriors(
            {"A": Fraction(1, 2), "B": Fraction(1, 2)},
            {"A": Fraction(0), "B": Fraction(0)},
        )
    with pytest.raises(ValueError):
        disease_probability_given_positive(Fraction(0), SENSITIVITY, Fraction(0))
