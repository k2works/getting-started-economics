"""第 14 章: AD-AS 分析のテスト。第 13 章の標準のモデルから総需要曲線を導く。"""

import dataclasses
from collections.abc import Callable

import pytest

from lib.chapter13.islm import IsLmModel
from lib.chapter14.adas import (
    aggregate_demand,
    classical_supply,
    equilibrium_price_and_income,
    keynesian_supply,
)

FULL_EMPLOYMENT_INCOME = 1250


def classical(price: float) -> float:
    return classical_supply(price, full_employment_income=FULL_EMPLOYMENT_INCOME)


def keynesian_recession(price: float) -> float:
    # 完全雇用所得 1300、完全雇用の物価 1.0、物価が 1 下がるごとに所得は 500 減る
    return keynesian_supply(
        price, full_employment_income=1300, full_employment_price=1.0, slope=500
    )


def test_物価が1のとき総需要は第13章の均衡の所得1250() -> None:
    assert aggregate_demand(IsLmModel(), price_level=1) == pytest.approx(1250)


def test_物価が上がると実質貨幣供給が減り総需要は減る() -> None:
    # 物価 1.1 のとき実質貨幣供給は 525 / 1.1 = 477.27。0.45Y = 300 + 238.64
    assert aggregate_demand(IsLmModel(), price_level=1.1) == pytest.approx(
        1196.97, abs=0.01
    )


def test_総需要曲線は右下がり() -> None:
    prices = [0.8, 0.9, 1.0, 1.1, 1.2]
    demands = [aggregate_demand(IsLmModel(), p) for p in prices]
    assert demands == sorted(demands, reverse=True)


def test_古典派の総供給は物価によらず完全雇用所得で垂直() -> None:
    assert [classical(p) for p in (0.5, 1.0, 2.0)] == [1250, 1250, 1250]


def test_ケインズの総供給は右上がりのあと垂直() -> None:
    assert keynesian_recession(0.8) == pytest.approx(1200)
    assert keynesian_recession(0.9) == pytest.approx(1250)
    assert keynesian_recession(1.0) == pytest.approx(1300)
    assert keynesian_recession(1.5) == pytest.approx(1300)


def test_古典派の均衡の所得は完全雇用所得で物価は1() -> None:
    price, income = equilibrium_price_and_income(IsLmModel(), classical)
    assert price == pytest.approx(1)
    assert income == pytest.approx(1250)


def test_古典派では拡張的な財政政策は物価だけを上げる() -> None:
    expanded = IsLmModel(government=120)
    price, income = equilibrium_price_and_income(expanded, classical)
    assert income == pytest.approx(FULL_EMPLOYMENT_INCOME)
    assert price > 1


def test_古典派では拡張的な金融政策も物価だけを上げる() -> None:
    expanded = IsLmModel(money_supply=575)
    price, income = equilibrium_price_and_income(expanded, classical)
    # 貨幣供給が 575 / 525 倍になれば、物価も同じ倍率で上がる
    assert income == pytest.approx(FULL_EMPLOYMENT_INCOME)
    assert price == pytest.approx(575 / 525)


def test_ケインズの右上がりの部分では所得も物価も上がる() -> None:
    base_price, base_income = equilibrium_price_and_income(
        IsLmModel(), keynesian_recession
    )
    expanded = dataclasses.replace(IsLmModel(), government=120)
    price, income = equilibrium_price_and_income(expanded, keynesian_recession)
    assert base_income < 1300
    assert income > base_income
    assert price > base_price


def test_ケインズの垂直の部分では物価だけが上がる() -> None:
    expanded = dataclasses.replace(IsLmModel(), government=300)
    price, income = equilibrium_price_and_income(expanded, keynesian_recession)
    assert income == pytest.approx(1300)
    assert price > 1


def test_均衡では総需要と総供給が等しい() -> None:
    supply: Callable[[float], float] = keynesian_recession
    price, income = equilibrium_price_and_income(IsLmModel(), supply)
    assert aggregate_demand(IsLmModel(), price) == pytest.approx(income)
    assert supply(price) == pytest.approx(income)
