"""第 3 章のアニメーション: 利子率を動かすと、複利の増え方と、倍になる年数が動く。"""

from collections.abc import Callable
from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter03.interest import compound_amount, rule_of_72_years, years_to_multiply


@dataclass(frozen=True)
class CompoundRateFrame:
    """1 つの利子率での、毎年の元利合計（複利・単利）と、倍になる年数。"""

    rate: float
    years: list[int]
    compound: list[float]
    simple: list[float]
    doubling_years: float
    rule_of_72: float


def compound_rate_frames(
    principal: float, horizon: int, min_rate: float, max_rate: float, frames: int
) -> list[CompoundRateFrame]:
    """利子率を min_rate から max_rate へ動かしたときの、各フレームのデータ。"""
    years = list(range(horizon + 1))
    return [
        CompoundRateFrame(
            rate=rate,
            years=years,
            compound=[compound_amount(principal, rate, t) for t in years],
            simple=[principal * (1 + rate * t) for t in years],
            doubling_years=years_to_multiply(rate, 2),
            rule_of_72=rule_of_72_years(rate),
        )
        for rate in linear_values(min_rate, max_rate, frames)
    ]


def animate_compound_rate(
    principal: float = 100,
    horizon: int = 30,
    min_rate: float = 0.01,
    max_rate: float = 0.12,
    frames: int = 23,
) -> FuncAnimation:
    """利子率を上げると、複利の曲線が反り上がり、倍になる年数（縦線）が短くなる。"""
    data = compound_rate_frames(principal, horizon, min_rate, max_rate, frames)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axhline(2 * principal, color="gray", linestyle=":", label="Double the principal")
    (compound,) = ax.plot([], [], "o-", markersize=3, label="Compound interest")
    (simple,) = ax.plot([], [], ":", label="Simple interest")
    exact = ax.axvline(0, color="tab:red", label="Doubling time")
    approx = ax.axvline(0, color="tab:purple", linestyle="--", label="Rule of 72")
    ax.set_xlim(0, horizon)
    ax.set_ylim(0, max(data[-1].compound) * 1.05)
    ax.set_xlabel("Years")
    ax.set_ylabel("Amount")
    ax.legend(fontsize="x-small", loc="upper left", bbox_to_anchor=(0, 0.88))
    label = ax.text(0.02, 0.97, "", transform=ax.transAxes, va="top")

    def update(i: int) -> None:
        frame = data[i]
        compound.set_data(frame.years, frame.compound)
        simple.set_data(frame.years, frame.simple)
        exact.set_xdata([frame.doubling_years])
        approx.set_xdata([frame.rule_of_72])
        label.set_text(
            f"Rate = {frame.rate:.1%}, doubling = {frame.doubling_years:.1f} years "
            f"(rule of 72: {frame.rule_of_72:.1f})"
        )

    plt.close(fig)
    return make_animation(fig, update, frames)


ANIMATIONS: dict[str, Callable[[], FuncAnimation]] = {
    "ch03-compound-rate": animate_compound_rate,
}
