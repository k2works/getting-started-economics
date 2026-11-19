"""第 15 章: IS-MP-PC モデルの図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D

from lib.chapter15.ismppc import IsMpPcParameters, impulse_response
from lib.chapter15.plot import plot_responses, plot_stance_comparison

DEFAULT = IsMpPcParameters()
CASE_2 = IsMpPcParameters(c=0.5, d=1.5)


def ys(line: Line2D) -> list[float]:
    data: Any = line.get_ydata()
    return [float(v) for v in data]


def xs(line: Line2D) -> list[float]:
    data: Any = line.get_xdata()
    return [float(v) for v in data]


def test_反応の図は4つの変数と0の線() -> None:
    df = impulse_response(DEFAULT, shock_pc=1.0)
    ax = plot_responses(df).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Inflation",
        "Output",
        "Nominal rate",
        "Real rate",
        "Zero",
    ]


def test_反応の図は定常状態からの乖離を描く() -> None:
    df = impulse_response(DEFAULT, shock_pc=1.0)
    ax = plot_responses(df).axes[0]
    assert ys(ax.lines[0]) == pytest.approx((df["pi"] - 2.0).tolist())
    assert ys(ax.lines[1]) == pytest.approx((df["y"] - 100.0).tolist())
    assert ys(ax.lines[2]) == pytest.approx((df["i"] - 4.0).tolist())
    assert ys(ax.lines[3]) == pytest.approx((df["r"] - 2.0).tolist())


def test_0の線は最初の期から最後の期まで() -> None:
    df = impulse_response(DEFAULT, shock_pc=1.0)
    ax = plot_responses(df).axes[0]
    assert xs(ax.lines[4]) == [0, len(df) - 1]


def test_反応の図の横軸はショックの期を示す() -> None:
    ax = plot_responses(impulse_response(DEFAULT, shock_pc=1.0)).axes[0]
    assert ax.get_xlabel() == "Period (shock at period 3)"


def test_政策スタンスの図は2つのケースのインフレ率と産出量() -> None:
    case1 = impulse_response(DEFAULT, shock_pc=1.0)
    case2 = impulse_response(CASE_2, shock_pc=1.0)
    ax = plot_stance_comparison(case1, case2).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Inflation (case 1)",
        "Output (case 1)",
        "Inflation (case 2)",
        "Output (case 2)",
        "Zero",
    ]
    assert ys(ax.lines[2]) == pytest.approx((case2["pi"] - 2.0).tolist())
    assert ys(ax.lines[1]) == pytest.approx((case1["y"] - 100.0).tolist())
    assert xs(ax.lines[4]) == [0, len(case1) - 1]


def test_政策スタンスの図は実線がcase1で点線がcase2() -> None:
    case1 = impulse_response(DEFAULT, shock_pc=1.0)
    case2 = impulse_response(CASE_2, shock_pc=1.0)
    ax = plot_stance_comparison(case1, case2).axes[0]
    styles = [line.get_linestyle() for line in ax.lines]
    assert styles == ["-", "-", ":", ":", "--"]
