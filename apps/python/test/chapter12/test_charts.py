"""第 12 章: pandas による図示・移動平均・景気動向のテスト。"""

import math
from typing import Any

import pandas as pd
import pytest
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from lib.chapter11.economy import load_economy
from lib.chapter12.charts import (
    diffusion_index,
    moving_average,
    plot_gdp_chart,
    plot_growth_chart,
)

EXPENDITURE = ["consumption", "investment", "government", "exports"]


def curve_points(line: Line2D) -> dict[float, float]:
    """線の (横軸, 縦軸) の組を、横軸をキーにした辞書にする。"""
    points: Any = line.get_xydata()
    return {float(x): float(y) for x, y in points}


def test_3期移動平均は3つの値の平均で最初の2つは計算できない() -> None:
    result = moving_average(pd.Series([1.0, 2.0, 3.0, 4.0, 5.0]), window=3)
    assert math.isnan(result.iloc[0])
    assert math.isnan(result.iloc[1])
    assert result.iloc[2:].tolist() == [2.0, 3.0, 4.0]


def test_窓の幅が1未満の移動平均は求められない() -> None:
    with pytest.raises(ValueError):
        moving_average(pd.Series([1.0, 2.0, 3.0]), window=0)


def test_景気動向指数は前の年より増えた系列の割合() -> None:
    df = pd.DataFrame(
        {"a": [1, 2, 1], "b": [1, 1, 2], "c": [5, 6, 6]}, index=[2000, 2001, 2002]
    )
    result = diffusion_index(df)
    # 2001 年は a と c の 2 系列が増加、2002 年は b の 1 系列だけが増加
    assert result.index.tolist() == [2001, 2002]
    assert result.tolist() == pytest.approx([200 / 3, 100 / 3])


def test_景気動向指数は最初の年を含まない() -> None:
    df = load_economy()[EXPENDITURE]
    assert 2010 not in diffusion_index(df).index


def test_すべての支出が減った2020年の景気動向指数は0() -> None:
    df = load_economy()[EXPENDITURE]
    assert diffusion_index(df)[2020] == 0


def test_すべての支出が増えた2012年の景気動向指数は100() -> None:
    df = load_economy()[EXPENDITURE]
    assert diffusion_index(df)[2012] == 100


def test_GDPの図には名目と実質の2本の線がある() -> None:
    fig = plot_gdp_chart(load_economy())
    ax = fig.axes[0]
    assert isinstance(fig, Figure)
    assert [line.get_label() for line in ax.lines] == ["Nominal GDP", "Real GDP"]


def test_基準年の2015年では名目と実質のGDPが同じ高さ() -> None:
    ax = plot_gdp_chart(load_economy()).axes[0]
    nominal = curve_points(ax.lines[0])
    real = curve_points(ax.lines[1])
    assert nominal[2015] == pytest.approx(541)
    assert real[2015] == pytest.approx(541)


def test_成長率の図は最初の年を除く11本の棒() -> None:
    ax = plot_growth_chart(load_economy()).axes[0]
    bars = [p for p in ax.patches if isinstance(p, Rectangle)]
    assert len(bars) == 11


def test_成長率の図で一番低い棒は2020年のマイナス3パーセント() -> None:
    ax = plot_growth_chart(load_economy()).axes[0]
    heights = [p.get_height() for p in ax.patches if isinstance(p, Rectangle)]
    assert min(heights) == pytest.approx(-3.0, abs=0.1)
