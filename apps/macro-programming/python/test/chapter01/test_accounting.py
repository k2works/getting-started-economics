"""第 1 章: 発展会計のテスト。

生産関数 y = A · k^α · h^(1−α)。α = 1/3 の例では、8^(1/3) = 2 なので、手計算できる。
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lib.chapter01.accounting import (
    income_gap,
    load_countries,
    tfp,
    variance_shares,
    with_tfp,
)

ALPHA = 1 / 3


def two_countries() -> pd.DataFrame:
    """基準の国（A = 1、k = 8、h = 1、y = 2）と、貧しい国（A = 0.5、k = 1、h = 1）。"""
    return pd.DataFrame(
        {"y": [2.0, 0.5], "k": [8.0, 1.0], "h": [1.0, 1.0]},
        index=pd.Index(["rich", "poor"], name="country"),
    )


def test_TFPは所得を資本と人的資本の寄与で割った残差() -> None:
    # k^(1/3) = 2、h^(2/3) = 1 なので、y = 2 のとき、A = 2 ÷ 2 = 1
    assert tfp(output=2, capital=8, human_capital=1, alpha=ALPHA) == pytest.approx(1)


def test_資本と人的資本が同じでも所得が2倍ならTFPも2倍() -> None:
    low = tfp(output=2, capital=8, human_capital=1, alpha=ALPHA)
    high = tfp(output=4, capital=8, human_capital=1, alpha=ALPHA)
    assert high == pytest.approx(2 * low)


def test_資本分配率が0_5のとき() -> None:
    # y = 4、k = 4、h = 4 のとき、A = 4 ÷ (4^0.5 × 4^0.5) = 1
    assert tfp(output=4, capital=4, human_capital=4, alpha=0.5) == pytest.approx(1)


@pytest.mark.parametrize("alpha", [0, 1, -0.1, 1.5])
def test_資本分配率は0より大きく1より小さくなければならない(alpha: float) -> None:
    with pytest.raises(ValueError, match="資本分配率"):
        tfp(output=2, capital=8, human_capital=1, alpha=alpha)


@pytest.mark.parametrize("name", ["output", "capital", "human_capital"])
def test_所得_資本_人的資本は正でなければならない(name: str) -> None:
    values = {"output": 2.0, "capital": 8.0, "human_capital": 1.0}
    values[name] = 0.0
    with pytest.raises(ValueError, match="正"):
        tfp(**values, alpha=ALPHA)


def test_CSVを読むと国名が行の名前になる(tmp_path: Path) -> None:
    path = tmp_path / "countries.csv"
    path.write_text("country,y,k,h\nA,2.0,8.0,1.0\nB,0.5,1.0,1.0\n", encoding="utf-8")
    df = load_countries(path)
    assert list(df.index) == ["A", "B"]
    assert list(df.columns) == ["y", "k", "h"]
    assert df.loc["A", "k"] == 8.0


def test_同梱のデータは24か国で所得の高い順に並んでいる() -> None:
    df = load_countries()
    assert len(df) == 24
    assert df.index[0] == "C01"
    assert df["y"].is_monotonic_decreasing


def test_TFPの列を足しても元の表は変わらない() -> None:
    df = two_countries()
    result = with_tfp(df, ALPHA)
    assert result["tfp"].tolist() == pytest.approx([1.0, 0.5])
    assert "tfp" not in df.columns


def test_基準の国との所得の差を3つの寄与に分ける() -> None:
    gap = income_gap(two_countries(), reference="rich", alpha=ALPHA)
    # 所得の差 ln(0.5 ÷ 2) = ln(1 ÷ 4)。資本 (1/3)·ln(1 ÷ 8)、人的資本 0、TFP ln(0.5)
    assert gap.loc["poor", "total"] == pytest.approx(np.log(0.25))
    assert gap.loc["poor", "capital"] == pytest.approx(np.log(1 / 8) / 3)
    assert gap.loc["poor", "human_capital"] == pytest.approx(0)
    assert gap.loc["poor", "tfp"] == pytest.approx(np.log(0.5))


def test_所得の差の半分は資本で半分はTFP() -> None:
    gap = income_gap(two_countries(), reference="rich", alpha=ALPHA)
    row = gap.loc["poor"]
    assert row["capital"] / row["total"] == pytest.approx(0.5)
    assert row["tfp"] / row["total"] == pytest.approx(0.5)


def test_基準の国の寄与はすべて0() -> None:
    gap = income_gap(two_countries(), reference="rich", alpha=ALPHA)
    assert gap.loc["rich"].to_numpy() == pytest.approx([0, 0, 0, 0])


def test_3つの寄与の和は所得の差と等しい() -> None:
    gap = income_gap(load_countries(), reference="C01", alpha=ALPHA)
    parts = gap["capital"] + gap["human_capital"] + gap["tfp"]
    assert parts.to_numpy() == pytest.approx(gap["total"].to_numpy())


def test_基準の国がデータにないときは受け付けない() -> None:
    with pytest.raises(ValueError, match="基準の国"):
        income_gap(two_countries(), reference="nowhere", alpha=ALPHA)


def test_分散の割合は3つで合計1() -> None:
    shares = variance_shares(load_countries(), alpha=ALPHA)
    assert shares.sum() == pytest.approx(1)
    assert list(shares.index) == ["capital", "human_capital", "tfp"]


def test_同梱のデータではTFPが所得の分散の6割を説明する() -> None:
    shares = variance_shares(load_countries(), alpha=ALPHA)
    assert shares["tfp"] == pytest.approx(0.615, abs=0.001)
    assert shares["capital"] == pytest.approx(0.257, abs=0.001)
    assert shares["human_capital"] == pytest.approx(0.128, abs=0.001)


def test_所得の差がすべてTFPの差ならTFPの割合は1() -> None:
    a = np.array([0.5, 1.0, 2.0, 4.0])
    df = pd.DataFrame(
        {"y": a * 2.0, "k": [8.0] * 4, "h": [1.0] * 4},
        index=pd.Index(list("wxyz"), name="country"),
    )
    shares = variance_shares(df, alpha=ALPHA)
    assert shares["tfp"] == pytest.approx(1)
    assert shares["capital"] == pytest.approx(0)


def test_所得に差がなければ分散の割合は求められない() -> None:
    df = pd.DataFrame(
        {"y": [2.0, 2.0], "k": [8.0, 1.0], "h": [1.0, 1.0]},
        index=pd.Index(["a", "b"], name="country"),
    )
    with pytest.raises(ValueError, match="差"):
        variance_shares(df, alpha=ALPHA)


def test_表に正でない値があればTFPは求められない() -> None:
    df = two_countries()
    df.loc["poor", "k"] = 0.0
    with pytest.raises(ValueError, match="正"):
        with_tfp(df, ALPHA)
