"""内閣府の国民経済計算（暦年の CSV）を、この章の表の形に直す。

内閣府・経済社会総合研究所の「四半期別 GDP 速報」の統計表一覧にある、
「国内総生産(支出側)及び各需要項目」の「名目暦年」と「暦年デフレーター」の CSV を読む。
CSV は、文字コードが cp932、先頭の 7 行が見出し、数値は 3 桁区切り、
金額の単位は 10 億円。この章の表（兆円）に合わせて、1000 で割る。
"""

import csv
import re
from pathlib import Path

import pandas as pd

ENCODING = "cp932"
_YEAR_ROW = re.compile(r"^(\d{4})/1-12\.$")
# 金額の単位: 10 億円 → 兆円
_UNIT = 1000

# CSV の列の位置（0 から数える）
_GDP = 1
_PRIVATE_CONSUMPTION = 2
# 投資: 民間住宅・民間企業設備・民間在庫・公的固定資本形成・公的在庫
_INVESTMENT_COLUMNS = (5, 6, 7, 9, 10)
_GOVERNMENT_CONSUMPTION = 8
_EXPORTS = 12
_IMPORTS = 13


def _read_calendar_years(path: Path) -> dict[int, list[str]]:
    """「2020/1-12.」の形の行だけを、年ごとに取り出す（見出しや注記は読み飛ばす）。"""
    rows: dict[int, list[str]] = {}
    with path.open(encoding=ENCODING, newline="") as file:
        for row in csv.reader(file):
            match = _YEAR_ROW.match(row[0]) if row else None
            if match:
                rows[int(match.group(1))] = row
    return rows


def _number(row: list[str], column: int) -> float:
    return float(row[column].replace(",", ""))


def load_sna_expenditure(nominal_path: Path, deflator_path: Path) -> pd.DataFrame:
    """支出側の名目 GDP の CSV と、デフレーターの CSV から、この章の表を作る。

    列は、consumption・investment・government・exports・imports（兆円）と
    deflator（GDP デフレーター。基準年は、CSV に書かれた年で 100）。
    投資には、在庫と公的固定資本形成も含める。
    """
    nominal = _read_calendar_years(nominal_path)
    deflator = _read_calendar_years(deflator_path)
    if nominal.keys() != deflator.keys():
        raise ValueError("名目 GDP とデフレーターの CSV で、年がそろっていない")
    records = {
        year: {
            "consumption": _number(row, _PRIVATE_CONSUMPTION) / _UNIT,
            "investment": sum(_number(row, c) for c in _INVESTMENT_COLUMNS) / _UNIT,
            "government": _number(row, _GOVERNMENT_CONSUMPTION) / _UNIT,
            "exports": _number(row, _EXPORTS) / _UNIT,
            "imports": _number(row, _IMPORTS) / _UNIT,
            "deflator": _number(deflator[year], _GDP),
        }
        for year, row in sorted(nominal.items())
    }
    return pd.DataFrame.from_dict(records, orient="index")
