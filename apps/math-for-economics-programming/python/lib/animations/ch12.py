"""第 12 章のアニメーション: ソロー・モデルの蜘蛛の巣図。"""

from collections.abc import Callable, Sequence
from typing import NamedTuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from lib.animations.common import make_animation
from lib.chapter12.solow import (
    solow_capital_path,
    solow_next_capital,
    solow_steady_state_capital,
)


class CobwebFrame(NamedTuple):
    """period 期までの、初期値ごとの資本の経路。"""

    period: int
    paths: tuple[list[float], ...]


def solow_cobweb_frames(
    starts: Sequence[float],
    saving: float,
    alpha: float,
    depreciation: float,
    periods: int,
) -> list[CobwebFrame]:
    """0 期から periods 期まで、経路を 1 期ずつ伸ばしたフレーム。"""
    if not starts or periods < 1:
        raise ValueError("初期値は 1 つ以上、期数は 1 以上にする")
    full = [solow_capital_path(k, saving, alpha, depreciation, periods) for k in starts]
    return [
        CobwebFrame(t, tuple(path[: t + 1] for path in full))
        for t in range(periods + 1)
    ]


def cobweb_points(path: Sequence[float]) -> tuple[list[float], list[float]]:
    """45 度線から曲線 (k(t), k(t+1)) へ縦に、45 度線へ横に進む、階段の点。"""
    xs, ys = [path[0]], [path[0]]
    for now, nxt in zip(path, path[1:], strict=False):
        xs += [now, nxt]
        ys += [nxt, nxt]
    return xs, ys


def animate_solow_cobweb(
    starts: Sequence[float] = (0.1, 2.5),
    saving: float = 0.5,
    alpha: float = 1 / 3,
    depreciation: float = 0.5,
    frames: int = 16,
) -> FuncAnimation:
    """資本が、曲線 k(t+1) = s·k^α + (1 − δ)·k と 45 度線の間を、階段状に進む。"""
    data = solow_cobweb_frames(starts, saving, alpha, depreciation, frames - 1)
    steady = solow_steady_state_capital(saving, alpha, depreciation)
    top = 1.1 * max(*starts, steady)
    grid = np.linspace(0, top, 200)
    fig, ax = plt.subplots()
    curve = [solow_next_capital(float(k), saving, alpha, depreciation) for k in grid]
    ax.plot(grid, curve, color="C0", label="k(t+1) = s·k^α + (1 − δ)·k")
    ax.plot([0, top], [0, top], ":", color="black", label="45-degree line")
    ax.plot([steady], [steady], "ko", label=f"Steady state k* = {steady:.2f}")
    stairs = [
        ax.plot([], [], color=f"C{j + 1}", label=f"Path from k(0) = {k:g}")[0]
        for j, k in enumerate(starts)
    ]
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(0, top)
    ax.set_ylim(0, top)
    ax.set_xlabel("Capital this period k(t)")
    ax.set_ylabel("Capital next period k(t+1)")
    ax.legend(fontsize="x-small", loc="lower right")

    def update(i: int) -> None:
        frame = data[i]
        for line, path in zip(stairs, frame.paths, strict=True):
            line.set_data(*cobweb_points(path))
        ends = ", ".join(f"{path[-1]:.2f}" for path in frame.paths)
        label.set_text(f"t = {frame.period}, k(t) = {ends}")

    plt.close(fig)
    return make_animation(fig, update, frames)


ANIMATIONS: dict[str, Callable[[], FuncAnimation]] = {
    "ch12-solow-cobweb": animate_solow_cobweb,
}
