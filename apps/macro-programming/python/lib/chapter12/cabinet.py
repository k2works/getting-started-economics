"""内閣府の四半期 GDP 速報の CSV（実際の統計）を、四半期の系列に直す。

「四半期別 GDP 速報」の統計表一覧にある、「国内総生産(支出側)及び各需要項目」の
「実質季節調整系列」や「四半期デフレーター季節調整系列」の CSV を読む。
CSV は、文字コードが cp932、先頭の 7 行が見出し。第 1 四半期の行にだけ年が付き
（`1994/ 1- 3.`）、続く行は `4- 6.`・`7- 9.`・`10-12.` の形。
実質 GDP は、年率、2020 暦年連鎖価格、10 億円。デフレーターは、2020 暦年 = 100。
"""

import csv
import re
from pathlib import Path

import numpy as np
import pandas as pd

ENCODING = "cp932"
_YEAR_ROW = re.compile(r"^\s*(\d{4})/\s*(\d{1,2})-\s*(\d{1,2})\.$")
_QUARTER_ROW = re.compile(r"^\s*(\d{1,2})-\s*(\d{1,2})\.$")


def load_cabinet_quarterly(path: Path, column: int = 1) -> pd.Series:
    """四半期の行だけを取り出し、四半期（PeriodIndex）の系列にする。

    column は CSV の列の位置（0 から数える）。1 が、国内総生産(支出側)。
    見出しと注記の行は、読み飛ばす。
    """
    year: int | None = None
    periods = []
    values = []
    with path.open(encoding=ENCODING, newline="") as file:
        for row in csv.reader(file):
            if not row:
                continue
            first_quarter = _YEAR_ROW.match(row[0])
            later_quarter = _QUARTER_ROW.match(row[0])
            if first_quarter:
                year = int(first_quarter.group(1))
                month = int(first_quarter.group(2))
            elif later_quarter and year is not None:
                month = int(later_quarter.group(1))
            else:
                continue
            quarter = (month - 1) // 3 + 1
            periods.append(pd.Period(f"{year}Q{quarter}"))
            values.append(float(row[column].replace(",", "").strip()))
    if not periods:
        raise ValueError("四半期の行がない")
    return pd.Series(values, index=pd.PeriodIndex(periods, freq="Q"))


def year_over_year(series: pd.Series) -> pd.Series:
    """前年同期比（%）= 100 × (ln x(t) − ln x(t−4))。最初の 4 四半期は、除く。"""
    logs = series.apply(np.log)
    return (100 * (logs - logs.shift(4))).dropna()
