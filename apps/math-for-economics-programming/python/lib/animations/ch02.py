"""第 2 章のアニメーション: クールノー競争で、企業の数を増やす。"""

from collections.abc import Callable
from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Polygon

from lib.animations.common import make_animation
from lib.chapter02.monopoly import (
    MarketOutcome,
    competitive_outcome,
    cournot_outcome,
    monopoly_outcome,
)

# 1 つの企業の数を、何フレーム見せるか（企業の数は整数なので、少し止める）
_HOLD = 3


@dataclass(frozen=True)
class CournotFrame:
    """企業の数ごとの、クールノー均衡（市場全体）と、1 社の数量。"""

    firms: int
    outcome: MarketOutcome

    @property
    def firm_quantity(self) -> float:
        return self.outcome.quantity / self.firms


def cournot_frames(
    a: float, b: float, cost: float, max_firms: int
) -> list[CournotFrame]:
    """企業の数 n = 1…max_firms の、各フレームのクールノー均衡。"""
    return [
        CournotFrame(n, cournot_outcome(n, a, b, cost)) for n in range(1, max_firms + 1)
    ]


def animate_cournot_n(
    a: float = 100, b: float = 1, cost: float = 20, max_firms: int = 10
) -> FuncAnimation:
    """企業が増えると、均衡の点が需要曲線を右下へ動き、利潤の長方形が縮む。"""
    data = cournot_frames(a, b, cost, max_firms)
    monopoly = monopoly_outcome(a, b, cost)
    competition = competitive_outcome(a, b, cost)
    fig, ax = plt.subplots()
    ax.plot([0, a / b], [a, 0], label="Inverse demand")
    ax.plot([0, a / b], [cost, cost], ":", label="Unit cost")
    ax.plot([monopoly.quantity], [monopoly.price], "ks", label="Monopoly")
    ax.plot([competition.quantity], [competition.price], "g^", label="Competition")
    (point,) = ax.plot([], [], "ro", label="Cournot equilibrium")
    profit = Polygon([(0, 0)], closed=True, alpha=0.3, color="tab:orange")
    profit.set_label("Total profit")
    ax.add_patch(profit)
    label = ax.text(0.98, 0.95, "", transform=ax.transAxes, ha="right", va="top")
    ax.set_xlim(0, a / b)
    ax.set_ylim(0, a)
    ax.set_xlabel("Total quantity Q")
    ax.set_ylabel("Price P")
    ax.legend(fontsize="x-small", loc="center right")

    def update(i: int) -> None:
        frame = data[i // _HOLD]
        q, p = frame.outcome.quantity, frame.outcome.price
        point.set_data([q], [p])
        profit.set_xy([(0, cost), (q, cost), (q, p), (0, p)])
        label.set_text(
            f"n = {frame.firms}: firm q = {frame.firm_quantity:.1f}, "
            f"Q = {q:.1f}, P = {p:.1f}"
        )

    plt.close(fig)
    return make_animation(fig, update, len(data) * _HOLD)


ANIMATIONS: dict[str, Callable[[], FuncAnimation]] = {
    "ch02-cournot-n": animate_cournot_n,
}
