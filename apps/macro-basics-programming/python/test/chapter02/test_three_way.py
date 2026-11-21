"""第 2 章: 三面等価のテスト。"""

import pytest

from lib.chapter02.three_way import (
    gdp_distribution,
    gdp_expenditure,
    gdp_production,
    inventory_change,
    is_three_way_equal,
)

# 3 つの産業の産出額と、中間投入（億円）。付加価値の合計が 500
OUTPUT = [300, 500, 700]
INTERMEDIATE = [200, 300, 500]


def test_生産面のGDPは産出額の合計から中間投入の合計を引いた値() -> None:
    assert gdp_production(OUTPUT, INTERMEDIATE) == 500


def test_生産面は産業の数が違えばエラー() -> None:
    with pytest.raises(ValueError, match="同じ長さ"):
        gdp_production([300, 500], [200])


def test_分配面のGDPは4つの所得の合計() -> None:
    gdp = gdp_distribution(
        compensation=280,
        operating_surplus=120,
        depreciation=80,
        indirect_taxes=25,
        subsidies=5,
    )
    assert gdp == 500


def test_分配面は間接税から補助金を引く() -> None:
    base = gdp_distribution(280, 120, 80, indirect_taxes=25, subsidies=5)
    more = gdp_distribution(280, 120, 80, indirect_taxes=25, subsidies=15)
    assert base - more == 10


def test_支出面のGDPは5つの需要の合計() -> None:
    gdp = gdp_expenditure(
        consumption=290,
        government=80,
        fixed_capital_formation=100,
        inventory=10,
        net_exports=20,
    )
    assert gdp == 500
    assert gdp_expenditure(290, 80, 100, 10, net_exports=-20) == 460


def test_在庫品増加は生産から販売を引いた値で在庫の取り崩しは負() -> None:
    assert inventory_change(production=500, sales=490) == 10
    assert inventory_change(production=490, sales=490) == 0
    assert inventory_change(production=480, sales=490) == -10


@pytest.mark.parametrize("sales", [470, 500, 520])
def test_在庫品増加を含めれば支出面は販売によらず生産面に一致する(sales: float) -> None:
    production = 500
    inventory = inventory_change(production, sales)
    # 販売 sales を、消費・政府消費・総固定資本形成・純輸出に分けて数える
    expenditure = gdp_expenditure(sales - 200, 80, 100, inventory, 20)
    assert expenditure == production


def test_3つの面が等しければ三面等価が成り立つ() -> None:
    assert is_three_way_equal(500, 500, 500)


def test_どれか1つの面がずれれば三面等価は成り立たない() -> None:
    assert not is_three_way_equal(501, 500, 500)
    assert not is_three_way_equal(500, 501, 500)
    assert not is_three_way_equal(500, 500, 501)


def test_三面等価の判定は小さな誤差を許す() -> None:
    assert is_three_way_equal(500, 500 + 1e-12, 500)
    assert not is_three_way_equal(500, 500.01, 500)
    assert is_three_way_equal(500, 500.5, 500, tolerance=1)
    # 誤差ちょうどは許す。面の順序によらず、最大と最小の差で見る
    assert is_three_way_equal(500, 501, 500, tolerance=1)
    assert not is_three_way_equal(499, 500, 501, tolerance=1)
