"""アニメーション（lib/animations）のテスト。

フレームごとのデータは、各章の関数と一致すること。GIF の保存は、全フレームを描くので、
更新の関数が動くことの確認になる。乱数を使うものは、種を固定して、同じ結果を再現する。
"""

from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest
from matplotlib.animation import FuncAnimation

from lib.animations.common import histogram_heights, linear_values
from lib.animations.endogenous import (
    animate_likelihood,
    animate_omitted_variable,
    animate_weak_instrument,
    likelihood_frames,
    omitted_frames,
    weak_instrument_frames,
)
from lib.animations.inference import (
    animate_confidence_intervals,
    animate_consistency,
    consistency_frames,
    coverage_frames,
)
from lib.animations.regression import (
    animate_collinearity,
    animate_outlier,
    collinearity_frames,
    outlier_frames,
)
from lib.chapter02.simple import draw_sample, fit_simple
from lib.chapter03.multiple import multicollinearity_experiment
from lib.chapter05.inference import slope_intervals
from lib.chapter06.asymptotics import consistency_experiment
from lib.chapter11.endogeneity import simulate_omitted
from lib.chapter12.iv import weak_instrument_experiment
from lib.chapter14.discrete import (
    draw_binary_sample,
    fit_binary,
    log_likelihood,
    predicted_probabilities,
)


def test_等間隔の値は両端を含む() -> None:
    assert linear_values(0, 10, 5) == [0, 2.5, 5, 7.5, 10]
    assert linear_values(4, 1, 4) == [4, 3, 2, 1]


def test_フレーム数は2以上() -> None:
    with pytest.raises(ValueError, match="フレーム数"):
        linear_values(0, 1, 1)


def test_棒の高さは割合で合計が1になる() -> None:
    heights = histogram_heights([0.5, 0.5, 1.5, 2.5], np.array([0.0, 1.0, 2.0, 3.0]))
    assert heights == [0.5, 0.25, 0.25]


def test_外れ値が動くと回帰直線が動く() -> None:
    data = outlier_frames(20, 2.5, -4.0, 5, 0)
    assert [f.outlier_y for f in data] == linear_values(1.0 + 0.5 * 2.5, -4.0, 5)
    x, y = draw_sample(20, 1.0, 0.5, 1.0, np.random.default_rng(0))
    assert len(data[0].x) == 21
    assert data[0].fit == fit_simple(data[0].x, data[0].y)
    assert data[0].x[-1] == 2.5
    assert list(data[0].x[:-1]) == list(x)
    assert data[-1].y[-1] == -4.0
    assert list(data[-1].y[:-1]) == list(y)
    slopes = [f.fit.slope for f in data]
    assert slopes == sorted(slopes, reverse=True)
    assert slopes[0] - slopes[-1] > 0.5


def test_相関が高いほど係数の推定値がばらつく() -> None:
    data = collinearity_frames([0.0, 0.9], 50, 100, 0)
    assert [f.correlation for f in data] == [0.0, 0.9]
    expected = multicollinearity_experiment(0.9, 50, 100, np.random.default_rng(0))
    assert data[1].estimates.equals(expected)
    assert data[1].estimates["x1"].std() > 2 * data[0].estimates["x1"].std()


def test_信頼区間のフレームは累計の被覆を数える() -> None:
    data = coverage_frames(30, 20, 0.95, 0)
    table = slope_intervals(30, 20, 0.95, np.random.default_rng(0))
    assert [f.lower for f in data] == list(table["lower"])
    assert [f.upper for f in data] == list(table["upper"])
    contains = [bool(f.lower <= 0.5 <= f.upper) for f in data]
    assert [f.contains for f in data] == contains
    assert [f.covered for f in data] == list(np.cumsum(contains))


def test_標本が大きいほど傾きの推定値が真の値に集まる() -> None:
    data = consistency_frames([20, 200], 100, 0)
    expected = consistency_experiment([20, 200], 100, np.random.default_rng(0))
    assert [f.size for f in data] == [20, 200]
    assert list(data[0].slopes) == list(expected[20])
    assert data[1].slopes.std() < data[0].slopes.std() / 2


def test_欠落変数のフレームは相関に応じた偏り() -> None:
    data = omitted_frames([0.0, 0.8], 100, 50, 0)
    expected = simulate_omitted(100, 0.8, 50, np.random.default_rng(0))
    assert data[1].estimates.equals(expected)
    assert data[0].estimates["short"].mean() == pytest.approx(1, abs=0.2)
    assert data[1].estimates["short"].mean() == pytest.approx(2.6, abs=0.3)
    assert data[1].estimates["long"].mean() == pytest.approx(1, abs=0.3)


def test_操作変数が弱いほどIVの推定値が広がる() -> None:
    data = weak_instrument_frames([1.0, 0.1], 100, 100, 0)
    expected = weak_instrument_experiment(100, 0.1, 100, np.random.default_rng(0))
    assert [f.strength for f in data] == [1.0, 0.1]
    assert data[1].estimates.equals(expected)
    assert data[1].estimates["iv"].std() > 5 * data[0].estimates["iv"].std()


def test_尤度のフレームは傾きを動かして対数尤度を求める() -> None:
    data = likelihood_frames(100, 5, 0)
    sample = draw_binary_sample(100, "logit", np.random.default_rng(0))
    x, y = sample["x1"].to_numpy(), sample["y"].to_numpy()
    fit = fit_binary(y, x, "logit")
    slopes = [f.slope for f in data]
    assert slopes[0] == 0
    assert slopes[-1] > fit.coefficients["x1"]
    best = max(data, key=lambda f: f.log_likelihood)
    assert abs(best.slope - fit.coefficients["x1"]) <= slopes[1] - slopes[0]
    design = np.column_stack([np.ones(len(x)), x])
    beta = np.array([fit.coefficients["const"], data[2].slope])
    assert data[2].log_likelihood == pytest.approx(
        log_likelihood("logit", y, design, beta)
    )
    assert data[0].log_likelihood < best.log_likelihood
    assert data[2].curve[0] == pytest.approx(
        1 / (1 + np.exp(-(beta[0] + beta[1] * data[2].grid[0])))
    )
    assert data[2].curve.shape == data[2].grid.shape
    flat = 1 / (1 + np.exp(-fit.coefficients["const"]))
    assert data[0].curve == pytest.approx(np.full(len(data[0].grid), flat))
    assert predicted_probabilities(fit, data[0].grid)[0] != pytest.approx(flat)


BUILDERS: dict[str, Callable[[], FuncAnimation]] = {
    "outlier": lambda: animate_outlier(frames=3),
    "collinearity": lambda: animate_collinearity(repetitions=20, frames=3),
    "intervals": lambda: animate_confidence_intervals(repetitions=5),
    "consistency": lambda: animate_consistency(sizes=[20, 50], repetitions=20),
    "omitted": lambda: animate_omitted_variable(repetitions=20, frames=3),
    "weak": lambda: animate_weak_instrument(repetitions=20, frames=3),
    "likelihood": lambda: animate_likelihood(frames=3),
}


@pytest.mark.parametrize("name", sorted(BUILDERS))
def test_アニメーションをGIFに保存できる(name: str, tmp_path: Path) -> None:
    animation = BUILDERS[name]()
    assert isinstance(animation, FuncAnimation)
    path = tmp_path / f"{name}.gif"
    animation.save(path, writer="pillow", fps=5, dpi=30)
    assert path.read_bytes()[:6] == b"GIF89a"
