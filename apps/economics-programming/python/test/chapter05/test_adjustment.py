"""第 5 章: 価格調整と数量調整のテスト。"""

import pytest

from lib.chapter05.adjustment import market_state, marshall_path, walras_path


def demand(price: float) -> float:
    return 100 - 2 * price


def supply(price: float) -> float:
    return 3 * price


def demand_price(quantity: float) -> float:
    # 需要曲線 Q = 100 - 2P を P について解いた逆需要曲線
    return (100 - quantity) / 2


def supply_price(quantity: float) -> float:
    # 供給曲線 Q = 3P を P について解いた逆供給曲線
    return quantity / 3


def test_ワルラス調整の最初の2回は手計算と一致する() -> None:
    path = walras_path(demand, supply, initial_price=0, step=0.1)
    # 超過需要 100 のとき、価格は 0 + 0.1 * 100 = 10。次は 10 + 0.1 * 50 = 15
    assert path[:3] == pytest.approx([0, 10, 15])


def test_ワルラス調整は均衡価格20に収束する() -> None:
    path = walras_path(demand, supply, initial_price=0, step=0.1)
    assert path[-1] == pytest.approx(20, abs=1e-6)


def test_ワルラス調整は初期価格が均衡価格なら動かない() -> None:
    assert walras_path(demand, supply, initial_price=20, step=0.1) == [20]


def test_調整の速さが大きすぎるとワルラス調整は収束しない() -> None:
    with pytest.raises(RuntimeError):
        walras_path(demand, supply, initial_price=0, step=0.5)


def test_マーシャル調整の最初の回は手計算と一致する() -> None:
    path = marshall_path(demand_price, supply_price, initial_quantity=0, step=0.1)
    # 需要価格 50 - 供給価格 0 = 50 なので、数量は 0 + 0.1 * 50 = 5
    assert path[:2] == pytest.approx([0, 5])


def test_マーシャル調整は均衡数量60に収束する() -> None:
    path = marshall_path(demand_price, supply_price, initial_quantity=0, step=0.1)
    assert path[-1] == pytest.approx(60, abs=1e-4)


def test_調整の速さが大きすぎるとマーシャル調整は収束しない() -> None:
    with pytest.raises(RuntimeError):
        marshall_path(demand_price, supply_price, initial_quantity=0, step=3)


@pytest.mark.parametrize(
    ("excess", "expected"),
    [(50, "品不足"), (-50, "売れ残り"), (0, "均衡"), (1e-12, "均衡")],
)
def test_超過需要から市場の状態を判定する(excess: float, expected: str) -> None:
    assert market_state(excess) == expected
