"""第 12 章: 消費の理論と加速度原理の図のテスト。"""

import numpy as np
import pytest
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from lib.chapter12.plot import plot_accelerator, plot_consumption_theories


def ydata(line: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(line.get_ydata())]


INCOMES = [100, 100, 100, 130, 100, 100]


def test_消費の理論の図は4本の線で一時的な所得の増加への反応を比べる() -> None:
    ax = plot_consumption_theories(INCOMES, 0.8, 0.2).axes[0]
    labels = [line.get_label() for line in ax.get_lines()]
    assert labels == ["Income", "Absolute income", "Permanent income", "Ratchet"]


def test_絶対所得仮説の線は所得の変動にそのまま反応する() -> None:
    ax = plot_consumption_theories(INCOMES, 0.8, 0.2).axes[0]
    absolute = ydata(ax.get_lines()[1])
    assert absolute == pytest.approx([80, 80, 80, 104, 80, 80])


def test_恒常所得仮説の線は一時的な増加にあまり反応しない() -> None:
    ax = plot_consumption_theories(INCOMES, 0.8, 0.2).axes[0]
    permanent = ydata(ax.get_lines()[2])
    assert permanent[3] == pytest.approx(84.8)
    assert permanent[4] == pytest.approx(83.84)


def test_ラチェットの線は最高所得のまま下がらない() -> None:
    ax = plot_consumption_theories(INCOMES, 0.8, 0.2).axes[0]
    assert ydata(ax.get_lines()[3]) == pytest.approx([80, 80, 80, 104, 104, 104])


def test_消費の理論の図の軸の名前() -> None:
    ax = plot_consumption_theories(INCOMES, 0.8, 0.2).axes[0]
    assert ax.get_xlabel() == "Period"
    assert ax.get_ylabel() == "Consumption"


def test_加速度原理の図は上が所得の線で下が投資の棒() -> None:
    incomes = [100, 120, 140, 150, 155, 155]
    fig = plot_accelerator(2, incomes)
    top, bottom = fig.axes
    assert ydata(top.get_lines()[0]) == pytest.approx(incomes)
    bars = [p.get_height() for p in bottom.patches if isinstance(p, Rectangle)]
    assert bars == pytest.approx([40, 40, 20, 10, 0])


def test_加速度原理の図の軸の名前() -> None:
    top, bottom = plot_accelerator(2, [100, 120]).axes
    assert top.get_ylabel() == "Income"
    assert bottom.get_ylabel() == "Investment"
    assert bottom.get_xlabel() == "Period"


def test_投資の棒は2期目から並び上の図の下に置かれる() -> None:
    top, bottom = plot_accelerator(2, [100, 120, 140, 150]).axes
    bars = [p for p in bottom.patches if isinstance(p, Rectangle)]
    centers = [p.get_x() + p.get_width() / 2 for p in bars]
    assert centers == pytest.approx([1, 2, 3])
    assert top.get_position().y0 > bottom.get_position().y0
