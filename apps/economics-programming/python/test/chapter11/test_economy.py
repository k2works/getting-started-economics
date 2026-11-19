"""第 11 章: pandas による経済データ分析のテスト。"""

import math

import pandas as pd
import pytest

from lib.chapter11.economy import (
    expenditure_gdp,
    expenditure_shares,
    growth_rates,
    income_gdp,
    laspeyres_index,
    load_economy,
    paasche_index,
    production_gdp,
    real_gdp,
    recession_years,
    statistical_discrepancy,
)


@pytest.fixture
def economy() -> pd.DataFrame:
    return load_economy()


def test_データは2010年から2021年までの12年分() -> None:
    df = load_economy()
    assert df.shape == (12, 12)
    assert list(df.index) == list(range(2010, 2022))


def test_列の名前を確かめる() -> None:
    df = load_economy()
    assert list(df.columns[:3]) == ["primary", "secondary", "tertiary"]
    assert "deflator" in df.columns


def test_生産面のGDPは3つの産業の付加価値の合計(economy: pd.DataFrame) -> None:
    # 2010 年: 14 + 130 + 336、2015 年: 16 + 146 + 379
    assert production_gdp(economy)[2010] == 480
    assert production_gdp(economy)[2015] == 541


def test_分配面のGDPは雇用者報酬と営業余剰と固定資本減耗と間接税の合計(
    economy: pd.DataFrame,
) -> None:
    # 2010 年: 250 + 124 + 106
    assert income_gdp(economy)[2010] == 480


def test_生産面と分配面のGDPは全年で一致する(economy: pd.DataFrame) -> None:
    assert (production_gdp(economy) == income_gdp(economy)).all()


def test_支出面のGDPは消費と投資と政府支出と純輸出の合計(
    economy: pd.DataFrame,
) -> None:
    # 2010 年: 264 + 110 + 96 + (82 - 72)
    assert expenditure_gdp(economy)[2010] == 480


def test_統計上の不突合は生産面から支出面を引いた差(economy: pd.DataFrame) -> None:
    gap = statistical_discrepancy(economy)
    assert gap[2010] == 0
    # 2011 年: 生産面 492、支出面 271 + 113 + 98 + (84 - 75) = 491
    assert gap[2011] == 1


def test_統計上の不突合はGDPの1パーセント未満(economy: pd.DataFrame) -> None:
    ratio = statistical_discrepancy(economy).abs() / production_gdp(economy)
    assert (ratio < 0.01).all()


def test_基準年の実質GDPは名目GDPと等しい(economy: pd.DataFrame) -> None:
    # デフレーターは 2015 年が 100
    assert real_gdp(economy)[2015] == pytest.approx(production_gdp(economy)[2015])


def test_名目GDPが同じでも物価が上がれば実質GDPは減る(
    economy: pd.DataFrame,
) -> None:
    nominal = production_gdp(economy)
    real = real_gdp(economy)
    assert nominal[2013] == nominal[2012]
    assert real[2013] < real[2012]


def test_成長率の最初の年は計算できない(economy: pd.DataFrame) -> None:
    assert math.isnan(growth_rates(real_gdp(economy))[2010])


def test_2020年の実質成長率はおよそマイナス3パーセント(
    economy: pd.DataFrame,
) -> None:
    # 実質 GDP は 2019 年が 599 / 1.032、2020 年が 580 / 1.030
    assert growth_rates(real_gdp(economy))[2020] == pytest.approx(-3.0, abs=0.1)


def test_実質成長率がマイナスの年は2013年と2020年(economy: pd.DataFrame) -> None:
    assert recession_years(economy) == [2013, 2020]


def test_2015年の支出の構成比(economy: pd.DataFrame) -> None:
    shares = expenditure_shares(economy, 2015)
    # GDP 541 のうち、消費 298、投資 124、政府支出 108、純輸出 92 - 80
    assert shares["consumption"] == pytest.approx(298 / 541 * 100)
    assert shares["investment"] == pytest.approx(124 / 541 * 100)
    assert shares["government"] == pytest.approx(108 / 541 * 100)
    assert shares["net_exports"] == pytest.approx(12 / 541 * 100)


def test_存在しない年の構成比は求められない(economy: pd.DataFrame) -> None:
    with pytest.raises(KeyError):
        expenditure_shares(economy, 1999)


def test_ラスパイレス指数は基準年の数量で価格の変化を測る() -> None:
    # (110 * 10 + 190 * 5) / (100 * 10 + 200 * 5) = 2050 / 2000
    result = laspeyres_index(
        base_prices=[100, 200], base_quantities=[10, 5], current_prices=[110, 190]
    )
    assert result == pytest.approx(102.5)


def test_パーシェ指数は比較年の数量で価格の変化を測る() -> None:
    # (110 * 8 + 190 * 6) / (100 * 8 + 200 * 6) = 2020 / 2000
    result = paasche_index(
        base_prices=[100, 200], current_prices=[110, 190], current_quantities=[8, 6]
    )
    assert result == pytest.approx(101.0)


def test_財の数が合わない指数は求められない() -> None:
    with pytest.raises(ValueError):
        laspeyres_index(
            base_prices=[100, 200], base_quantities=[10], current_prices=[110, 190]
        )
