import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter09.plot import plot_regression_with_residuals, plot_residuals_against_x
from lib.chapter09.regression import simple_regression_coefficients

PRICES = [2, 4, 6, 8, 10]
QUANTITIES = [18, 15, 13, 8, 6]


def _line(ax: Axes, label: str) -> Line2D:
    return next(x for x in ax.lines if x.get_label() == label)


def _series(ax: Axes, label: str) -> tuple[list[float], list[float]]:
    line = _line(ax, label)
    xs = np.asarray(line.get_xdata(), dtype=float).tolist()
    ys = np.asarray(line.get_ydata(), dtype=float).tolist()
    return xs, ys


def _residual_segments(ax: Axes) -> list[Line2D]:
    return [x for x in ax.lines if x.get_gid() == "residual"]


def test_回帰の図はデータの点を描く() -> None:
    ax = plot_regression_with_residuals(PRICES, QUANTITIES).axes[0]
    assert _series(ax, "Data") == (PRICES, QUANTITIES)


def test_回帰直線はxの最小から最大まで当てはめた値を結ぶ() -> None:
    ax = plot_regression_with_residuals(PRICES, QUANTITIES).axes[0]
    xs, ys = _series(ax, "Regression line")
    assert xs == pytest.approx([2, 10])
    # q = 21.3 − 1.55p
    assert ys == pytest.approx([18.2, 5.8])


def test_残差の線分はデータの点から回帰直線まで縦にのびる() -> None:
    ax = plot_regression_with_residuals(PRICES, QUANTITIES).axes[0]
    segments = _residual_segments(ax)
    assert len(segments) == len(PRICES)
    fitted = [18.2, 15.1, 12, 8.9, 5.8]
    for segment, x, y, f in zip(segments, PRICES, QUANTITIES, fitted, strict=True):
        xs = np.asarray(segment.get_xdata(), dtype=float).tolist()
        ys = np.asarray(segment.get_ydata(), dtype=float).tolist()
        assert xs == [x, x]
        assert ys == pytest.approx([y, f])


def test_残差の線分は凡例に1つだけ載る() -> None:
    ax = plot_regression_with_residuals(PRICES, QUANTITIES).axes[0]
    labels = [str(x.get_label()) for x in _residual_segments(ax)]
    assert labels.count("Residual") == 1
    legend = ax.get_legend()
    assert legend is not None
    shown = [t.get_text() for t in legend.get_texts()]
    assert shown == ["Data", "Regression line", "Residual"]


def test_回帰の図の軸() -> None:
    ax = plot_regression_with_residuals(PRICES, QUANTITIES).axes[0]
    assert ax.get_xlabel() == "Price"
    assert ax.get_ylabel() == "Quantity"


def test_残差の散布図は価格ごとの残差を描く() -> None:
    ax = plot_residuals_against_x(PRICES, QUANTITIES).axes[0]
    xs, ys = _series(ax, "Residuals")
    assert xs == PRICES
    assert ys == pytest.approx([-0.2, -0.1, 1, -0.9, 0.2])


def test_残差を価格に回帰した直線は傾きも切片も0() -> None:
    ax = plot_residuals_against_x(PRICES, QUANTITIES).axes[0]
    xs, ys = _series(ax, "Regression of residuals on price")
    assert xs == pytest.approx([2, 10])
    assert ys == pytest.approx([0, 0], abs=1e-9)
    residuals = _series(ax, "Residuals")[1]
    assert simple_regression_coefficients(PRICES, residuals) == pytest.approx(
        (0, 0), abs=1e-9
    )


def test_残差の散布図の軸と凡例() -> None:
    ax = plot_residuals_against_x(PRICES, QUANTITIES).axes[0]
    assert ax.get_xlabel() == "Price"
    assert ax.get_ylabel() == "Residual"
    legend = ax.get_legend()
    assert legend is not None
    shown = {t.get_text() for t in legend.get_texts()}
    assert shown == {"Residuals", "Regression of residuals on price"}


def test_1点だけでは回帰の図は描けない() -> None:
    with pytest.raises(ValueError):
        plot_regression_with_residuals([3], [5])
    with pytest.raises(ValueError):
        plot_residuals_against_x([3], [5])
