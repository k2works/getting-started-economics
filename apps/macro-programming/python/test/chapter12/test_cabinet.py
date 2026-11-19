"""第 12 章: 内閣府の四半期データ（実際の統計）の読み込みのテスト。

公式の CSV と同じ構造（cp932、見出し 7 行、第 1 四半期の行にだけ年が付く）の、
小さなファイルを、テストの中で作って使う。
"""

from pathlib import Path

import numpy as np
import pytest

from lib.chapter12.cabinet import load_cabinet_quarterly, year_over_year

HEADER = [
    "実質季節調整系列,,,<参考>,,(単位:2020暦年連鎖価格、10億円)",
    "Real, Seasonally Adjusted Series,,,<cf>",
    ",国内総生産(支出側),民間最終消費支出",
    ",,,家計最終消費支出",
    ",,,",
    ",GDP(Expenditure Approach),PrivateConsumption",
    ",,,",
]
ROWS = [
    '1994/ 1- 3.,"465,062.6 ","252,336.7 "',
    '4- 6.,"461,497.1 ","250,000.0 "',
    '7- 9.,"466,135.7 ","251,000.0 "',
    '10-12.,"464,394.6 ","252,000.0 "',
    '1995/ 1- 3.,"468,893.1 ","253,000.0 "',
]
NOTES = ["＊年率で表示している。", "＊開差＝国内総生産(支出側)－内訳項目計"]


def write_csv(path: Path, rows: list[str]) -> None:
    path.write_text("\n".join([*HEADER, *rows, *NOTES]) + "\n", encoding="cp932")


def test_第1四半期の行の年が続く行にも引き継がれる(tmp_path: Path) -> None:
    path = tmp_path / "q.csv"
    write_csv(path, ROWS)
    series = load_cabinet_quarterly(path)
    assert [str(p) for p in series.index] == [
        "1994Q1",
        "1994Q2",
        "1994Q3",
        "1994Q4",
        "1995Q1",
    ]


def test_値は3桁区切りと空白を除いた小数(tmp_path: Path) -> None:
    path = tmp_path / "q.csv"
    write_csv(path, ROWS)
    series = load_cabinet_quarterly(path)
    assert series.iloc[0] == pytest.approx(465062.6)
    assert series.iloc[-1] == pytest.approx(468893.1)


def test_列の位置を指定して別の項目を読める(tmp_path: Path) -> None:
    path = tmp_path / "q.csv"
    write_csv(path, ROWS)
    consumption = load_cabinet_quarterly(path, column=2)
    assert consumption.iloc[0] == pytest.approx(252336.7)


def test_空の行は読み飛ばす(tmp_path: Path) -> None:
    path = tmp_path / "q.csv"
    write_csv(path, [ROWS[0], "", ROWS[1]])
    assert len(load_cabinet_quarterly(path)) == 2


def test_注記の行は読み飛ばす(tmp_path: Path) -> None:
    path = tmp_path / "q.csv"
    write_csv(path, ROWS)
    assert len(load_cabinet_quarterly(path)) == 5


def test_四半期の行がなければ受け付けない(tmp_path: Path) -> None:
    path = tmp_path / "q.csv"
    write_csv(path, [])
    with pytest.raises(ValueError, match="四半期"):
        load_cabinet_quarterly(path)


def test_前年同期比は対数の差のパーセント(tmp_path: Path) -> None:
    path = tmp_path / "q.csv"
    write_csv(path, ROWS)
    growth = year_over_year(load_cabinet_quarterly(path))
    assert len(growth) == 1
    assert growth.iloc[0] == pytest.approx(100 * np.log(468893.1 / 465062.6))


def test_前年同期比は最初の4四半期が欠ける(tmp_path: Path) -> None:
    path = tmp_path / "q.csv"
    write_csv(path, ROWS)
    growth = year_over_year(load_cabinet_quarterly(path))
    assert str(growth.index[0]) == "1995Q1"


def test_年の行より前の四半期の行は読み飛ばす(tmp_path: Path) -> None:
    path = tmp_path / "q.csv"
    write_csv(path, ['4- 6.,"100.0 ","50.0 "', ROWS[0]])
    series = load_cabinet_quarterly(path)
    assert [str(p) for p in series.index] == ["1994Q1"]
