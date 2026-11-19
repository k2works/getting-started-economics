"""第 14 章: 線形確率モデル・ロジット・プロビットの曲線の図のテスト。"""

from typing import Any

import numpy as np
import pytest

from lib.chapter14.discrete import draw_binary_sample, fit_binary
from lib.chapter14.plot import plot_probability_curves


def xs(line: Any) -> list[float]:
    values: Any = line.get_xdata()
    return [float(v) for v in values]


def ys(line: Any) -> list[float]:
    values: Any = line.get_ydata()
    return [float(v) for v in values]


def test_データと3つの曲線() -> None:
    s = draw_binary_sample(300, "logit", np.random.default_rng(0))
    ax = plot_probability_curves(s["x1"].to_numpy(), s["y"].to_numpy()).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Data",
        "Linear probability",
        "Logit",
        "Probit",
    ]
    assert ys(ax.lines[0]) == s["y"].tolist()


def test_ロジットとプロビットの曲線は0と1の間で単調に増える() -> None:
    s = draw_binary_sample(300, "logit", np.random.default_rng(0))
    ax = plot_probability_curves(s["x1"].to_numpy(), s["y"].to_numpy()).axes[0]
    for line in (ax.lines[2], ax.lines[3]):
        values = ys(line)
        assert min(values) > 0
        assert max(values) < 1
        assert values == sorted(values)


def test_ロジットの曲線は最尤推定の確率() -> None:
    s = draw_binary_sample(300, "logit", np.random.default_rng(0))
    x, y = s["x1"].to_numpy(), s["y"].to_numpy()
    ax = plot_probability_curves(x, y).axes[0]
    fit = fit_binary(y, x, "logit")
    grid = xs(ax.lines[2])
    expected = 1 / (
        1
        + np.exp(-(fit.coefficients["const"] + fit.coefficients["x1"] * np.array(grid)))
    )
    assert ys(ax.lines[2]) == pytest.approx(expected)


def test_線形確率モデルの直線は範囲の外に出る() -> None:
    s = draw_binary_sample(300, "logit", np.random.default_rng(0))
    ax = plot_probability_curves(s["x1"].to_numpy(), s["y"].to_numpy()).axes[0]
    values = ys(ax.lines[1])
    assert max(values) > 1 or min(values) < 0


def test_曲線の範囲はデータの範囲の両側に1ずつ広げる() -> None:
    s = draw_binary_sample(300, "logit", np.random.default_rng(0))
    x = s["x1"].to_numpy()
    ax = plot_probability_curves(x, s["y"].to_numpy()).axes[0]
    grid = xs(ax.lines[2])
    assert grid[0] == pytest.approx(x.min() - 1)
    assert grid[-1] == pytest.approx(x.max() + 1)
    assert len(grid) == 100


def test_軸の名前() -> None:
    s = draw_binary_sample(100, "logit", np.random.default_rng(0))
    ax = plot_probability_curves(s["x1"].to_numpy(), s["y"].to_numpy()).axes[0]
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "P(y = 1)"
