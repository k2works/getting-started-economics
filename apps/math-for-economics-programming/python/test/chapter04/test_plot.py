import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes

from lib.chapter04.plot import plot_bond_prices, plot_partial_sums
from lib.chapter04.sequence import coupon_bond_price, partial_sums


def _series(ax: Axes, label: str) -> tuple[list[float], list[float]]:
    line = next(x for x in ax.lines if x.get_label() == label)
    xs = np.asarray(line.get_xdata(), dtype=float).tolist()
    ys = np.asarray(line.get_ydata(), dtype=float).tolist()
    return xs, ys


def test_部分和の点は項数ごとの部分和() -> None:
    ax = plot_partial_sums(1, 0.5, 10).axes[0]
    xs, ys = _series(ax, "Partial sum")
    assert xs == list(range(1, 11))
    assert ys == pytest.approx(partial_sums(1, 0.5, 10))


def test_無限級数の値は水平の点線() -> None:
    ax = plot_partial_sums(3, 0.25, 6).axes[0]
    line = next(x for x in ax.lines if x.get_label() == "Infinite series")
    xs, ys = _series(ax, "Infinite series")
    assert (xs[0], xs[-1]) == (1, 6)
    assert set(ys) == {4}
    assert line.get_linestyle() == ":"


def test_部分和の図の軸と凡例() -> None:
    ax = plot_partial_sums(1, 0.5, 10).axes[0]
    assert ax.get_xlabel() == "Number of terms"
    assert ax.get_ylabel() == "Sum"
    assert ax.get_legend() is not None
    plt.close("all")


def test_収束しない公比では部分和の図を描かない() -> None:
    with pytest.raises(ValueError):
        plot_partial_sums(1, 1.5, 10)


def test_債券価格の線は利子率ごとの価格で右下がり() -> None:
    rates = [0.01, 0.03, 0.05, 0.07]
    ax = plot_bond_prices(100, 5, 10, rates).axes[0]
    xs, ys = _series(ax, "Bond price")
    assert xs == pytest.approx([1, 3, 5, 7])
    assert ys == pytest.approx([coupon_bond_price(100, 5, r, 10) for r in rates])
    assert all(y1 > y2 for y1, y2 in zip(ys, ys[1:], strict=False))


def test_クーポンの利回りの点で価格は額面() -> None:
    ax = plot_bond_prices(100, 4, 5, [0.02, 0.06]).axes[0]
    xs, ys = _series(ax, "Price = face value")
    assert xs == pytest.approx([4])
    assert ys == pytest.approx([100])


def test_債券価格の図の軸と凡例() -> None:
    ax = plot_bond_prices(100, 5, 10, [0.01, 0.09]).axes[0]
    assert ax.get_xlabel() == "Interest rate (%)"
    assert ax.get_ylabel() == "Bond price"
    assert ax.get_legend() is not None
    plt.close("all")
