"""第 14 章: フィリップス曲線・需給ギャップ・オークンの法則・貨幣数量説のテスト。"""

import pytest

from lib.chapter14.indicators import (
    okun_unemployment,
    output_gap,
    phillips_inflation,
    price_level_by_quantity_theory,
    real_interest_rate,
)


@pytest.mark.parametrize(
    ("unemployment", "expected"),
    [(3, 2.5), (4, 2.0), (5, 1.5)],
)
def test_フィリップス曲線は失業率が低いほど物価上昇率が高い(
    unemployment: float, expected: float
) -> None:
    result = phillips_inflation(
        unemployment, natural_rate=4, expected_inflation=2, slope=0.5
    )
    assert result == pytest.approx(expected)


def test_自然失業率では物価上昇率は期待物価上昇率に等しい() -> None:
    result = phillips_inflation(4, natural_rate=4, expected_inflation=3, slope=0.5)
    assert result == pytest.approx(3)


def test_需給ギャップは実際のGDPと潜在GDPの差の割合() -> None:
    assert output_gap(actual=1200, potential=1250) == pytest.approx(-4)
    assert output_gap(actual=1300, potential=1250) == pytest.approx(4)


def test_潜在GDPが0以下なら需給ギャップは求められない() -> None:
    with pytest.raises(ValueError):
        output_gap(actual=100, potential=0)


def test_オークンの法則では需給ギャップが負だと失業率が自然失業率を上回る() -> None:
    # ギャップ -4%、係数 0.5 なら、失業率は自然失業率 4% より 2% 高い
    assert okun_unemployment(-4, natural_rate=4, coefficient=0.5) == pytest.approx(6)
    assert okun_unemployment(4, natural_rate=4, coefficient=0.5) == pytest.approx(2)


def test_実質利子率は名目利子率からインフレ率を引いた値() -> None:
    assert real_interest_rate(nominal=3, inflation=1) == pytest.approx(2)


def test_デフレでは名目利子率が0でも実質利子率はプラス() -> None:
    assert real_interest_rate(nominal=0, inflation=-2) == pytest.approx(2)


def test_貨幣量が2倍なら物価も2倍() -> None:
    # MV = PY: 525 × 2 ÷ 1050 = 1、1050 × 2 ÷ 1050 = 2
    base = price_level_by_quantity_theory(525, velocity=2, real_income=1050)
    doubled = price_level_by_quantity_theory(1050, velocity=2, real_income=1050)
    assert base == pytest.approx(1)
    assert doubled == pytest.approx(2 * base)


def test_実質所得が0以下なら貨幣数量説の物価は求められない() -> None:
    with pytest.raises(ValueError):
        price_level_by_quantity_theory(525, velocity=2, real_income=0)
