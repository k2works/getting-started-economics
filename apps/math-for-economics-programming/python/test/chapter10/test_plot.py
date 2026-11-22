import math
from fractions import Fraction

import numpy as np
import pytest
from matplotlib.axes import Axes

from lib.chapter10.bayes import bayes_posteriors
from lib.chapter10.plot import plot_bayes_update, plot_certainty_equivalent

HALF = Fraction(1, 2)
PRIORS = {"Disease": Fraction(1, 100), "Healthy": Fraction(99, 100)}
LIKELIHOODS = {"Disease": Fraction(9, 10), "Healthy": Fraction(5, 100)}


def _series(ax: Axes, label: str) -> tuple[list[float], list[float]]:
    line = next(x for x in ax.lines if x.get_label() == label)
    xs = np.asarray(line.get_xdata(), dtype=float).tolist()
    ys = np.asarray(line.get_ydata(), dtype=float).tolist()
    return xs, ys


def test_ベイズの図は事前確率と事後確率の棒を重ならずに左右に並べる() -> None:
    ax = plot_bayes_update(PRIORS, LIKELIHOODS).axes[0]
    prior, posterior = ax.containers
    assert [b.get_height() for b in prior] == pytest.approx([0.01, 0.99])
    expected = [float(p) for p in bayes_posteriors(PRIORS, LIKELIHOODS).values()]
    assert [b.get_height() for b in posterior] == pytest.approx(expected)
    labels = [prior.get_label(), posterior.get_label()]
    assert labels == ["Prior", "Posterior (after a positive test)"]
    for left, right in zip(prior, posterior, strict=True):
        assert left.get_x() + left.get_width() <= right.get_x() + 1e-9
    assert [t.get_text() for t in ax.get_xticklabels()] == ["Disease", "Healthy"]
    # 確率の軸は 0 から始まり、1 の棒の上に値の文字が入る余白がある
    assert ax.get_ylim()[0] == 0 and ax.get_ylim()[1] > 1


def test_確実性等価の図は効用曲線と弦と確実性等価と危険プレミアムを描く() -> None:
    ax = plot_certainty_equivalent({16: HALF, 100: HALF}, math.sqrt).axes[0]
    xs, ys = _series(ax, "Utility u(x)")
    assert ys == pytest.approx([math.sqrt(x) for x in xs])
    assert (xs[0], xs[-1]) == pytest.approx((16, 100))
    assert _series(ax, "Mixes of the two prizes") == ([16, 100], [4, 10])
    assert _series(ax, "Expected value, expected utility") == ([58], [7])
    for label, points in [
        ("Certainty equivalent", [49, 7]),
        ("Risk premium", [49, 58, 7, 7]),
        ("Utility of the expected value", [58, math.sqrt(58)]),
    ]:
        xs, ys = _series(ax, label)
        assert xs + ys == pytest.approx(points)


def test_確実性等価の図は賞金が2つの賭けだけ() -> None:
    three = {9: Fraction(1, 3), 36: Fraction(1, 3), 81: Fraction(1, 3)}
    with pytest.raises(ValueError):
        plot_certainty_equivalent(three, math.sqrt)
    with pytest.raises(ValueError):
        plot_certainty_equivalent({40: Fraction(1)}, math.sqrt)
