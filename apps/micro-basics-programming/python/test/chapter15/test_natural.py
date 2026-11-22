"""第 15 章: 自然独占（限界費用価格形成と平均費用価格形成）のテスト。"""

import pytest

from lib.chapter11.monopoly import Monopoly
from lib.chapter15.natural import (
    average_cost_pricing,
    marginal_cost_pricing,
    natural_average_cost,
    required_subsidy,
    unregulated_outcome,
)

# 逆需要 P = 100 − Q、限界費用 10、固定費用 800
DEMAND = Monopoly(demand_intercept=100, demand_slope=1, marginal_cost=10)
FIXED = 800


def test_平均費用は限界費用に固定費用の分を足した値で右下がり() -> None:
    assert natural_average_cost(DEMAND, FIXED, 40) == pytest.approx(10 + 800 / 40)
    assert natural_average_cost(DEMAND, FIXED, 80) < natural_average_cost(
        DEMAND, FIXED, 40
    )
    assert natural_average_cost(DEMAND, FIXED, 80) > DEMAND.marginal_cost


def test_平均費用の数量は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="数量"):
        natural_average_cost(DEMAND, FIXED, 0)


def test_限界費用価格形成は効率的だが赤字() -> None:
    outcome = marginal_cost_pricing(DEMAND, FIXED)
    assert (outcome.price, outcome.quantity) == (10, 90)
    assert outcome.profit == -800
    assert outcome.consumer_surplus == pytest.approx(4050)
    assert outcome.total_surplus == pytest.approx(4050 - 800)


def test_赤字は固定費用に等しく補助金が必要() -> None:
    assert required_subsidy(DEMAND, FIXED) == 800
    assert marginal_cost_pricing(DEMAND, FIXED).profit == -required_subsidy(
        DEMAND, FIXED
    )


def test_平均費用価格形成は利潤が0で価格が平均費用に等しい() -> None:
    outcome = average_cost_pricing(DEMAND, FIXED)
    assert outcome.quantity == pytest.approx(80)
    assert outcome.price == pytest.approx(20)
    assert outcome.profit == pytest.approx(0, abs=1e-9)
    assert outcome.price == pytest.approx(
        natural_average_cost(DEMAND, FIXED, outcome.quantity)
    )


def test_平均費用価格形成は限界費用価格形成より価格が高く数量が少ない() -> None:
    mc, ac = marginal_cost_pricing(DEMAND, FIXED), average_cost_pricing(DEMAND, FIXED)
    assert ac.price > mc.price
    assert ac.quantity < mc.quantity


def test_規制しない独占は価格が最も高く数量が最も少ない() -> None:
    free = unregulated_outcome(DEMAND, FIXED)
    ac = average_cost_pricing(DEMAND, FIXED)
    assert (free.price, free.quantity) == (55, 45)
    assert free.profit == pytest.approx(2025 - 800)
    assert free.price > ac.price
    assert free.quantity < ac.quantity


def test_総余剰の順は限界費用価格_平均費用価格_独占() -> None:
    mc = marginal_cost_pricing(DEMAND, FIXED).total_surplus
    ac = average_cost_pricing(DEMAND, FIXED).total_surplus
    free = unregulated_outcome(DEMAND, FIXED).total_surplus
    assert mc > ac > free


def test_固定費用が大きすぎると平均費用価格は成り立たない() -> None:
    with pytest.raises(ValueError, match="固定費用"):
        average_cost_pricing(DEMAND, 2100)


def test_固定費用は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="固定費用"):
        marginal_cost_pricing(DEMAND, 0)
    with pytest.raises(ValueError, match="固定費用"):
        required_subsidy(DEMAND, -1)


def test_傾きが違う需要の平均費用価格() -> None:
    steep = Monopoly(demand_intercept=100, demand_slope=2, marginal_cost=10)
    outcome = average_cost_pricing(steep, 400)
    assert outcome.quantity == pytest.approx(40)
    assert outcome.price == pytest.approx(20)
    assert outcome.profit == pytest.approx(0, abs=1e-9)


def test_平均費用が需要曲線に接する固定費用() -> None:
    outcome = average_cost_pricing(DEMAND, 2025)
    assert (outcome.quantity, outcome.price) == (45, 55)
    barely = average_cost_pricing(DEMAND, 2024.9)
    assert barely.quantity == pytest.approx(45 + 0.5 * (0.4**0.5), rel=1e-6)
