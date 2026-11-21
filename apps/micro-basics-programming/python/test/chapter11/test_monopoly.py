"""第 11 章: 独占と独占的競争のテスト。"""

import math

import pytest

from lib.chapter11.monopoly import (
    Monopoly,
    competitive_outcome,
    deadweight_loss,
    demand_elasticity,
    lerner_index,
    long_run_monopolistic_competition,
    marginal_revenue,
    monopolistic_competition_profit,
    monopoly_outcome,
    price_at,
)

# 逆需要 P = 100 − Q、限界費用 10。独占は Q = 45、P = 55。完全競争は Q = 90、P = 10
MONOPOLY = Monopoly(demand_intercept=100, demand_slope=1, marginal_cost=10)


def test_逆需要は数量が増えると価格が下がる() -> None:
    assert price_at(MONOPOLY, 0) == 100
    assert price_at(MONOPOLY, 45) == 55
    assert price_at(MONOPOLY, 100) == 0


def test_需要の範囲外の数量はエラー() -> None:
    with pytest.raises(ValueError, match="数量"):
        price_at(MONOPOLY, -1)
    with pytest.raises(ValueError, match="数量"):
        price_at(MONOPOLY, 101)


def test_限界収入は需要曲線の2倍の傾き() -> None:
    assert marginal_revenue(MONOPOLY, 0) == 100
    assert marginal_revenue(MONOPOLY, 45) == 10
    drop_price = price_at(MONOPOLY, 10) - price_at(MONOPOLY, 20)
    drop_revenue = marginal_revenue(MONOPOLY, 10) - marginal_revenue(MONOPOLY, 20)
    assert drop_revenue == 2 * drop_price


def test_傾きが違う需要の限界収入() -> None:
    steep = Monopoly(demand_intercept=100, demand_slope=2, marginal_cost=10)
    assert marginal_revenue(steep, 10) == 100 - 4 * 10


def test_独占の数量と価格は限界収入と限界費用が等しい点() -> None:
    outcome = monopoly_outcome(MONOPOLY)
    assert outcome.quantity == 45
    assert outcome.price == 55
    assert marginal_revenue(MONOPOLY, outcome.quantity) == MONOPOLY.marginal_cost


def test_独占の利潤と消費者余剰() -> None:
    outcome = monopoly_outcome(MONOPOLY)
    assert outcome.profit == 2025
    assert outcome.consumer_surplus == pytest.approx(1012.5)
    assert outcome.total_surplus == pytest.approx(3037.5)


def test_完全競争では価格は限界費用で数量は多い() -> None:
    outcome = competitive_outcome(MONOPOLY)
    assert outcome.price == 10
    assert outcome.quantity == 90
    assert outcome.profit == 0
    assert outcome.consumer_surplus == pytest.approx(4050)
    assert outcome.total_surplus == pytest.approx(4050)


def test_独占は完全競争より価格が高く数量が少ない() -> None:
    mono, comp = monopoly_outcome(MONOPOLY), competitive_outcome(MONOPOLY)
    assert mono.price > comp.price
    assert mono.quantity < comp.quantity


def test_独占の死荷重は総余剰の差() -> None:
    assert deadweight_loss(MONOPOLY) == pytest.approx(1012.5)
    assert deadweight_loss(MONOPOLY) == pytest.approx(
        competitive_outcome(MONOPOLY).total_surplus
        - monopoly_outcome(MONOPOLY).total_surplus
    )


def test_限界費用が高い独占() -> None:
    high = Monopoly(demand_intercept=100, demand_slope=1, marginal_cost=40)
    assert (monopoly_outcome(high).quantity, monopoly_outcome(high).price) == (30, 70)
    assert (competitive_outcome(high).quantity, competitive_outcome(high).price) == (
        60,
        40,
    )


def test_傾きが違う需要の独占() -> None:
    steep = Monopoly(demand_intercept=100, demand_slope=2, marginal_cost=10)
    outcome = monopoly_outcome(steep)
    assert (outcome.quantity, outcome.price) == (22.5, 55)
    assert competitive_outcome(steep).quantity == 45


