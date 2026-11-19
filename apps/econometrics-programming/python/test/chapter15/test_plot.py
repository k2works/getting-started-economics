"""第 15 章: 打ち切られたデータと、OLS・トービットの直線の図のテスト。"""

from typing import Any

import numpy as np
import pytest

from lib.chapter03.multiple import fit_ols
from lib.chapter15.limited import censor, draw_latent_sample, fit_tobit
from lib.chapter15.plot import plot_censored_data


def data() -> tuple[np.ndarray, np.ndarray]:
    x, latent = draw_latent_sample(2000, np.random.default_rng(0))
    return x, censor(latent)


def xs(line: Any) -> list[float]:
    values: Any = line.get_xdata()
    return [float(v) for v in values]


def ys(line: Any) -> list[float]:
    values: Any = line.get_ydata()
    return [float(v) for v in values]


def slope(line: Any) -> float:
    x, y = xs(line), ys(line)
    return (y[1] - y[0]) / (x[1] - x[0])


def test_データと3本の直線() -> None:
    x, y = data()
    ax = plot_censored_data(x, y).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Data",
        "True line",
        "OLS",
        "Tobit",
    ]
    assert ys(ax.lines[0]) == y.tolist()


def test_真の直線の傾きは2でOLSは偏りトービットは真の値に近い() -> None:
    x, y = data()
    ax = plot_censored_data(x, y).axes[0]
    assert slope(ax.lines[1]) == pytest.approx(2)
    assert slope(ax.lines[2]) == pytest.approx(fit_ols(y, x).coefficients["x1"])
    assert slope(ax.lines[3]) == pytest.approx(fit_tobit(y, x).coefficients["x1"])
    assert slope(ax.lines[2]) < slope(ax.lines[3])


def test_軸の名前() -> None:
    x, y = data()
    ax = plot_censored_data(x, y).axes[0]
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y (censored at 0)"
