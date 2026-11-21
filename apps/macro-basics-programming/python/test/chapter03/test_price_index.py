"""第 3 章: 物価指数と GDP デフレータのテスト。"""

import pandas as pd
import pytest

from lib.chapter03.price_index import (
    gdp_deflator,
    laspeyres,
    paasche,
    price_indexes,
    real_gdp,
)

# 2 つの財（パンと牛乳）の、基準時と比較時の価格・数量
BASE_PRICES = [100, 200]
BASE_QUANTITIES = [10, 5]
PRICES = [110, 180]
QUANTITIES = [12, 4]

# 3 つの年の価格と数量の表（行は年、列は財）
PRICE_TABLE = pd.DataFrame(
    {"bread": [100, 110, 121], "milk": [200, 180, 170]},
    index=["2020", "2021", "2022"],
)
QUANTITY_TABLE = pd.DataFrame(
    {"bread": [10, 12, 14], "milk": [5, 4, 3]},
    index=["2020", "2021", "2022"],
)


def test_ラスパイレスは基準時の数量で比較時の価格を評価する() -> None:
    # (110 × 10 + 180 × 5) ÷ (100 × 10 + 200 × 5) = 2000 ÷ 2000
    assert laspeyres(BASE_PRICES, BASE_QUANTITIES, PRICES) == pytest.approx(1.0)


def test_パーシェは比較時の数量で価格の変化を評価する() -> None:
    # (110 × 12 + 180 × 4) ÷ (100 × 12 + 200 × 4) = 2040 ÷ 2000
    assert paasche(BASE_PRICES, PRICES, QUANTITIES) == pytest.approx(1.02)


def test_価格が変わらなければどちらも1() -> None:
    assert laspeyres(BASE_PRICES, BASE_QUANTITIES, BASE_PRICES) == 1
    assert paasche(BASE_PRICES, BASE_PRICES, QUANTITIES) == 1


def test_数量が変わらなければラスパイレスとパーシェは一致する() -> None:
    assert paasche(BASE_PRICES, PRICES, BASE_QUANTITIES) == pytest.approx(
        laspeyres(BASE_PRICES, BASE_QUANTITIES, PRICES)
    )


def test_ラスパイレスは比較時の数量によらない() -> None:
    # 数量を渡す引数がないので、比較時の数量が変わっても、値は同じ
    assert laspeyres(BASE_PRICES, BASE_QUANTITIES, PRICES) == pytest.approx(1.0)
    # 高くなった財を減らし、安くなった財を増やすと、パーシェは、ラスパイレスより小さい
    assert paasche(BASE_PRICES, PRICES, [8, 6]) == pytest.approx(0.98)


def test_品目の数が違えばエラー() -> None:
    with pytest.raises(ValueError, match="品目の数"):
        laspeyres([100, 200], [10], [110, 180])
    with pytest.raises(ValueError, match="品目の数"):
        paasche([100, 200], [110], [12, 4])


def test_基準時の支出が0ならエラー() -> None:
    with pytest.raises(ValueError, match="基準時の支出が 0"):
        laspeyres([0, 0], [10, 5], [110, 180])
    with pytest.raises(ValueError, match="基準時の支出が 0"):
        paasche([0, 0], [110, 180], [12, 4])


def test_実質GDPは名目GDPをデフレータで割って100をかけた値() -> None:
    assert real_gdp(nominal=2040, deflator=102) == pytest.approx(2000)


def test_名目GDPは実質GDPにデフレータをかけて100で割った値() -> None:
    real = 2000
    deflator = gdp_deflator(nominal=2040, real=real)
    assert deflator == pytest.approx(102)
    assert real * deflator / 100 == pytest.approx(2040)


def test_GDPデフレータは基準時価格で測った実質GDPで名目GDPを割る() -> None:
    nominal = sum(p * q for p, q in zip(PRICES, QUANTITIES, strict=True))
    real = sum(p * q for p, q in zip(BASE_PRICES, QUANTITIES, strict=True))
    assert (nominal, real) == (2040, 2000)
    assert gdp_deflator(nominal, real) == pytest.approx(
        100 * paasche(BASE_PRICES, PRICES, QUANTITIES)
    )


def test_デフレータが0以下か実質GDPが0ならエラー() -> None:
    with pytest.raises(ValueError, match="デフレータ"):
        real_gdp(2040, 0)
    with pytest.raises(ValueError, match="デフレータ"):
        real_gdp(2040, -1)
    with pytest.raises(ValueError, match="実質 GDP"):
        gdp_deflator(2040, 0)


def test_表の物価指数はラスパイレスとパーシェの列() -> None:
    table = price_indexes(PRICE_TABLE, QUANTITY_TABLE, base="2020")
    assert list(table.columns) == ["laspeyres", "paasche"]
    assert list(table.index) == ["2020", "2021", "2022"]
    assert table["laspeyres"].tolist() == pytest.approx([1.0, 1.0, 1.03])
    assert table["paasche"].tolist() == pytest.approx([1.0, 1.02, 1.102])


def test_表の物価指数は1つずつ計算した値に一致する() -> None:
    table = price_indexes(PRICE_TABLE, QUANTITY_TABLE, base="2020")
    assert table.loc["2021", "laspeyres"] == pytest.approx(
        laspeyres(BASE_PRICES, BASE_QUANTITIES, PRICES)
    )
    assert table.loc["2021", "paasche"] == pytest.approx(
        paasche(BASE_PRICES, PRICES, QUANTITIES)
    )


def test_基準時の指数は1() -> None:
    table = price_indexes(PRICE_TABLE, QUANTITY_TABLE, base="2021")
    assert list(table.loc["2021"]) == pytest.approx([1.0, 1.0])


def test_表の形が合わなければエラー() -> None:
    with pytest.raises(ValueError, match="期間と品目"):
        price_indexes(PRICE_TABLE, QUANTITY_TABLE.iloc[:2], base="2020")
    with pytest.raises(ValueError, match="期間と品目"):
        price_indexes(
            PRICE_TABLE, QUANTITY_TABLE.rename(columns={"milk": "tea"}), "2020"
        )


def test_基準時が表になければエラー() -> None:
    with pytest.raises(ValueError, match="基準時"):
        price_indexes(PRICE_TABLE, QUANTITY_TABLE, base="1999")


def test_表の基準時の支出が0ならエラー() -> None:
    zero = QUANTITY_TABLE.copy()
    zero.loc["2020"] = 0
    with pytest.raises(ValueError, match="支出が 0"):
        price_indexes(PRICE_TABLE, zero, base="2020")
    zero = QUANTITY_TABLE.copy()
    zero.loc["2022"] = 0
    with pytest.raises(ValueError, match="支出が 0"):
        price_indexes(PRICE_TABLE, zero, base="2020")
