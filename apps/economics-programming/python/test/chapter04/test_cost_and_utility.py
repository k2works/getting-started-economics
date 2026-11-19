"""第 4 章: 費用関数と効用関数のテスト。"""

import pytest

from lib.chapter04.cost import (
    average_cost,
    average_variable_cost,
    marginal_cost,
    total_cost,
)
from lib.chapter04.utility import cobb_douglas_utility, marginal_rate_of_substitution


def test_生産量が0でも固定費用がかかる() -> None:
    assert total_cost(0) == 10


def test_生産量が2のときの総費用は24() -> None:
    # C(q) = q^3 - 6q^2 + 15q + 10 に q = 2 を入れる: 8 - 24 + 30 + 10
    assert total_cost(2) == 24


def test_固定費用を変えられる() -> None:
    assert total_cost(2, fixed_cost=0) == 14


def test_生産量が2のときの限界費用は3() -> None:
    # MC(q) = 3q^2 - 12q + 15 に q = 2 を入れる: 12 - 24 + 15
    assert marginal_cost(2) == 3


def test_生産量が2のときの平均費用は12() -> None:
    assert average_cost(2) == 12


def test_生産量が2のときの平均可変費用は7() -> None:
    assert average_variable_cost(2) == 7


def test_生産量が3のとき限界費用は平均可変費用に等しい() -> None:
    # 操業停止点: MC と AVC の交点（最低点）
    assert marginal_cost(3) == average_variable_cost(3) == 6


def test_生産量が0のとき平均費用は求められない() -> None:
    with pytest.raises(ValueError):
        average_cost(0)


def test_生産量が負なら総費用は求められない() -> None:
    with pytest.raises(ValueError):
        total_cost(-1)


def test_コブ_ダグラス型の効用は4と9で6() -> None:
    assert cobb_douglas_utility(4, 9) == pytest.approx(6)


def test_財の量が負なら効用は求められない() -> None:
    with pytest.raises(ValueError):
        cobb_douglas_utility(-1, 9)


def test_限界代替率は財yの量を財xの量で割った値に比例する() -> None:
    assert marginal_rate_of_substitution(4, 9) == pytest.approx(2.25)
    assert marginal_rate_of_substitution(4, 9, alpha=0.75) == pytest.approx(6.75)


def test_財xの量が0なら限界代替率は求められない() -> None:
    with pytest.raises(ValueError):
        marginal_rate_of_substitution(0, 9)
