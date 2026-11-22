import pytest

from lib.chapter02.quadratic import argmax_on_grid
from lib.chapter05.cost import (
    average_cost,
    average_variable_cost,
    competitive_profit,
    fixed_cost,
    marginal_cost,
    minimum_average_cost,
    minimum_average_variable_cost,
    profit_maximizing_quantity,
    variable_cost,
)
from lib.chapter05.derivative import Polynomial, numerical_derivative

# この章で使い回す費用関数（係数は、次数の低い順）
COST = Polynomial((100, 10, 1))  # C(q) = q² + 10q + 100
COST_HALF = Polynomial((50, 4, 0.5))  # C(q) = 0.5q² + 4q + 50
COST_CUBIC = Polynomial((20, 15, -6, 1))  # C(q) = q³ − 6q² + 15q + 20


def test_費用は固定費用と可変費用に分かれる() -> None:
    assert fixed_cost(COST) == 100
    assert variable_cost(COST, 20) == 600
    assert fixed_cost(COST_HALF) == 50
    assert variable_cost(COST_HALF, 10) == 90
    assert variable_cost(COST, 0) == 0


def test_平均費用と平均可変費用は1単位あたりの費用() -> None:
    assert average_cost(COST, 20) == 35
    assert average_variable_cost(COST, 20) == 30
    assert average_cost(COST_HALF, 10) == 14
    assert average_variable_cost(COST_HALF, 10) == 9
    assert average_cost(COST, 0.5) == pytest.approx(210.5)


def test_限界費用は費用関数の導関数() -> None:
    assert marginal_cost(COST, 20) == 50  # MC = 2q + 10
    assert marginal_cost(COST_HALF, 10) == 14  # MC = q + 4
    for cost in [COST, COST_HALF, COST_CUBIC]:
        for q in [0.5, 3, 12]:
            slope = numerical_derivative(cost, q)
            assert marginal_cost(cost, q) == pytest.approx(slope, abs=1e-6)


def test_価格50なら限界費用50の数量20で利潤300() -> None:
    assert profit_maximizing_quantity(50, COST) == 20
    assert competitive_profit(50, COST, 20) == 300  # 1000 − 700
    assert profit_maximizing_quantity(20, COST_HALF) == 16
    assert competitive_profit(20, COST_HALF, 16) == 78  # 320 − 242


@pytest.mark.parametrize("cost", [COST, COST_HALF, COST_CUBIC])
@pytest.mark.parametrize("price", [15, 30, 50, 80])
def test_利潤最大の数量では価格と限界費用が等しく格子探索と一致する(
    price: float, cost: Polynomial
) -> None:
    best = profit_maximizing_quantity(price, cost)
    assert marginal_cost(cost, best) == pytest.approx(price)
    grid = argmax_on_grid(lambda q: competitive_profit(price, cost, q), 0, 100, 10001)
    assert best == pytest.approx(grid, abs=0.01)


def test_平均費用は限界費用と交わる点で最小() -> None:
    assert minimum_average_cost(COST) == (10, 30)
    assert marginal_cost(COST, 10) == 30
    assert minimum_average_cost(COST_HALF) == (10, 14)
    assert marginal_cost(COST_HALF, 10) == 14
    # 固定費用が 1 より小さくても、q = √(c₀ ÷ c₂) で最小（√(0.5 ÷ 2) = 0.5）
    assert minimum_average_cost(Polynomial((0.5, 0, 2))) == (0.5, 2)
    grid = argmax_on_grid(lambda q: -average_cost(COST, q), 1, 40, 3901)
    assert grid == pytest.approx(10)


def test_価格が平均可変費用の最小値より低ければ生産しない() -> None:
    # 3 次の費用: AVC = q² − 6q + 15 は q = 3 で最小 6（そこで MC = AVC）
    assert minimum_average_variable_cost(COST_CUBIC) == (3, 6)
    assert marginal_cost(COST_CUBIC, 3) == 6
    assert profit_maximizing_quantity(15, COST_CUBIC) == 4
    assert competitive_profit(15, COST_CUBIC, 4) == 12
    assert profit_maximizing_quantity(6.1, COST_CUBIC) > 3
    # ちょうど AVC の最小値では、作っても作らなくても利潤は −20。作るほうを選ぶ
    assert profit_maximizing_quantity(6, COST_CUBIC) == 3
    assert profit_maximizing_quantity(5.9, COST_CUBIC) == 0
    assert profit_maximizing_quantity(5, COST_CUBIC) == 0


def test_数量が正でなければ平均費用は決まらない() -> None:
    for quantity in [0, -1]:
        with pytest.raises(ValueError):
            average_cost(COST, quantity)
        with pytest.raises(ValueError):
            average_variable_cost(COST, quantity)


def test_2次の費用では価格が限界費用の切片以下なら生産しない() -> None:
    # MC = 2q + 10 なので、価格 10 以下では、正の数量で P = MC にならない
    assert minimum_average_variable_cost(COST) == (0, 10)
    assert profit_maximizing_quantity(10, COST) == 0
    assert profit_maximizing_quantity(8, COST) == 0
    assert profit_maximizing_quantity(10.5, COST) == pytest.approx(0.25)
    assert competitive_profit(8, COST, 0) == -fixed_cost(COST)


def test_平均可変費用の頂点が負なら最小は数量0の極限() -> None:
    cost = Polynomial((5, 1, 3, 1))  # AVC = q² + 3q + 1 の頂点は q = −1.5
    assert minimum_average_variable_cost(cost) == (0, 1)
    # 頂点が 0 < q < 1 なら、そこが最小（AVC = q² − q + 1 は q = 0.5 で 0.75）
    assert minimum_average_variable_cost(Polynomial((5, 1, -1, 1))) == (0.5, 0.75)


def test_利潤最大化は上に凸の利潤になる費用だけを扱う() -> None:
    for cost in [Polynomial((100, 10)), Polynomial((0, 30, 0, -1))]:
        with pytest.raises(ValueError):
            profit_maximizing_quantity(50, cost)


def test_平均費用の最小は固定費用と2乗の係数が正の2次の費用だけ() -> None:
    for cost in [COST_CUBIC, Polynomial((100, 10))]:
        with pytest.raises(ValueError, match="2 次の費用"):
            minimum_average_cost(cost)
    for cost in [Polynomial((0, 10, 1)), Polynomial((100, 10, -1))]:
        with pytest.raises(ValueError, match="正でなければ"):
            minimum_average_cost(cost)
