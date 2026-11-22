import pytest

from lib.chapter01.market import (
    Equilibrium,
    constant_cost_equilibrium,
    consumer_surplus,
    demand_quantity,
    equilibrium,
    line_through,
    market_demand,
    producer_surplus,
    supply_quantity,
    total_surplus,
)

# 需要 q = 120 − 2p、供給 q = p（この章で使い回す、手計算できる例）
A, B, C, D = 120, 2, 0, 1


def test_2点を通る直線の傾きと切片() -> None:
    assert line_through((10, 5), (20, 15)) == (1, -5)


def test_同じxの2点では直線が決まらない() -> None:
    with pytest.raises(ValueError):
        line_through((10, 5), (10, 15))


def test_需要量は価格が上がると減る() -> None:
    assert demand_quantity(10, A, B) == 100
    assert demand_quantity(30, A, B) == 60
    assert demand_quantity(30, A, B) < demand_quantity(10, A, B)


def test_需要量は負にならない() -> None:
    assert demand_quantity(60, A, B) == 0
    assert demand_quantity(100, A, B) == 0


def test_供給量は価格が上がると増え負にならない() -> None:
    assert supply_quantity(10, 10, 1) == 20
    assert supply_quantity(5, -10, 1) == 0
    assert supply_quantity(30, -10, 1) == 20


def test_均衡では需要量と供給量が等しい() -> None:
    result = equilibrium(A, B, C, D)
    assert result == Equilibrium(price=40, quantity=40)
    assert demand_quantity(result.price, A, B) == supply_quantity(result.price, C, D)


def test_均衡の収入は価格かける数量() -> None:
    assert equilibrium(A, B, C, D).revenue == 1600


def test_切片のある供給でも均衡を求める() -> None:
    result = equilibrium(100, 2, 10, 1)
    assert result.price == pytest.approx(30)
    assert result.quantity == pytest.approx(40)


def test_均衡価格が正にならなければエラー() -> None:
    with pytest.raises(ValueError):
        equilibrium(10, 1, 20, 1)


def test_傾きが正でなければエラー() -> None:
    with pytest.raises(ValueError):
        equilibrium(120, 0, 0, 1)
    with pytest.raises(ValueError):
        equilibrium(120, 2, 0, 0)


def test_消費者余剰と生産者余剰と総余剰() -> None:
    assert consumer_surplus(40, A, B) == 400
    assert producer_surplus(40, C, D) == 800
    assert total_surplus(A, B, C, D) == 1200


def test_供給が価格0でも正の量ならその分も生産者余剰に入る() -> None:
    assert producer_surplus(30, 10, 1) == pytest.approx(750)
    assert consumer_surplus(30, 100, 2) == pytest.approx(400)


def test_価格が需要の上限以上なら消費者余剰は0() -> None:
    assert consumer_surplus(60, A, B) == 0
    assert consumer_surplus(80, A, B) == 0


def test_価格が供給の下限以下なら生産者余剰は0() -> None:
    assert producer_surplus(5, -10, 1) == 0
    assert producer_surplus(10, -10, 1) == 0


def test_個人の需要を横に足して市場の需要にする() -> None:
    people = [(60, 1), (40, 1)]
    assert market_demand(20, people) == 60
    assert market_demand(30, people) == 40
    assert market_demand(50, people) == 10


def test_市場の需要は価格が個人の上限を超えると折れる() -> None:
    people = [(60, 1), (40, 1)]
    assert market_demand(40, people) == 20
    assert market_demand(60, people) == 0
    # 折れ点（p = 40）の前後で、傾きが 2 から 1 に変わる
    left = market_demand(30, people) - market_demand(31, people)
    right = market_demand(41, people) - market_demand(42, people)
    assert (left, right) == (2, 1)


def test_需要が非弾力的なら豊作で収入が減る() -> None:
    before = equilibrium(100, 0.5, 10, 1)
    after = equilibrium(100, 0.5, 40, 1)
    assert (before.price, before.quantity) == (60, 70)
    assert (after.price, after.quantity) == (40, 80)
    assert before.revenue == 4200
    assert after.revenue == 3200


def test_需要が弾力的なら供給が増えて収入も増える() -> None:
    before = equilibrium(A, B, C, D)
    after = equilibrium(A, B, 20, D)
    assert after.price < before.price
    assert after.quantity > before.quantity
    assert after.revenue > before.revenue


def test_単位あたり費用が一定なら価格は費用に等しい() -> None:
    result = constant_cost_equilibrium(A, B, 20)
    assert result == Equilibrium(price=20, quantity=80)


def test_単位あたり費用が需要の上限以上なら均衡がない() -> None:
    with pytest.raises(ValueError):
        constant_cost_equilibrium(A, B, 60)
    with pytest.raises(ValueError):
        constant_cost_equilibrium(A, B, -1)


def test_供給の傾きが0なら均衡を求めない() -> None:
    with pytest.raises(ValueError):
        equilibrium(120, 2, 10, 0)


def test_均衡の価格が0なら成り立たない() -> None:
    with pytest.raises(ValueError):
        equilibrium(10, 1, 10, 1)


def test_均衡の数量が0なら成り立たない() -> None:
    with pytest.raises(ValueError):
        equilibrium(10, 1, -10, 1)


def test_価格も数量も1未満の均衡を求める() -> None:
    result = equilibrium(1, 2, 0.25, 1)
    assert result.price == pytest.approx(0.25)
    assert result.quantity == pytest.approx(0.5)


def test_傾きが等しくない需要と供給の均衡() -> None:
    result = equilibrium(100, 2, 10, 3)
    assert (result.price, result.quantity) == (18, 64)


def test_傾きが1でない供給の生産者余剰() -> None:
    assert producer_surplus(30, 10, 2) == pytest.approx(1200)
    assert producer_surplus(30, -10, 2) == pytest.approx(625)


def test_費用が0なら均衡がない() -> None:
    with pytest.raises(ValueError):
        constant_cost_equilibrium(120, 2, 0)


def test_費用も数量も1未満の均衡を求める() -> None:
    result = constant_cost_equilibrium(1, 1, 0.5)
    assert result == Equilibrium(price=0.5, quantity=0.5)


def test_余剰の関数も傾きが正でなければエラー() -> None:
    with pytest.raises(ValueError):
        consumer_surplus(40, 120, 0)
    with pytest.raises(ValueError):
        consumer_surplus(40, 120, -2)
    with pytest.raises(ValueError):
        producer_surplus(40, 0, 0)
    with pytest.raises(ValueError):
        producer_surplus(40, 0, -1)


def test_費用一定の均衡も需要の傾きが正でなければエラー() -> None:
    with pytest.raises(ValueError):
        constant_cost_equilibrium(120, 0, 20)
    with pytest.raises(ValueError):
        constant_cost_equilibrium(120, -2, 20)
