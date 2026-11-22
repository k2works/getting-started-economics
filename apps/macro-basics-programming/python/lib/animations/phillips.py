"""失業率を自然失業率より低く保つと、インフレ率が上がり続ける（第 11 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lib.animations.common import make_animation
from lib.chapter11.phillips import accelerating_inflation_path, short_run_inflation

_U_RANGE = [2.0, 8.0]


@dataclass(frozen=True)
class PhillipsFrame:
    """期 period の、期待インフレ率と、実際のインフレ率。"""

    period: int
    expected: float
    inflation: float


def phillips_frames(
    unemployment: float,
    natural_rate: float,
    initial_inflation: float,
    beta: float,
    periods: int,
) -> list[PhillipsFrame]:
    """失業率を保ち続けたときの、各期のデータ。期待は、前の期の現実に等しい。"""
    path = accelerating_inflation_path(
        unemployment, natural_rate, initial_inflation, beta, periods
    )
    expected = [initial_inflation, *path[:-1]]
    return [PhillipsFrame(t, expected[t], path[t]) for t in range(len(path))]


def animate_accelerating_inflation(
    unemployment: float = 4.0,
    natural_rate: float = 5.0,
    initial_inflation: float = 2.0,
    beta: float = 0.5,
    periods: int = 8,
) -> FuncAnimation:
    """期待が追いつくたびに、短期のフィリップス曲線が上へ動き、点も上へ動き続ける。"""
    data = phillips_frames(unemployment, natural_rate, initial_inflation, beta, periods)
    fig, ax = plt.subplots()
    ax.plot([natural_rate, natural_rate], [0, 8], linestyle=":", label="Natural rate")
    (curve,) = ax.plot([], [], label="Short-run Phillips curve")
    (trail,) = ax.plot([], [], "o", label="Economy")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(*_U_RANGE)
    ax.set_ylim(0, 8)
    ax.set_xlabel("Unemployment rate u (%)")
    ax.set_ylabel("Inflation rate (%)")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        curve.set_data(
            _U_RANGE,
            [
                short_run_inflation(u, natural_rate, frame.expected, beta)
                for u in _U_RANGE
            ],
        )
        trail.set_data([unemployment] * (i + 1), [f.inflation for f in data[: i + 1]])
        label.set_text(
            f"Period {frame.period}: expected = {frame.expected:.1f}, "
            f"inflation = {frame.inflation:.1f}"
        )

    plt.close(fig)
    return make_animation(fig, update, len(data))
