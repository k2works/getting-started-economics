import numpy as np
import pytest
from matplotlib.axes import Axes

from lib.chapter02.monopoly import cournot_outcome, monopoly_profit
from lib.chapter02.plot import plot_cournot_convergence, plot_monopoly_profit


def _line(ax: Axes, label: str) -> tuple[list[float], list[float]]:
    line = next(x for x in ax.lines if x.get_label() == label)
    xs = np.asarray(line.get_xdata(), dtype=float).tolist()
    ys = np.asarray(line.get_ydata(), dtype=float).tolist()
    return xs, ys


def test_利潤の放物線は数量0と競争の数量で利潤0() -> None:
    ax = plot_monopoly_profit(100, 2, 20).axes[0]
    xs, ys = _line(ax, "Profit")
    assert (xs[0], ys[0]) == (0, 0)
    assert xs[-1] == 40
    assert ys[-1] == pytest.approx(0)


def test_利潤の放物線の各点は利潤の式の値() -> None:
    ax = plot_monopoly_profit(100, 2, 20).axes[0]
    xs, ys = _line(ax, "Profit")
    assert ys == pytest.approx([monopoly_profit(q, 100, 2, 20) for q in xs])


def test_頂点の点は放物線の最大値() -> None:
    ax = plot_monopoly_profit(100, 1, 20).axes[0]
    assert _line(ax, "Monopoly optimum") == ([40], [1600])
    assert max(_line(ax, "Profit")[1]) == pytest.approx(1600)


def test_利潤の図の軸と凡例() -> None:
    ax = plot_monopoly_profit(100, 1, 20).axes[0]
    assert (ax.get_xlabel(), ax.get_ylabel()) == ("Quantity", "Profit")
    assert ax.get_legend() is not None
    assert ax.get_xlim()[0] == 0
    assert ax.get_ylim()[0] == 0


def test_企業の数ごとの総数量と価格() -> None:
    ax = plot_cournot_convergence(100, 1, 20, 10).axes[0]
    xs, quantities = _line(ax, "Total quantity")
    assert xs == list(range(1, 11))
    expected = [cournot_outcome(n, 100, 1, 20) for n in range(1, 11)]
    assert quantities == pytest.approx([r.quantity for r in expected])
    assert _line(ax, "Price")[1] == pytest.approx([r.price for r in expected])
    assert ax.get_xlabel() == "Number of firms"
    assert ax.get_legend() is not None
    assert ax.get_ylim()[0] == 0


def test_完全競争の数量と費用を水平の点線で引く() -> None:
    ax = plot_cournot_convergence(100, 2, 20, 5).axes[0]
    assert _line(ax, "Competitive quantity") == ([1, 5], [40, 40])
    assert _line(ax, "Unit cost") == ([1, 5], [20, 20])
    for label in ["Competitive quantity", "Unit cost"]:
        line = next(x for x in ax.lines if x.get_label() == label)
        assert line.get_linestyle() in ("--", ":")
