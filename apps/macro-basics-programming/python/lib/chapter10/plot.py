"""労働市場と AD-AS の図。"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter10.ad_as import (
    AdEconomy,
    aggregate_demand_income,
    classical_supply,
    expand_demand,
    keynesian_supply,
    solve_ad_as,
)
from lib.chapter10.labor import (
    LaborCurves,
    labor_demand,
    labor_equilibrium,
    labor_supply,
)


def plot_labor_market(
    curves: LaborCurves, sticky_wage: float, wage_max: float
) -> Figure:
    """労働需要・供給と、均衡。賃金が硬直的で均衡より高いと、需要と供給の差が失業。"""
    wages = [0, wage_max]
    wage, employment = labor_equilibrium(curves)
    fig, ax = plt.subplots()
    ax.plot([labor_demand(curves, w) for w in wages], wages, label="Labor demand")
    ax.plot([labor_supply(curves, w) for w in wages], wages, label="Labor supply")
    ax.plot([employment], [wage], "o", label="Equilibrium")
    ax.plot(
        [labor_demand(curves, sticky_wage), labor_supply(curves, sticky_wage)],
        [sticky_wage, sticky_wage],
        "s-",
        label="Involuntary unemployment",
    )
    ax.set_xlabel("Employment L")
    ax.set_ylabel("Real wage W/P")
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig


def _panel(
    ax: Axes,
    title: str,
    economy: AdEconomy,
    moved: AdEconomy,
    supply_curve: tuple[list[float], list[float]],
    solve: tuple[tuple[float, float], tuple[float, float]],
    prices: list[float],
) -> None:
    ax.plot([aggregate_demand_income(economy, p) for p in prices], prices, label="AD")
    ax.plot(
        [aggregate_demand_income(moved, p) for p in prices],
        prices,
        "--",
        label="AD after",
    )
    ax.plot(*supply_curve, label="AS")
    before, after = solve
    ax.plot([before[1]], [before[0]], "o", label="Equilibrium before")
    ax.plot([after[1]], [after[0]], "s", label="Equilibrium after")
    ax.set_title(title)
    ax.set_xlabel("Income Y")
    ax.legend(fontsize="x-small")


def plot_ad_as(
    economy: AdEconomy,
    full_employment_income: float,
    base_income: float,
    slope: float,
    delta_government: float,
    price_min: float,
    price_max: float,
) -> Figure:
    """左: 古典派（AS が垂直）、右: ケインズ（AS が右上がりのち垂直）。"""
    prices = [float(p) for p in np.linspace(price_min, price_max, 41)]
    moved = expand_demand(economy, delta_government=delta_government)

    def classical(price: float) -> float:
        return classical_supply(price, full_employment_income)

    def keynesian(price: float) -> float:
        return keynesian_supply(price, full_employment_income, base_income, slope)

    fig, (left, right) = plt.subplots(1, 2, sharey=True)
    _panel(
        left,
        "Classical",
        economy,
        moved,
        ([full_employment_income] * 2, [price_min, price_max]),
        (solve_ad_as(economy, classical), solve_ad_as(moved, classical)),
        prices,
    )
    _panel(
        right,
        "Keynesian",
        economy,
        moved,
        ([keynesian(p) for p in prices], prices),
        (solve_ad_as(economy, keynesian), solve_ad_as(moved, keynesian)),
        prices,
    )
    left.set_ylabel("Price level P")
    plt.close(fig)
    return fig
