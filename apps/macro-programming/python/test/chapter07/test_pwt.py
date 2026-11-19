"""第 7 章: Penn World Table（実際の統計）の読み込みのテスト。

公式の Stata ファイルと同じ列名の、小さなファイルを、テストの中で作って使う。
y = cgdpo ÷ emp（就業者 1 人当たりの GDP）、k = cn ÷ emp、h = hc。
"""

from pathlib import Path

import pandas as pd
import pytest

from lib.chapter07.pwt import balanced_countries, load_pwt


def write_dta(path: Path, rows: list[dict[str, object]]) -> None:
    columns = [
        "countrycode",
        "country",
        "year",
        "cgdpo",
        "cn",
        "emp",
        "hc",
        "pop",
        "pl_gdpo",
        "rgdpe",
    ]
    df = pd.DataFrame(rows, columns=columns)
    df.to_stata(path, write_index=False)


def row(code: str, year: int, **overrides: float) -> dict[str, object]:
    values: dict[str, object] = {
        "countrycode": code,
        "country": f"Country {code}",
        "year": year,
        "cgdpo": 1000.0,
        "cn": 3000.0,
        "emp": 10.0,
        "hc": 2.0,
        "pop": 20.0,
        "pl_gdpo": 0.5,
        "rgdpe": 999.0,
    }
    values.update(overrides)
    return values


@pytest.fixture
def dta(tmp_path: Path) -> Path:
    path = tmp_path / "pwt.dta"
    write_dta(
        path,
        [
            row("AAA", 2018),
            row("AAA", 2019, cgdpo=1100.0),
            row("BBB", 2018, hc=float("nan")),
            row("BBB", 2019, emp=0.0),
            row("BBB", 2020),
        ],
    )
    return path


def test_国と年が行の名前になる(dta: Path) -> None:
    df = load_pwt(dta)
    assert list(df.index.names) == ["country", "year"]
    assert df.index.get_level_values("country").unique().tolist() == ["AAA", "BBB"]


def test_列の値は元の変数から計算される(dta: Path) -> None:
    df = load_pwt(dta)
    key = ("AAA", 2018)
    assert df.loc[key, "y"] == pytest.approx(1000 / 10)
    assert df.loc[key, "k"] == pytest.approx(3000 / 10)
    assert df.loc[key, "h"] == pytest.approx(2.0)
    assert df.loc[key, "income_pc"] == pytest.approx(1000 / 20)
    assert df.loc[key, "price_level"] == pytest.approx(0.5)
    assert df.loc[("AAA", 2019), "y"] == pytest.approx(110)


def test_使う列だけを返す(dta: Path) -> None:
    assert list(load_pwt(dta).columns) == ["y", "k", "h", "income_pc", "price_level"]


def test_欠けた値のある行は除く(dta: Path) -> None:
    df = load_pwt(dta)
    assert ("BBB", 2018) not in df.index


def test_就業者が0の行は除く(dta: Path) -> None:
    df = load_pwt(dta)
    assert ("BBB", 2019) not in df.index
    assert ("BBB", 2020) in df.index


def test_全年がそろう国だけを残す(dta: Path) -> None:
    df = load_pwt(dta)
    kept = balanced_countries(df, 2018, 2019)
    assert kept.index.get_level_values("country").unique().tolist() == ["AAA"]
    assert len(kept) == 2


def test_期間の外の年は残さない(dta: Path) -> None:
    kept = balanced_countries(load_pwt(dta), 2018, 2019)
    assert set(kept.index.get_level_values("year")) == {2018, 2019}


def test_期間の始まりは終わりより前でなければならない(dta: Path) -> None:
    with pytest.raises(ValueError, match="期間"):
        balanced_countries(load_pwt(dta), 2019, 2018)


def test_期間が0年でも受け付けない(dta: Path) -> None:
    with pytest.raises(ValueError, match="期間"):
        balanced_countries(load_pwt(dta), 2018, 2018)
