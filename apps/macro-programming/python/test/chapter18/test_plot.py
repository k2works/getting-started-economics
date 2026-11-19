"""第 18 章: RBC モデルのインパルス反応の図のテスト。"""

from typing import Any

import pytest

from lib.chapter18.plot import plot_rbc_responses
from lib.chapter18.rbc import RbcParameters, impulse_response, solve_rbc

PARAMS = RbcParameters()


def ys(line: Any) -> list[float]:
    data: Any = line.get_ydata()
    return [float(v) for v in data]


def test_基本モデルの図は4つの変数と0の線() -> None:
    df = impulse_response(solve_rbc(PARAMS), shock=0.01)
    ax = plot_rbc_responses(df).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Output",
        "Consumption",
        "Investment",
        "Capital",
        "Zero",
    ]
    assert ys(ax.lines[0]) == pytest.approx(df["y"].tolist())
    assert ys(ax.lines[2]) == pytest.approx(df["i"].tolist())


def test_内生的労働供給の図は労働も描く() -> None:
    df = impulse_response(solve_rbc(PARAMS, True), shock=0.01)
    ax = plot_rbc_responses(df).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Output",
        "Consumption",
        "Investment",
        "Capital",
        "Labour",
        "Zero",
    ]
    assert ys(ax.lines[4]) == pytest.approx(df["l"].tolist())


def test_0の線と軸の名前() -> None:
    df = impulse_response(solve_rbc(PARAMS), shock=0.01)
    ax = plot_rbc_responses(df).axes[0]
    xs: Any = ax.lines[-1].get_xdata()
    assert [float(x) for x in xs] == [0, len(df) - 1]
    assert ax.lines[-1].get_linestyle() == "--"
    assert ax.get_xlabel() == "Period (shock at period 3)"
    assert ax.get_ylabel() == "Deviation from steady state (%)"
