import numpy as np
import pytest
from matplotlib.axes import Axes

from lib.chapter07.budget import budget_expenditure
from lib.chapter07.vectors import vector_angle_degrees, vector_length
from lib.chapter08.plot import plot_income_expansion_paths, plot_utility_maximization
from lib.chapter08.utility import cobb_douglas_utility


def _series(ax: Axes, label: str) -> tuple[list[float], list[float]]:
    line = next(x for x in ax.lines if x.get_label() == label)
    xs = np.asarray(line.get_xdata(), dtype=float).tolist()
    ys = np.asarray(line.get_ydata(), dtype=float).tolist()
    return xs, ys


def _labels(ax: Axes) -> list[str]:
    return [str(x.get_label()) for x in ax.lines]


def test_効用最大化の図は予算線と最適点を描く() -> None:
    ax = plot_utility_maximization([3, 4], 120, 0.3).axes[0]
    assert _series(ax, "Budget line") == ([0, 40], [30, 0])
    xs, ys = _series(ax, "Optimum")
    assert (xs, ys) == ([pytest.approx(12)], [pytest.approx(21)])


def test_最適点を通る無差別曲線は予算線に接して予算線より下に出ない() -> None:
    prices = [3, 4]
    ax = plot_utility_maximization(prices, 120, 0.3).axes[0]
    label = next(x for x in _labels(ax) if x.startswith("Indifference curve (U ="))
    xs, ys = _series(ax, label)
    level = cobb_douglas_utility(12, 21, 0.3)
    assert label == f"Indifference curve (U = {level:.2f})"
    for x, y in zip(xs, ys, strict=True):
        assert cobb_douglas_utility(x, y, 0.3) == pytest.approx(level)
        assert budget_expenditure(prices, [x, y]) >= 120 - 1e-9
    # 接点の近くでは、支出が所得にほぼ等しい
    assert min(
        budget_expenditure(prices, [x, y]) for x, y in zip(xs, ys, strict=True)
    ) == (pytest.approx(120, abs=0.1))


def test_効用が7割の無差別曲線は予算線と交わる() -> None:
    ax = plot_utility_maximization([3, 4], 120, 0.3).axes[0]
    xs, ys = _series(ax, "Indifference curve (lower utility)")
    lower = 0.7 * cobb_douglas_utility(12, 21, 0.3)
    assert all(
        cobb_douglas_utility(x, y, 0.3) == pytest.approx(lower)
        for x, y in zip(xs, ys, strict=True)
    )
    spending = [budget_expenditure([3, 4], [x, y]) for x, y in zip(xs, ys, strict=True)]
    assert min(spending) < 120 < max(spending)


def test_効用の勾配の矢印は価格ベクトルと同じ向き() -> None:
    ax = plot_utility_maximization([3, 4], 120, 0.3).axes[0]
    xs, ys = _series(ax, "Gradient of U (same direction as prices)")
    arrow = [xs[1] - xs[0], ys[1] - ys[0]]
    assert (xs[0], ys[0]) == pytest.approx((12, 21))
    assert vector_angle_degrees(arrow, [3, 4]) == pytest.approx(0, abs=1e-4)
    assert vector_length(arrow) == pytest.approx(30 / 4)


def test_効用最大化の図の軸と凡例() -> None:
    ax = plot_utility_maximization([3, 4], 120, 0.3).axes[0]
    assert (ax.get_xlabel(), ax.get_ylabel()) == ("Good x", "Good y")
    assert ax.get_xlim() == pytest.approx((0, 44))
    assert ax.get_ylim() == pytest.approx((0, 45))
    legend = ax.get_legend()
    assert legend is not None
    assert "Optimum" in {t.get_text() for t in legend.get_texts()}


def test_所得を変えた最適点の軌跡はコブダグラス型なら原点を通る直線() -> None:
    fig = plot_income_expansion_paths([1, 2], [8, 16, 24], 0.5, 4)
    xs, ys = _series(fig.axes[0], "Optimal bundles")
    assert xs == pytest.approx([4, 8, 12])
    assert ys == pytest.approx([2, 4, 6])
    assert fig.axes[0].get_title() == "Cobb-Douglas (a = 0.5)"


def test_準線形効用の軌跡は端点を通ってから縦にのびる() -> None:
    fig = plot_income_expansion_paths([1, 2], [8, 16, 24, 32], 0.5, 4)
    xs, ys = _series(fig.axes[1], "Optimal bundles")
    assert xs == pytest.approx([8, 16, 16, 16])
    assert ys == pytest.approx([0, 0, 4, 8])
    assert fig.axes[1].get_title() == "Quasi-linear (U = 4√x + y)"


def test_所得が増えた後の予算線は破線() -> None:
    for ax in plot_income_expansion_paths([1, 2], [8, 16, 24], 0.5, 4).axes:
        budgets = [x for x in ax.lines if x.get_color() == "C0"]
        assert [x.get_label() for x in budgets] == [
            "Budget (income 8)",
            "Budget after income rise",
            "_nolegend_",
        ]
        assert [x.get_linestyle() for x in budgets] == ["-", "--", "--"]
        assert _series(ax, "Budget (income 8)") == ([0, 8], [4, 0])
        assert _series(ax, "_nolegend_") == ([0, 24], [12, 0])
        assert (ax.get_xlabel(), ax.get_ylabel()) == ("Good x", "Good y")
        assert ax.get_legend() is not None


def test_所得の軌跡には所得が1つ以上必要() -> None:
    with pytest.raises(ValueError):
        plot_income_expansion_paths([1, 2], [], 0.5, 4)
