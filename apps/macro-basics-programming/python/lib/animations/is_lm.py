"""IS 曲線のシフトとクラウディングアウトのアニメーション（第 8・9 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter07.money_market import lm_interest
from lib.chapter08.is_lm import is_interest, solve_is_lm
from lib.chapter09.policy import crowding_out, fiscal_effect

_INCOMES = [600.0, 1200.0]
_INTEREST_MAX = 12.0


@dataclass(frozen=True)
class ShiftFrame:
    """政府支出の増加のもとの、IS の切片と、IS-LM の均衡。"""

    delta_government: float
    intercept: float
    income: float
    interest: float


def fiscal_shift_frames(
    mpc: float,
    b: float,
    intercept: float,
    k: float,
    h: float,
    real_money: float,
    max_delta_government: float,
    frames: int,
) -> list[ShiftFrame]:
    """政府支出を 0 から増やしたときの、各フレームのデータ。"""
    data = []
    for dg in linear_values(0.0, max_delta_government, frames):
        income, interest = solve_is_lm(mpc, b, intercept + dg, k, h, real_money)
        data.append(ShiftFrame(dg, intercept + dg, income, interest))
    return data


def animate_fiscal_shift(
    mpc: float = 0.6,
    b: float = 20.0,
    intercept: float = 450.0,
    k: float = 0.5,
    h: float = 100.0,
    real_money: float = 250.0,
    max_delta_government: float = 40.0,
    frames: int = 30,
) -> FuncAnimation:
    """政府支出が増えると、IS 曲線が右へ動き、均衡が LM 曲線に沿って右上へ動く。"""
    data = fiscal_shift_frames(
        mpc, b, intercept, k, h, real_money, max_delta_government, frames
    )
    fig, ax = plt.subplots()
    ax.plot(_INCOMES, [is_interest(y, intercept, mpc, b) for y in _INCOMES], ":")
    ax.plot(_INCOMES, [lm_interest(y, real_money, k, h) for y in _INCOMES], label="LM")
    (curve,) = ax.plot([], [], label="IS")
    (point,) = ax.plot([], [], "o", label="Equilibrium")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(*_INCOMES)
    ax.set_ylim(0, _INTEREST_MAX)
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Interest rate r")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        curve.set_data(
            _INCOMES, [is_interest(y, frame.intercept, mpc, b) for y in _INCOMES]
        )
        point.set_data([frame.income], [frame.interest])
        label.set_text(
            f"Delta G = {frame.delta_government:.0f}, Y = {frame.income:.0f}, "
            f"r = {frame.interest:.2f}"
        )

    plt.close(fig)
    return make_animation(fig, update, frames)


@dataclass(frozen=True)
class CrowdingFrame:
    """ある h のもとの、財政政策の効果・クラウディングアウト・政策の前後の所得。"""

    h: float
    effect: float
    crowding_out: float
    income_before: float
    income_after: float


def crowding_frames(
    mpc: float,
    b: float,
    intercept: float,
    k: float,
    h_start: float,
    h_end: float,
    delta_government: float,
    real_money: float,
    frames: int,
) -> list[CrowdingFrame]:
    """貨幣需要の利子感応度 h を動かしたときの、各フレームのデータ。"""
    data = []
    for h in linear_values(h_start, h_end, frames):
        before, _ = solve_is_lm(mpc, b, intercept, k, h, real_money)
        after, _ = solve_is_lm(mpc, b, intercept + delta_government, k, h, real_money)
        data.append(
            CrowdingFrame(
                h,
                fiscal_effect(mpc, b, k, h, delta_government),
                crowding_out(mpc, b, k, h, delta_government),
                before,
                after,
            )
        )
    return data


def animate_crowding_out(
    mpc: float = 0.6,
    b: float = 20.0,
    intercept: float = 450.0,
    k: float = 0.5,
    h_start: float = 20.0,
    h_end: float = 400.0,
    delta_government: float = 20.0,
    real_money: float = 250.0,
    frames: int = 30,
) -> FuncAnimation:
    """h が大きい（LM が平ら）ほど、所得が増え、クラウディングアウトが減る。"""
    data = crowding_frames(
        mpc,
        b,
        intercept,
        k,
        h_start,
        h_end,
        delta_government,
        real_money,
        frames,
    )
    fig, ax = plt.subplots()
    ax.plot(_INCOMES, [is_interest(y, intercept, mpc, b) for y in _INCOMES], ":")
    shifted = intercept + delta_government
    ax.plot(
        _INCOMES,
        [is_interest(y, shifted, mpc, b) for y in _INCOMES],
        label="IS after",
    )
    (lm,) = ax.plot([], [], label="LM")
    (before,) = ax.plot([], [], "o", label="Before")
    (after,) = ax.plot([], [], "s", label="After")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(*_INCOMES)
    ax.set_ylim(0, _INTEREST_MAX)
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Interest rate r")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        lm.set_data(
            _INCOMES, [lm_interest(y, real_money, k, frame.h) for y in _INCOMES]
        )
        before.set_data(
            [frame.income_before],
            [lm_interest(frame.income_before, real_money, k, frame.h)],
        )
        after.set_data(
            [frame.income_after],
            [lm_interest(frame.income_after, real_money, k, frame.h)],
        )
        label.set_text(
            f"h = {frame.h:.0f}, effect = {frame.effect:.1f}, "
            f"crowding out = {frame.crowding_out:.1f}"
        )

    plt.close(fig)
    return make_animation(fig, update, frames)
