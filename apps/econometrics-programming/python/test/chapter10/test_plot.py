"""第 10 章: 個人ごとの直線と、推定値の比較の図のテスト。"""

from typing import Any

import numpy as np
import pytest

from lib.chapter09.did import draw_panel
from lib.chapter10.panel import estimator_comparison, fixed_effects
from lib.chapter10.plot import plot_entity_lines, plot_estimate_comparison


def ys(line: Any) -> list[float]:
    values: Any = line.get_ydata()
    return [float(v) for v in values]


def xs(line: Any) -> list[float]:
    values: Any = line.get_xdata()
    return [float(v) for v in values]


def test_個人ごとのデータと直線とプーリングの直線() -> None:
    panel = draw_panel(8, 5, 1.0, np.random.default_rng(0))
    ax = plot_entity_lines(panel, entities=3).axes[0]
    labels = [line.get_label() for line in ax.lines]
    assert labels == [
        "Entity 0",
        "_fit",
        "Entity 1",
        "_fit",
        "Entity 2",
        "_fit",
        "Pooled OLS",
    ]


def test_個人ごとの直線の傾きは固定効果の傾き() -> None:
    panel = draw_panel(8, 5, 1.0, np.random.default_rng(0))
    beta = fixed_effects(panel, "y", ["x"]).coefficients["x"]
    ax = plot_entity_lines(panel, entities=2).axes[0]
    for line in (ax.lines[1], ax.lines[3]):
        x, y = xs(line), ys(line)
        assert (y[1] - y[0]) / (x[1] - x[0]) == pytest.approx(beta)


def test_個人ごとの直線は個人の平均の点を通る() -> None:
    panel = draw_panel(8, 5, 1.0, np.random.default_rng(0))
    ax = plot_entity_lines(panel, entities=2).axes[0]
    for entity, line in ((0, ax.lines[1]), (1, ax.lines[3])):
        data = panel[panel["entity"] == entity]
        at_mean = np.interp(data["x"].mean(), xs(line), ys(line))
        assert at_mean == pytest.approx(data["y"].mean())


def test_プーリングの直線の傾きはプーリングの推定値() -> None:
    panel = draw_panel(8, 5, 1.0, np.random.default_rng(0))
    ax = plot_entity_lines(panel, entities=3).axes[0]
    x, y = xs(ax.lines[-1]), ys(ax.lines[-1])
    shown = panel[panel["entity"] < 3]
    expected = np.polyfit(shown["x"], shown["y"], 1)[0]
    assert (y[1] - y[0]) / (x[1] - x[0]) == pytest.approx(expected)
    assert ax.lines[-1].get_linestyle() == "--"


def test_推定値の比較の図は3つのヒストグラムと真の値の線() -> None:
    table = estimator_comparison(50, 3, 1.0, 30, np.random.default_rng(0))
    ax = plot_estimate_comparison(table, 1.0).axes[0]
    assert len(ax.patches) == 3 * 20
    assert [line.get_label() for line in ax.lines] == ["True value"]
    legend = ax.get_legend()
    assert legend is not None
    assert [t.get_text() for t in legend.get_texts()] == [
        "pooled",
        "fixed_effects",
        "random_effects",
        "True value",
    ]


def test_軸の名前() -> None:
    table = estimator_comparison(50, 3, 1.0, 30, np.random.default_rng(0))
    ax = plot_estimate_comparison(table, 1.0).axes[0]
    assert ax.get_xlabel() == "Estimated slope"
    assert ax.get_ylabel() == "Frequency"
    ax2 = plot_entity_lines(draw_panel(8, 5, 1.0, np.random.default_rng(0)), 3).axes[0]
    assert ax2.get_xlabel() == "x"
    assert ax2.get_ylabel() == "y"
