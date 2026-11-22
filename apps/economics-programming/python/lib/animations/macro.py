"""乗数効果・IS-LM・AD-AS のアニメーション（第 9・13・14 章）。"""

import dataclasses
from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter09.linear import income_determination
from lib.chapter13.islm import IsLmModel, is_income, lm_interest, solve_equilibrium
from lib.chapter14.adas import (
    aggregate_demand,
    classical_supply,
    equilibrium_price_and_income,
)

_PRICE_LEVELS = [round(0.6 + 0.05 * i, 2) for i in range(21)]


def multiplier_frames(
    autonomous_consumption: float,
    mpc: float,
    start_investment: float,
    end_investment: float,
    frames: int,
) -> list[tuple[float, float]]:
    """投資を動かしたときの、各フレームの（投資, 均衡所得）。"""
    return [
        (
            investment,
            income_determination(autonomous_consumption, mpc, investment)[0],
        )
        for investment in linear_values(start_investment, end_investment, frames)
    ]


def animate_multiplier(
    autonomous_consumption: float = 20,
    mpc: float = 0.8,
    start_investment: float = 30,
    end_investment: float = 60,
    frames: int = 30,
) -> FuncAnimation:
    """投資が増えると、総支出の線が上へ動き、均衡所得が、乗数倍に増える。"""
    data = multiplier_frames(
        autonomous_consumption, mpc, start_investment, end_investment, frames
    )
    start_income = data[0][1]
    limit = 1.2 * data[-1][1]
    fig, ax = plt.subplots()
    ax.plot([0, limit], [0, limit], label="45-degree line")
    (spending,) = ax.plot([], [], label="Expenditure")
    (point,) = ax.plot([], [], "o", color="black", label="Equilibrium")
    ax.plot([start_income], [start_income], "o", color="gray", label="Start")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(0, limit)
    ax.set_ylim(0, limit)
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Expenditure")
    ax.legend(fontsize="x-small", loc="lower right")

    def update(i: int) -> None:
        investment, income = data[i]
        base = autonomous_consumption + investment
        spending.set_data([0, limit], [base, base + mpc * limit])
        point.set_data([income], [income])
        label.set_text(f"I = {investment:.1f}, Y = {income:.1f}")

    plt.close(fig)
    return make_animation(fig, update, frames)


def fiscal_models(
    base: IsLmModel, end_government: float, frames: int
) -> list[IsLmModel]:
    """政府支出を base の値から end_government へ動かしたときの、各フレームのモデル。"""
    return [
        dataclasses.replace(base, government=g)
        for g in linear_values(base.government, end_government, frames)
    ]


def animate_islm_fiscal(
    base: IsLmModel | None = None, end_government: float = 160, frames: int = 30
) -> FuncAnimation:
    """政府支出が増えると、IS 曲線が右へ動き、所得と利子率がともに上がる。"""
    model = base or IsLmModel()
    models = fiscal_models(model, end_government, frames)
    rates = [0.2 * i for i in range(71)]
    incomes = [1000 + 15 * i for i in range(61)]
    fig, ax = plt.subplots()
    ax.plot(
        incomes,
        [lm_interest(model, y) for y in incomes],
        color="tab:orange",
        label="LM",
    )
    ax.plot(
        [is_income(model, r) for r in rates],
        rates,
        linestyle=":",
        color="gray",
        label="IS (start)",
    )
    (is_line,) = ax.plot([], [], color="tab:blue", label="IS")
    (point,) = ax.plot([], [], "o", color="black", label="Equilibrium")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(1000, 1900)
    ax.set_ylim(0, 14)
    ax.set_xlabel("Income (Y)")
    ax.set_ylabel("Interest rate (r)")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        current = models[i]
        income, rate = solve_equilibrium(current)
        is_line.set_data([is_income(current, r) for r in rates], rates)
        point.set_data([income], [rate])
        label.set_text(
            f"G = {current.government:.0f}, Y = {income:.0f}, r = {rate:.2f}"
        )

    plt.close(fig)
    return make_animation(fig, update, frames)


@dataclass(frozen=True)
class AdAsFrame:
    """政府支出が変わったときの、総需要と古典派の総供給の均衡。"""

    model: IsLmModel
    price: float
    income: float


def adas_frames(
    base: IsLmModel,
    full_employment_income: float,
    end_government: float,
    frames: int,
) -> list[AdAsFrame]:
    """政府支出を動かしたときの、各フレームの均衡（物価と所得）。"""
    result = []
    for current in fiscal_models(base, end_government, frames):
        price, income = equilibrium_price_and_income(
            current, lambda p: classical_supply(p, full_employment_income)
        )
        result.append(AdAsFrame(current, price, income))
    return result


def animate_adas_fiscal(
    base: IsLmModel | None = None,
    full_employment_income: float = 1250,
    end_government: float = 140,
    frames: int = 30,
) -> FuncAnimation:
    """政府支出が増えると、総需要曲線が右へ動くが、所得は変わらず、物価だけが上がる。"""
    model = base or IsLmModel()
    data = adas_frames(model, full_employment_income, end_government, frames)
    fig, ax = plt.subplots()
    ax.plot(
        [aggregate_demand(model, p) for p in _PRICE_LEVELS],
        _PRICE_LEVELS,
        linestyle=":",
        color="gray",
        label="AD (start)",
    )
    ax.plot(
        [full_employment_income] * 2,
        [_PRICE_LEVELS[0], _PRICE_LEVELS[-1]],
        color="tab:orange",
        label="AS (classical)",
    )
    (demand,) = ax.plot([], [], color="tab:blue", label="AD")
    (point,) = ax.plot([], [], "o", color="black", label="Equilibrium")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(1000, 1800)
    ax.set_ylim(_PRICE_LEVELS[0], _PRICE_LEVELS[-1])
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Price level P")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        demand.set_data(
            [aggregate_demand(frame.model, p) for p in _PRICE_LEVELS], _PRICE_LEVELS
        )
        point.set_data([frame.income], [frame.price])
        label.set_text(
            f"G = {frame.model.government:.0f}, "
            f"P = {frame.price:.2f}, Y = {frame.income:.0f}"
        )

    plt.close(fig)
    return make_animation(fig, update, frames)
