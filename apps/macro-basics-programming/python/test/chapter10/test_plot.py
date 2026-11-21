"""第 10 章: 労働市場と AD-AS の図のテスト。"""

import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter10.ad_as import (
    AdEconomy,
    aggregate_demand_income,
    expand_demand,
    keynesian_supply,
)
from lib.chapter10.labor import LaborCurves
from lib.chapter10.plot import plot_ad_as, plot_labor_market

CURVES = LaborCurves(100, 10, 20, 10)
ECONOMY = AdEconomy(mpc=0.6, b=20, intercept=450, k=0.5, h=100, nominal_money=250)


def line(ax: Axes, label: str) -> Line2D:
    (found,) = [ln for ln in ax.get_lines() if ln.get_label() == label]
    return found


def xs(ln: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(ln.get_xdata(), dtype=float)]


def ys(ln: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(ln.get_ydata(), dtype=float)]


def test_労働市場の図は需要と供給の曲線() -> None:
    ax = plot_labor_market(CURVES, sticky_wage=6, wage_max=10).axes[0]
    demand = line(ax, "Labor demand")
    supply = line(ax, "Labor supply")
    assert ys(demand) == [0, 10]
    assert xs(demand) == pytest.approx([100, 0])
    assert xs(supply) == pytest.approx([20, 120])


def test_労働市場の図の均衡点は賃金4で雇用60() -> None:
    ax = plot_labor_market(CURVES, sticky_wage=6, wage_max=10).axes[0]
    point = line(ax, "Equilibrium")
    assert xs(point) == pytest.approx([60])
    assert ys(point) == pytest.approx([4])


def test_労働市場の図の失業は硬直的な賃金での需要から供給まで() -> None:
    ax = plot_labor_market(CURVES, sticky_wage=6, wage_max=10).axes[0]
    gap = line(ax, "Involuntary unemployment")
    assert xs(gap) == pytest.approx([40, 80])
    assert ys(gap) == pytest.approx([6, 6])


def test_労働市場の図の軸の名前() -> None:
    ax = plot_labor_market(CURVES, sticky_wage=6, wage_max=10).axes[0]
    assert ax.get_xlabel() == "Employment L"
    assert ax.get_ylabel() == "Real wage W/P"


def draw(delta_government: float = 10) -> list[Axes]:
    return plot_ad_as(
        ECONOMY,
        full_employment_income=1000,
        base_income=480,
        slope=400,
        delta_government=delta_government,
        price_min=0.8,
        price_max=1.6,
    ).axes


def test_AD_ASの図は古典派とケインズの2枚() -> None:
    left, right = draw()
    assert left.get_title() == "Classical"
    assert right.get_title() == "Keynesian"


def test_総需要の曲線は右下がり() -> None:
    left, _ = draw()
    incomes = xs(line(left, "AD"))
    prices = ys(line(left, "AD"))
    assert len(prices) == 41
    assert prices == sorted(prices)
    assert incomes == sorted(incomes, reverse=True)
    assert incomes[0] == pytest.approx(aggregate_demand_income(ECONOMY, prices[0]))


def test_古典派の総供給は垂直() -> None:
    left, _ = draw()
    assert xs(line(left, "AS")) == [1000, 1000]
    assert ys(line(left, "AS")) == [0.8, 1.6]


def test_ケインズの総供給は右上がりのち垂直() -> None:
    _, right = draw()
    supply = line(right, "AS")
    incomes = xs(supply)
    prices = ys(supply)
    assert incomes[0] == pytest.approx(keynesian_supply(prices[0], 1000, 480, 400))
    assert incomes[-1] == 1000
    assert incomes == sorted(incomes)


def test_古典派の均衡は所得が動かず物価だけが動く() -> None:
    left, _ = draw()
    before, after = line(left, "Equilibrium before"), line(left, "Equilibrium after")
    assert xs(before) == pytest.approx([1000])
    assert ys(before) == pytest.approx([1.0])
    assert xs(after) == pytest.approx([1000])
    assert ys(after) == pytest.approx([1.25])


def test_ケインズの均衡は所得も物価も動く() -> None:
    _, right = draw()
    before, after = line(right, "Equilibrium before"), line(right, "Equilibrium after")
    assert xs(before) == pytest.approx([980])
    assert ys(before) == pytest.approx([1.25])
    assert xs(after)[0] > 980
    assert ys(after)[0] > 1.25


def test_政策後の総需要は右にある() -> None:
    left, _ = draw()
    moved = expand_demand(ECONOMY, delta_government=10)
    after = line(left, "AD after")
    prices = ys(after)
    assert xs(after) == pytest.approx(
        [aggregate_demand_income(moved, p) for p in prices]
    )
    assert np.all(np.array(xs(after)) > np.array(xs(line(left, "AD"))))


def test_AD_ASの図の軸の名前() -> None:
    left, right = draw()
    for ax in (left, right):
        assert ax.get_xlabel() == "Income Y"
    assert left.get_ylabel() == "Price level P"
