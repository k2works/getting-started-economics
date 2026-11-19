"""第 1 章: 需要曲線 Q = a - bP のテスト。"""

import pytest

from lib.chapter01.demand import choke_price, quantity_demanded


def test_価格が0なら需要量は切片と等しい() -> None:
    assert quantity_demanded(price=0, intercept=100, slope=2) == 100


def test_価格が上がると需要量は傾きの分だけ減る() -> None:
    assert quantity_demanded(price=10, intercept=100, slope=2) == 80


def test_価格が高すぎると需要量は0になる() -> None:
    assert quantity_demanded(price=60, intercept=100, slope=2) == 0


def test_負の価格は受け付けない() -> None:
    with pytest.raises(ValueError):
        quantity_demanded(price=-1, intercept=100, slope=2)


def test_需要が0になる最低の価格を求める() -> None:
    assert choke_price(intercept=100, slope=2) == 50
