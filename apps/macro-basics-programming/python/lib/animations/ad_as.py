"""政府支出で AD が右へ動くと、均衡の物価と所得が動く（第 10 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter10.ad_as import (
    AdEconomy,
    aggregate_demand_income,
    expand_demand,
    keynesian_supply,
    solve_ad_as,
)

_ECONOMY = AdEconomy(mpc=0.6, b=20, intercept=450, k=0.5, h=100, nominal_money=250)
_PRICES = [0.8 + 0.02 * i for i in range(41)]


@dataclass(frozen=True)
class AdFrame:
    """政府支出の増加のもとの、AD 曲線と、AD と AS の交点。"""

    delta_government: float
    curve: list[float]
    price: float
    income: float


def ad_as_frames(
    economy: AdEconomy,
    full_employment_income: float,
    base_income: float,
    slope: float,
    max_delta_government: float,
    prices: list[float],
    frames: int,
) -> list[AdFrame]:
    """政府支出を 0 から増やしたときの、各フレームのデータ。"""

    def supply(price: float) -> float:
        return keynesian_supply(price, full_employment_income, base_income, slope)

    data = []
    for dg in linear_values(0.0, max_delta_government, frames):
        moved = expand_demand(economy, delta_government=dg)
        price, income = solve_ad_as(moved, supply)
        curve = [aggregate_demand_income(moved, p) for p in prices]
        data.append(AdFrame(dg, curve, price, income))
    return data


def animate_ad_as(
    economy: AdEconomy = _ECONOMY,
    full_employment_income: float = 1000.0,
    base_income: float = 480.0,
    slope: float = 400.0,
    max_delta_government: float = 15.0,
    frames: int = 30,
) -> FuncAnimation:
    """政府支出が増えると、AD が右へ動き、AS が右上がりの間は、物価も所得も上がる。"""
    data = ad_as_frames(
        economy,
        full_employment_income,
        base_income,
        slope,
        max_delta_government,
        _PRICES,
        frames,
    )
    fig, ax = plt.subplots()
    ax.plot(data[0].curve, _PRICES, linestyle=":")
    ax.plot(
        [
            keynesian_supply(p, full_employment_income, base_income, slope)
            for p in _PRICES
        ],
        _PRICES,
        label="AS",
    )
    (demand,) = ax.plot([], [], label="AD")
    (point,) = ax.plot([], [], "o", label="Equilibrium")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(900, 1100)
    ax.set_ylim(_PRICES[0], _PRICES[-1])
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Price level P")
    ax.legend(fontsize="x-small", loc="lower right")

    def update(i: int) -> None:
        frame = data[i]
        demand.set_data(frame.curve, _PRICES)
        point.set_data([frame.income], [frame.price])
        label.set_text(
            f"Delta G = {frame.delta_government:.0f}, P = {frame.price:.2f}, "
            f"Y = {frame.income:.0f}"
        )

    plt.close(fig)
    return make_animation(fig, update, frames)
