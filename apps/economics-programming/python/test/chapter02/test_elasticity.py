"""第 2 章: 弾力性のテスト。"""

import pytest

from lib.chapter02.elasticity import (
    classify_income_elasticity,
    income_elasticity,
    is_price_elastic,
    price_elasticity,
)


def test_価格が2割上がり需要量が5パーセント減ると価格弾力性は0_25() -> None:
    # 需要曲線 Q = 100 - 2P で、価格 10 -> 12 のとき需要量は 80 -> 76
    result = price_elasticity(
        price_before=10, price_after=12, quantity_before=80, quantity_after=76
    )
    assert result == pytest.approx(0.25)


def test_価格が変わらないと価格弾力性は求められない() -> None:
    with pytest.raises(ValueError):
        price_elasticity(
            price_before=10, price_after=10, quantity_before=80, quantity_after=80
        )


def test_所得が1割増え需要量が3割増えると所得弾力性は3() -> None:
    result = income_elasticity(
        income_before=300, income_after=330, quantity_before=20, quantity_after=26
    )
    assert result == pytest.approx(3.0)


def test_所得が変わらないと所得弾力性は求められない() -> None:
    with pytest.raises(ValueError):
        income_elasticity(
            income_before=300, income_after=300, quantity_before=20, quantity_after=20
        )


@pytest.mark.parametrize(
    ("elasticity", "expected"),
    [
        (3.0, "奢侈品"),
        (1.0, "奢侈品"),
        (0.5, "必需品"),
        (0.0, "必需品"),
        (-0.2, "下級財"),
    ],
)
def test_所得弾力性で財を分類する(elasticity: float, expected: str) -> None:
    assert classify_income_elasticity(elasticity) == expected


def test_価格弾力性が1より大きければ弾力的() -> None:
    assert is_price_elastic(1.5) is True
    assert is_price_elastic(0.25) is False
