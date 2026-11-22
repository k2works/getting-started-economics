import pytest

from lib.chapter05.derivative import Polynomial
from lib.chapter06.supply import aggregate_supply_quantity

# 第 5 章の費用関数（係数は、次数の低い順）
COST = Polynomial((100, 10, 1))  # C(q) = q² + 10q + 100、MC = 2q + 10
COST_HALF = Polynomial((50, 4, 0.5))  # C(q) = 0.5q² + 4q + 50、MC = q + 4
COST_CUBIC = Polynomial((20, 15, -6, 1))  # AVC の最小は q = 3 で 6


@pytest.mark.parametrize("price", [12, 25, 30, 50])
def test_1社の供給は限界費用の右上がりの部分(price: float) -> None:
    assert aggregate_supply_quantity(price, [COST]) == pytest.approx((price - 10) / 2)


def test_価格が限界費用の切片以下なら1社の供給は0() -> None:
    assert aggregate_supply_quantity(10, [COST]) == 0
    assert aggregate_supply_quantity(4, [COST]) == 0


@pytest.mark.parametrize("price", [12, 30, 50])
def test_同じ企業10社の総供給は5かけるp引く10(price: float) -> None:
    total = aggregate_supply_quantity(price, [COST] * 10)
    assert total == pytest.approx(5 * (price - 10))


def test_費用の違う企業の総供給は同じ価格での供給量を足す() -> None:
    # p = 20: (20 − 10) ÷ 2 = 5 と 20 − 4 = 16。p = 8: 0 と 4
    assert aggregate_supply_quantity(20, [COST, COST_HALF]) == pytest.approx(21)
    assert aggregate_supply_quantity(8, [COST, COST_HALF]) == pytest.approx(4)
    assert aggregate_supply_quantity(20, []) == 0


def test_3次の費用の供給は操業停止点で飛ぶ() -> None:
    assert aggregate_supply_quantity(5.9, [COST_CUBIC]) == 0
    jump = aggregate_supply_quantity(6.1, [COST_CUBIC])
    assert jump > 3  # P = MC の右上がりの部分（AVC の最小点 q = 3 より右）
    assert aggregate_supply_quantity(15, [COST_CUBIC] * 2) == pytest.approx(
        2 * aggregate_supply_quantity(15, [COST_CUBIC])
    )