def test_限界費用0なら独占は需要曲線の中点で作る() -> None:
    free = Monopoly(demand_intercept=100, demand_slope=1, marginal_cost=0)
    outcome = monopoly_outcome(free)
    assert (outcome.quantity, outcome.price) == (50, 50)
    assert demand_elasticity(free, outcome.quantity) == pytest.approx(1)


def test_独占の仮定のチェック() -> None:
    with pytest.raises(ValueError, match="傾き"):
        Monopoly(100, 0, 10)
    with pytest.raises(ValueError, match="限界費用"):
        Monopoly(100, 1, -1)
    with pytest.raises(ValueError, match="切片"):
        Monopoly(10, 1, 10)


def test_価格弾力性は価格を数量と傾きで割った値() -> None:
    assert demand_elasticity(MONOPOLY, 45) == pytest.approx(55 / 45)
    assert demand_elasticity(MONOPOLY, 90) == pytest.approx(10 / 90)


def test_弾力性は数量が正でなければ求められない() -> None:
    with pytest.raises(ValueError, match="数量"):
        demand_elasticity(MONOPOLY, 0)


def test_独占は需要が弾力的な範囲で作る() -> None:
    assert demand_elasticity(MONOPOLY, monopoly_outcome(MONOPOLY).quantity) > 1


def test_ラーナー指数は価格の上乗せの割合で弾力性の逆数() -> None:
    outcome = monopoly_outcome(MONOPOLY)
    assert lerner_index(MONOPOLY, outcome.price) == pytest.approx(45 / 55)
    assert lerner_index(MONOPOLY, outcome.price) == pytest.approx(
        1 / demand_elasticity(MONOPOLY, outcome.quantity)
    )
    assert lerner_index(MONOPOLY, MONOPOLY.marginal_cost) == 0


def test_ラーナー指数の価格は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="価格"):
        lerner_index(MONOPOLY, 0)


def test_独占的競争の短期の利潤は固定費用を引いた値() -> None:
    assert monopolistic_competition_profit(MONOPOLY, 1000) == 1025
    assert monopolistic_competition_profit(MONOPOLY, 2025) == 0
    assert monopolistic_competition_profit(MONOPOLY, 3000) == -975


def test_長期には新規参入で利潤が0になり価格は平均費用に等しい() -> None:
    long_run = long_run_monopolistic_competition(
        marginal_cost=10, demand_slope=1, fixed_cost=1000
    )
    assert long_run.quantity == pytest.approx(math.sqrt(1000))
    assert long_run.price == pytest.approx(10 + math.sqrt(1000))
    average_cost = 10 + 1000 / long_run.quantity
    assert long_run.price == pytest.approx(average_cost)
    assert long_run.profit == pytest.approx(0, abs=1e-9)


def test_長期の需要曲線は参入で左へ動く() -> None:
    long_run = long_run_monopolistic_competition(10, 1, 1000)
    assert long_run.demand_intercept == pytest.approx(10 + 2 * math.sqrt(1000))
    assert long_run.demand_intercept < MONOPOLY.demand_intercept


def test_長期に利潤が0になる需要では短期の利潤も0() -> None:
    long_run = long_run_monopolistic_competition(10, 1, 2025)
    assert long_run.demand_intercept == pytest.approx(100)
    after = Monopoly(long_run.demand_intercept, 1, 10)
    assert monopolistic_competition_profit(after, 2025) == pytest.approx(0, abs=1e-9)


def test_独占的競争では平均費用がまだ下がる数量で作る() -> None:
    long_run = long_run_monopolistic_competition(10, 1, 1000)
    q = long_run.quantity
    assert 10 + 1000 / q > 10 + 1000 / (2 * q)


def test_独占的競争の仮定のチェック() -> None:
    with pytest.raises(ValueError, match="固定費用"):
        long_run_monopolistic_competition(10, 1, 0)
    with pytest.raises(ValueError, match="傾き"):
        long_run_monopolistic_competition(10, 0, 1000)
    with pytest.raises(ValueError, match="限界費用"):
        long_run_monopolistic_competition(-1, 1, 1000)
