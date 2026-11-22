"""ベイズの更新（事前確率と事後確率の棒）と、効用関数の凹と確実性等価の図。"""

from collections.abc import Mapping
from fractions import Fraction

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from lib.chapter10.bayes import bayes_posteriors
from lib.chapter10.expectation import discrete_expected_value
from lib.chapter10.risk import (
    UtilityFunction,
    certainty_equivalent_of_lottery,
    expected_utility_of_lottery,
)


def plot_bayes_update(
    priors: Mapping[str, Fraction], likelihoods: Mapping[str, Fraction]
) -> Figure:
    """仮説ごとに、事前確率と、観測のあとの事後確率の棒を並べる。"""
    posteriors = bayes_posteriors(priors, likelihoods)
    names = list(priors)
    positions = np.arange(len(names))
    fig, ax = plt.subplots()
    for shift, label, values in [
        (-0.2, "Prior", priors),
        (0.2, "Posterior (after a positive test)", posteriors),
    ]:
        heights = [float(values[n]) for n in names]
        bars = ax.bar(positions + shift, heights, width=0.4, label=label)
        ax.bar_label(bars, fmt="%.3f", fontsize="small")
    ax.set_xticks(positions, names)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Probability")
    ax.legend(fontsize="small")
    plt.close(fig)
    return fig


def plot_certainty_equivalent[V: int | Fraction](
    lottery: Mapping[V, Fraction], utility: UtilityFunction
) -> Figure:
    """賞金が 2 つの賭けの、効用曲線・賞金を結ぶ弦・確実性等価・危険プレミアム。"""
    if len(lottery) != 2:
        raise ValueError("この図は、賞金が 2 つの賭けだけを描きます")
    low, high = float(min(lottery)), float(max(lottery))
    mean = float(discrete_expected_value(lottery))
    expected = expected_utility_of_lottery(lottery, utility)
    certain = certainty_equivalent_of_lottery(lottery, utility)
    xs = np.linspace(low, high, 101).tolist()
    fig, ax = plt.subplots()
    ax.plot(xs, [utility(x) for x in xs], label="Utility u(x)")
    ax.plot(
        [low, high],
        [utility(low), utility(high)],
        "--",
        label="Mixes of the two prizes",
    )
    ax.plot([certain, mean], [expected, expected], ":", lw=3, label="Risk premium")
    ax.plot([mean], [expected], "o", label="Expected value, expected utility")
    ax.plot([certain], [expected], "s", label="Certainty equivalent")
    ax.plot([mean], [utility(mean)], "^", label="Utility of the expected value")
    ax.set_xlabel("Money x")
    ax.set_ylabel("Utility")
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig
