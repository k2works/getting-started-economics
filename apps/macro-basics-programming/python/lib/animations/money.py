"""信用創造と LM 曲線のシフトのアニメーション（第 6・7 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter06.money_supply import credit_creation_path, money_stock
from lib.chapter07.liquidity import lm_interest_with_trap
from lib.chapter07.money_market import lm_interest

_INCOMES = [float(y) for y in range(600, 1201, 25)]


@dataclass(frozen=True)
class CreditFrame:
    """信用創造のラウンドと、そのときのマネーストック。limit は、最終的な値。"""

    round: int
    stock: float
    limit: float


def credit_frames(
    base: float, cash_ratio: float, reserve_ratio: float, rounds: int
) -> list[CreditFrame]:
    """信用創造を、ラウンドごとに追った、各フレームのデータ。"""
    limit = money_stock(cash_ratio, reserve_ratio, base)
    path = credit_creation_path(base, cash_ratio, reserve_ratio, rounds)
    return [CreditFrame(i + 1, stock, limit) for i, stock in enumerate(path)]


def animate_credit_creation(
    base: float = 110.0,
    cash_ratio: float = 0.1,
    reserve_ratio: float = 0.01,
    rounds: int = 40,
) -> FuncAnimation:
    """ラウンドを重ねるごとに、マネーストックが、貨幣乗数 × H へ近づく。"""
    data = credit_frames(base, cash_ratio, reserve_ratio, rounds)
    limit = data[0].limit
    fig, ax = plt.subplots()
    ax.plot([1, rounds], [limit, limit], linestyle="--", label="M = multiplier x H")
    (line,) = ax.plot([], [], label="Money stock")
    label = ax.text(0.02, 0.8, "", transform=ax.transAxes, va="top")
    ax.set_xlim(1, rounds)
    ax.set_ylim(0, limit * 1.1)
    ax.set_xlabel("Round")
    ax.set_ylabel("Money stock M")
    ax.legend(fontsize="x-small", loc="upper left")

    def update(i: int) -> None:
        line.set_data(
            [f.round for f in data[: i + 1]], [f.stock for f in data[: i + 1]]
        )
        label.set_text(f"Round {data[i].round}: M = {data[i].stock:.0f}")

    plt.close(fig)
    return make_animation(fig, update, len(data))


@dataclass(frozen=True)
class LmFrame:
    """ある実質貨幣供給のもとの、LM 曲線と、流動性のわなのある LM 曲線。"""

    real_money: float
    curve: list[float]
    trap_curve: list[float]


def lm_shift_frames(
    real_money_start: float,
    real_money_end: float,
    k: float,
    h: float,
    floor: float,
    incomes: list[float],
    frames: int,
) -> list[LmFrame]:
    """実質貨幣供給を増やしたときの、各フレームの LM 曲線。"""
    return [
        LmFrame(
            m,
            [lm_interest(y, m, k, h) for y in incomes],
            [lm_interest_with_trap(y, m, k, h, floor) for y in incomes],
        )
        for m in linear_values(real_money_start, real_money_end, frames)
    ]


def animate_lm_shift(
    real_money_start: float = 250.0,
    real_money_end: float = 400.0,
    k: float = 0.5,
    h: float = 100.0,
    floor: float = 2.5,
    frames: int = 30,
) -> FuncAnimation:
    """実質貨幣供給が増えると、LM 曲線が下へ動き、わなの水平部分に行き当たる。"""
    data = lm_shift_frames(
        real_money_start, real_money_end, k, h, floor, _INCOMES, frames
    )
    fig, ax = plt.subplots()
    ax.plot(_INCOMES, data[0].curve, linestyle=":", label="LM at start")
    (lm,) = ax.plot([], [], label="LM")
    (trap,) = ax.plot([], [], linestyle="--", label="LM with trap")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(_INCOMES[0], _INCOMES[-1])
    ax.set_ylim(0, 8)
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Interest rate r")
    ax.legend(fontsize="x-small", loc="lower right")

    def update(i: int) -> None:
        frame = data[i]
        lm.set_data(_INCOMES, frame.curve)
        trap.set_data(_INCOMES, frame.trap_curve)
        label.set_text(f"M/P = {frame.real_money:.0f}")

    plt.close(fig)
    return make_animation(fig, update, frames)
