import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes

from lib.chapter04.sequence import iterate_map
from lib.chapter12.plot import (
    plot_golden_rule,
    plot_linear_recurrence_paths,
    plot_solow_convergence,
)
from lib.chapter12.solow import (
    solow_capital_path,
    solow_steady_state_capital,
    solow_steady_state_consumption,
)

ALPHA = 1 / 3


def _series(ax: Axes, label: str) -> tuple[list[float], list[float]]:
    line = next(x for x in ax.lines if x.get_label() == label)
    xs = np.asarray(line.get_xdata(), dtype=float).tolist()
    ys = np.asarray(line.get_ydata(), dtype=float).tolist()
    return xs, ys


def test_資本の収束の図は初期値ごとの経路と定常状態の水平の点線() -> None:
    ax = plot_solow_convergence([1, 12], 0.3, ALPHA, 0.1, 40).axes[0]
    for start in (1, 12):
        xs, ys = _series(ax, f"k(0) = {start}")
        assert xs == list(range(41))
        assert ys == pytest.approx(solow_capital_path(start, 0.3, ALPHA, 0.1, 40))
    line = next(x for x in ax.lines if x.get_label() == "Steady state")
    xs, ys = _series(ax, "Steady state")
    assert (xs[0], xs[-1]) == (0, 40)
    assert ys == pytest.approx([solow_steady_state_capital(0.3, ALPHA, 0.1)] * 2)
    assert line.get_linestyle() == ":"
    assert ax.get_xlabel() == "Period t"
    assert ax.get_ylabel() == "Capital per worker k"
    assert ax.get_legend() is not None
    plt.close("all")


def test_黄金律の図は貯蓄率ごとの定常状態の消費と頂点() -> None:
    savings = [0.1, 0.2, 0.3, 0.5, 0.8]
    ax = plot_golden_rule(0.4, 0.05, savings).axes[0]
    xs, ys = _series(ax, "Steady-state consumption")
    assert xs == pytest.approx(savings)
    assert ys == pytest.approx(
        [solow_steady_state_consumption(s, 0.4, 0.05) for s in savings]
    )
    xs, ys = _series(ax, "Golden rule (s = alpha)")
    assert xs == pytest.approx([0.4])
    assert ys == pytest.approx([solow_steady_state_consumption(0.4, 0.4, 0.05)])
    assert ys[0] >= max(_series(ax, "Steady-state consumption")[1])
    assert ax.get_xlabel() == "Saving rate s"
    assert ax.get_ylabel() == "Steady-state consumption c*"
    assert ax.get_legend() is not None
    plt.close("all")


def test_図には初期値や貯蓄率が1つ以上必要() -> None:
    with pytest.raises(ValueError):
        plot_solow_convergence([], 0.3, ALPHA, 0.1, 40)
    with pytest.raises(ValueError):
        plot_golden_rule(ALPHA, 0.1, [])


def test_漸化式の経路の図はaごとの反復の列() -> None:
    ax = plot_linear_recurrence_paths([0.9, 1, 1.1], 1, 0, 25).axes[0]
    for a in (0.9, 1, 1.1):
        xs, ys = _series(ax, f"a = {a:g}")
        assert xs == list(range(26))
        assert ys == pytest.approx(iterate_map(a, 1, 0, 25))
    assert ax.get_xlabel() == "Period t"
    assert ax.get_ylabel() == "x(t)"
    assert ax.get_legend() is not None
    with pytest.raises(ValueError):
        plot_linear_recurrence_paths([], 1, 0, 25)
    plt.close("all")
