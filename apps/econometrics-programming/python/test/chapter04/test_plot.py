"""第 4 章: 診断図と、要約統計量が同じで形が違うデータの図のテスト。"""

from typing import Any

import numpy as np
import pytest

from lib.chapter03.multiple import fit_ols, leverage
from lib.chapter04.diagnostics import (
    qq_points,
    same_summary_datasets,
    standardized_residuals,
)
from lib.chapter04.plot import plot_diagnostics, plot_same_summary


def data() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(0)
    x = rng.standard_normal(30)
    return x, 1 + 2 * x + rng.standard_normal(30)


def ys(line: Any) -> list[float]:
    values: Any = line.get_ydata()
    return [float(v) for v in values]


def xs(line: Any) -> list[float]:
    values: Any = line.get_xdata()
    return [float(v) for v in values]


def test_診断図は4つの枠を持つ() -> None:
    x, y = data()
    fig = plot_diagnostics(y, x)
    assert len(fig.axes) == 4
    assert [ax.get_title() for ax in fig.axes] == [
        "Residuals vs Fitted",
        "Normal Q-Q",
        "Scale-Location",
        "Residuals vs Leverage",
    ]


def test_残差と当てはめ値の図は残差を描き0の線を引く() -> None:
    x, y = data()
    ax = plot_diagnostics(y, x).axes[0]
    result = fit_ols(y, x)
    assert ys(ax.lines[0]) == pytest.approx(result.residuals)
    assert xs(ax.lines[0]) == pytest.approx(y - result.residuals)
    assert ys(ax.lines[1]) == [0, 0]


def test_Q_Qの図は点と基準線() -> None:
    x, y = data()
    ax = plot_diagnostics(y, x).axes[1]
    theoretical, ordered = qq_points(fit_ols(y, x).residuals)
    assert xs(ax.lines[0]) == pytest.approx(theoretical)
    assert ys(ax.lines[0]) == pytest.approx(ordered)
    assert xs(ax.lines[1]) == ys(ax.lines[1])


def test_スケールの図は標準化残差の絶対値の平方根() -> None:
    x, y = data()
    ax = plot_diagnostics(y, x).axes[2]
    z = standardized_residuals(fit_ols(y, x))
    assert ys(ax.lines[0]) == pytest.approx(np.sqrt(np.abs(z)))


def test_てこ比の図はてこ比を横軸にする() -> None:
    x, y = data()
    ax = plot_diagnostics(y, x).axes[3]
    assert xs(ax.lines[0]) == pytest.approx(leverage(x))
    assert ax.get_xlabel() == "Leverage"


def test_同じ要約統計量の図は4つの枠と直線を持つ() -> None:
    datasets = same_summary_datasets()
    fig = plot_same_summary(datasets)
    assert [ax.get_title() for ax in fig.axes] == list(datasets)
    for ax, (x, y) in zip(fig.axes, datasets.values(), strict=True):
        assert [line.get_label() for line in ax.lines] == ["Data", "Fitted line"]
        assert ys(ax.lines[0]) == pytest.approx(y)
        assert ys(ax.lines[1])[0] == pytest.approx(
            7.5 - 0.8 * 2 / 3.3 * 9 + 0.8 * 2 / 3.3 * min(x)
        )
