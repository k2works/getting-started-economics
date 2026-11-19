"""第 11 章: 内閣府の国民経済計算（暦年の CSV）の読み込みのテスト。

公式の CSV と同じ構造（cp932、ヘッダ 7 行、数値は 3 桁区切り、単位は 10 億円）の
小さなファイルを、テストの中で作って使う。
"""

from pathlib import Path

import pytest

from lib.chapter11.economy import expenditure_gdp
from lib.chapter11.sna import load_sna_expenditure

HEADER = [
    "項目 / 年,,,,,,,,,,,,,,,<参考>",
    '"Nominal, Calendar Year",,,,,,,,,,,,,,,<cf>',
    ",国内総生産(支出側),民間最終消費支出",
    ",,,家計最終消費支出",
    ",,,,",
    ",GDP(Expenditure Approach),PrivateConsumption",
    "Calendar Year,,,,,,,,,,,Net Exports,Exports,Imports",
]


def data_row(year: int, values: dict[int, str], width: int = 27) -> str:
    cells = [""] * width
    cells[0] = f"{year}/1-12."
    for index, text in values.items():
        cells[index] = text
    return ",".join(f'"{c}"' if "," in c else c for c in cells)


def write_csv(path: Path, rows: list[str], trailer: list[str] | None = None) -> None:
    lines = [*HEADER, *rows, *(trailer or ["", "注：数値は速報値である。"])]
    path.write_text("\n".join(lines) + "\n", encoding="cp932")


# 位置: 1=GDP、2=民間消費、5=民間住宅、6=民間企業設備、7=民間在庫、8=政府消費、
#       9=公的固定資本形成、10=公的在庫、12=輸出、13=輸入（単位: 10 億円）
NOMINAL_2000 = {
    1: "1,000.0", 2: "600.0", 5: "40.0", 6: "100.0", 7: "-10.0", 8: "150.0",
    9: "50.0", 10: "5.0", 12: "120.0", 13: "55.0",
}  # fmt: skip
NOMINAL_2001 = {
    1: "1,030.0", 2: "612.0", 5: "41.0", 6: "104.0", 7: "-8.0", 8: "154.0",
    9: "51.0", 10: "4.0", 12: "124.0", 13: "52.0",
}  # fmt: skip


@pytest.fixture
def files(tmp_path: Path) -> tuple[Path, Path]:
    nominal = tmp_path / "nominal.csv"
    deflator = tmp_path / "deflator.csv"
    write_csv(nominal, [data_row(2000, NOMINAL_2000), data_row(2001, NOMINAL_2001)])
    write_csv(
        deflator,
        [data_row(2000, {1: "98.5"}), data_row(2001, {1: "97.9"})],
    )
    return nominal, deflator


def test_年を行の名前にして支出の5項目とデフレーターの列を返す(
    files: tuple[Path, Path],
) -> None:
    df = load_sna_expenditure(*files)
    assert list(df.index) == [2000, 2001]
    assert list(df.columns) == [
        "consumption",
        "investment",
        "government",
        "exports",
        "imports",
        "deflator",
    ]


def test_単位は10億円から兆円に直す(files: tuple[Path, Path]) -> None:
    df = load_sna_expenditure(*files)
    assert df.loc[2000, "consumption"] == pytest.approx(0.6)
    assert df.loc[2000, "exports"] == pytest.approx(0.12)


def test_投資は民間住宅_民間企業設備_民間在庫_公的固定資本形成_公的在庫の合計(
    files: tuple[Path, Path],
) -> None:
    df = load_sna_expenditure(*files)
    assert df.loc[2000, "investment"] == pytest.approx((40 + 100 - 10 + 50 + 5) / 1000)


def test_政府支出は政府最終消費支出(files: tuple[Path, Path]) -> None:
    assert load_sna_expenditure(*files).loc[2001, "government"] == pytest.approx(0.154)


def test_支出面の合計は公表されたGDPと一致する(files: tuple[Path, Path]) -> None:
    gdp = expenditure_gdp(load_sna_expenditure(*files))
    assert gdp[2000] == pytest.approx(1.0)
    assert gdp[2001] == pytest.approx(1.03)


def test_デフレーターは別のファイルから読む(files: tuple[Path, Path]) -> None:
    df = load_sna_expenditure(*files)
    assert df.loc[2000, "deflator"] == pytest.approx(98.5)


def test_年の行ではない注記の行は読み飛ばす(tmp_path: Path) -> None:
    nominal = tmp_path / "n.csv"
    deflator = tmp_path / "d.csv"
    notes = ["", ",,,", "注：2025 年は速報から計算した値である。"]
    write_csv(nominal, [data_row(2000, NOMINAL_2000)], trailer=notes)
    write_csv(deflator, [data_row(2000, {1: "98.5"})], trailer=notes)
    assert list(load_sna_expenditure(nominal, deflator).index) == [2000]


def test_2つのファイルで年がそろわなければ受け付けない(tmp_path: Path) -> None:
    nominal = tmp_path / "n.csv"
    deflator = tmp_path / "d.csv"
    write_csv(nominal, [data_row(2000, NOMINAL_2000), data_row(2001, NOMINAL_2001)])
    write_csv(deflator, [data_row(2000, {1: "98.5"})])
    with pytest.raises(ValueError, match="年"):
        load_sna_expenditure(nominal, deflator)
