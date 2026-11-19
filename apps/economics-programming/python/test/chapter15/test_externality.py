"""第 15 章: 外部不経済とピグー税のテスト。

需要曲線 Q = 100 - 2P、私的な供給曲線 Q = 3P、1 単位あたりの外部費用は 5。
"""

import pytest

from lib.chapter07.surplus import equilibrium, equilibrium_with_tax
from lib.chapter15.externality import (
    externality_deadweight_loss,
    social_optimum_quantity,
)

MARKET = {
    "demand_intercept": 100,
    "demand_slope": 2,
    "supply_intercept": 0,
    "supply_slope": 3,
}


def test_社会的に最適な数量は市場の数量60より少ない54() -> None:
    # 社会的限界費用 = 私的限界費用 + 外部費用。(100 - Q) / 2 = Q / 3 + 5 を解く
    assert social_optimum_quantity(**MARKET, external_cost=5) == pytest.approx(54)
    assert equilibrium(**MARKET)[1] == pytest.approx(60)


def test_外部費用が0なら社会的に最適な数量は市場の数量と等しい() -> None:
    assert social_optimum_quantity(**MARKET, external_cost=0) == pytest.approx(60)


def test_放任すると過剰供給になり死荷重が出る() -> None:
    # 底辺は過剰供給の分 60 - 54 = 6、高さは外部費用 5
    assert externality_deadweight_loss(**MARKET, external_cost=5) == pytest.approx(15)


def test_外部費用と同じ額のピグー税で社会的に最適な数量になる() -> None:
    taxed = equilibrium_with_tax(**MARKET, tax=5)
    assert taxed.quantity == pytest.approx(
        social_optimum_quantity(**MARKET, external_cost=5)
    )


def test_ピグー税で解消される死荷重は第7章の死荷重の式と同じ値() -> None:
    # 第 7 章では税が死荷重を生んだが、外部費用があるときは、税が死荷重を解消する
    assert equilibrium_with_tax(**MARKET, tax=5).deadweight_loss == pytest.approx(
        externality_deadweight_loss(**MARKET, external_cost=5)
    )


def test_負の外部費用は受け付けない() -> None:
    with pytest.raises(ValueError):
        social_optimum_quantity(**MARKET, external_cost=-1)
