"""第 5 章: ソロー・モデルの図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D

from lib.chapter05.plot import plot_solow_convergence, plot_solow_diagram
from lib.chapter05.solow import (
    log_linear_path,
    solow_path,
    steady_state_capital,
)

MODEL = {"saving_rate": 0.2, "depreciation": 0.05, "alpha": 0.5}


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def test_ソロー図には貯蓄と減耗の曲線と定常状態の点がある() -> None:
    ax = plot_solow_diagram(**MODEL).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Saving",
        "Depreciation",
        "Steady state",
    ]


def test_定常状態の点は貯蓄と減耗が交わる点() -> None:
    ax = plot_solow_diagram(**MODEL).axes[0]
    (k, value) = xy(ax.lines[2])[0]
    assert k == pytest.approx(steady_state_capital(**MODEL))
    assert value == pytest.approx(0.05 * 16)
    assert value == pytest.approx(0.2 * 16**0.5)


def test_貯蓄の曲線は減耗の直線の上から下に出る() -> None:
    ax = plot_solow_diagram(**MODEL).axes[0]
    saving = [y for _, y in xy(ax.lines[0])]
    depreciation = [y for _, y in xy(ax.lines[1])]
    # 資本が少ないうちは、貯蓄のほうが多い（資本が増える）
    assert saving[1] > depreciation[1]
    # 資本が多いと、減耗のほうが多い（資本が減る）
    assert saving[-1] < depreciation[-1]


def test_収束の図には各初期値の経路と近似と定常状態がある() -> None:
    ax = plot_solow_convergence([2, 25], **MODEL, periods=50).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "k0 = 2",
        "k0 = 25",
        "Log-linear (k0 = 2)",
        "Steady state",
    ]


def test_経路は厳密な計算と一致する() -> None:
    ax = plot_solow_convergence([2, 25], **MODEL, periods=50).axes[0]
    assert [y for _, y in xy(ax.lines[0])] == pytest.approx(
        solow_path(2, **MODEL, periods=50)
    )


def test_近似の経路は対数線形近似と一致する() -> None:
    ax = plot_solow_convergence([2, 25], **MODEL, periods=50).axes[0]
    expected = log_linear_path(2, 16, 0.025, 50)
    assert [y for _, y in xy(ax.lines[2])] == pytest.approx(expected)
