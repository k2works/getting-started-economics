"""第 2 章: 成長会計のテスト。

成長率は、対数の差を年数で割った値（%）。y = A·k^α·h^(1−α) なので、
g_y = g_A + α·g_k + (1−α)·g_h が成り立つ。
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lib.chapter01.accounting import load_countries
from lib.chapter02.growth import (
    contribution_shares,
    growth_contribution,
    load_panel,
    log_growth_rate,
)

ALPHA = 1 / 3


def example_panel() -> pd.DataFrame:
    """2000〜2010 年。1 年当たりの対数の成長率は、A が 1%、k が 6%、h が 3%。"""
    rows = []
    for year in range(2000, 2011):
        t = year - 2000
        a = np.exp(0.01 * t)
        k = 8 * np.exp(0.06 * t)
        h = np.exp(0.03 * t)
        rows.append(("X", year, a * k ** (1 / 3) * h ** (2 / 3), k, h))
    df = pd.DataFrame(rows, columns=["country", "year", "y", "k", "h"])
    return df.set_index(["country", "year"])


def test_2倍になる系列の10年間の成長率は年6_93パーセント() -> None:
    assert log_growth_rate(1, 2, 10) == pytest.approx(100 * np.log(2) / 10)


def test_毎年の対数の成長率が5パーセントなら成長率は5() -> None:
    assert log_growth_rate(1, np.exp(0.5), 10) == pytest.approx(5)


def test_成長率は負にもなる() -> None:
    assert log_growth_rate(2, 1, 10) < 0


@pytest.mark.parametrize(
    ("start", "end", "years"), [(0, 1, 10), (1, 0, 10), (-1, 1, 10), (1, 2, 0)]
)
def test_値は正で年数も正でなければならない(
    start: float, end: float, years: float
) -> None:
    with pytest.raises(ValueError):
        log_growth_rate(start, end, years)


def test_CSVを読むと国と年が行の名前になる(tmp_path: Path) -> None:
    path = tmp_path / "panel.csv"
    path.write_text(
        "country,year,y,k,h\nA,2000,2.0,8.0,1.0\nA,2001,2.1,8.5,1.0\n",
        encoding="utf-8",
    )
    df = load_panel(path)
    assert list(df.index.names) == ["country", "year"]
    assert df.loc[("A", 2001), "k"] == 8.5


def test_同梱のパネルは24か国の1990年から2019年まで() -> None:
    df = load_panel()
    assert len(df) == 24 * 30
    assert df.index.get_level_values("year").min() == 1990
    assert df.index.get_level_values("year").max() == 2019


def test_2019年の値は第1章のデータと同じ() -> None:
    latest = load_panel().xs(2019, level="year")
    countries = load_countries()
    assert latest.loc[countries.index].to_numpy() == pytest.approx(countries.to_numpy())


def test_成長率を資本_人的資本_TFPの寄与に分ける() -> None:
    table = growth_contribution(example_panel(), 2000, 2010, ALPHA)
    row = table.loc["X"]
    # g_y = 1 + (1/3)·6 + (2/3)·3 = 1 + 2 + 2 = 5
    assert row["output"] == pytest.approx(5)
    assert row["capital"] == pytest.approx(2)
    assert row["human_capital"] == pytest.approx(2)
    assert row["tfp"] == pytest.approx(1)


def test_3つの寄与の和は所得の成長率と等しい() -> None:
    table = growth_contribution(load_panel(), 1990, 2019, ALPHA)
    parts = table["capital"] + table["human_capital"] + table["tfp"]
    assert parts.to_numpy() == pytest.approx(table["output"].to_numpy())


def test_列は所得_資本_人的資本_TFPの順() -> None:
    table = growth_contribution(example_panel(), 2000, 2010, ALPHA)
    assert list(table.columns) == ["output", "capital", "human_capital", "tfp"]


def test_期間の始まりは終わりより前でなければならない() -> None:
    with pytest.raises(ValueError, match="期間"):
        growth_contribution(example_panel(), 2010, 2000, ALPHA)


def test_期間が0年でも受け付けない() -> None:
    with pytest.raises(ValueError, match="期間"):
        growth_contribution(example_panel(), 2005, 2005, ALPHA)


def test_パネルにない年は受け付けない() -> None:
    with pytest.raises(ValueError, match="年"):
        growth_contribution(example_panel(), 1990, 2010, ALPHA)


def test_TFPの寄与の割合は5分の1() -> None:
    table = growth_contribution(example_panel(), 2000, 2010, ALPHA)
    shares = contribution_shares(table)
    assert shares.loc["X", "tfp"] == pytest.approx(0.2)
    assert shares.loc["X", "capital"] == pytest.approx(0.4)


def test_寄与の割合の合計は1() -> None:
    table = growth_contribution(load_panel(), 1990, 2019, ALPHA)
    shares = contribution_shares(table)
    assert shares.sum(axis=1).to_numpy() == pytest.approx(1)


def test_成長率が0の国があれば割合は求められない() -> None:
    table = pd.DataFrame(
        {"output": [0.0], "capital": [0.0], "human_capital": [0.0], "tfp": [0.0]},
        index=["Z"],
    )
    with pytest.raises(ValueError, match="0"):
        contribution_shares(table)
