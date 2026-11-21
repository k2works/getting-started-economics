"""第 13 章: 公共財（フリーライダー）と財の分類のテスト。"""

import pytest

from lib.chapter13.public import (
    PublicGood,
    classify_good,
    individual_quantity,
    public_good_optimal_quantity,
    under_provision,
    voluntary_quantity,
)

# 2 人の限界便益 MB₁ = 40 − 2q、MB₂ = 20 − q。限界費用 30
GOOD = PublicGood(benefit_intercepts=(40, 20), benefit_slopes=(2, 1), marginal_cost=30)


def test_最適な供給量は限界便益の縦の和が限界費用に等しい点() -> None:
    assert public_good_optimal_quantity(GOOD) == pytest.approx(10)
    total_benefit = (40 - 2 * 10) + (20 - 10)
    assert total_benefit == GOOD.marginal_cost


def test_1人だけで決めるなら自分の限界便益が限界費用に等しい点() -> None:
    assert individual_quantity(GOOD, 0) == pytest.approx(5)
    assert individual_quantity(GOOD, 1) == 0


def test_自発的な供給は最も欲しい人の量() -> None:
    assert voluntary_quantity(GOOD) == pytest.approx(5)


def test_フリーライダーがいると供給は最適より少ない() -> None:
    assert under_provision(GOOD) == pytest.approx(5)
    assert voluntary_quantity(GOOD) < public_good_optimal_quantity(GOOD)


def test_全員の限界便益が限界費用以下なら供給しない() -> None:
    hopeless = PublicGood((10, 10), (1, 1), 50)
    assert public_good_optimal_quantity(hopeless) == 0
    assert voluntary_quantity(hopeless) == 0
    assert under_provision(hopeless) == 0


def test_1人だけの社会では自発的な供給が最適() -> None:
    alone = PublicGood((40,), (2,), 30)
    assert voluntary_quantity(alone) == public_good_optimal_quantity(alone)


def test_人数が増えるほど最適な供給は増えるが自発的な供給は変わらない() -> None:
    more = PublicGood((40, 20, 20), (2, 1, 1), 30)
    assert public_good_optimal_quantity(more) == pytest.approx((80 - 30) / 4)
    assert voluntary_quantity(more) == pytest.approx(5)
    assert under_provision(more) > under_provision(GOOD)


def test_公共財の入力のチェック() -> None:
    with pytest.raises(ValueError, match="人"):
        PublicGood((), (), 10)
    with pytest.raises(ValueError, match="同じ"):
        PublicGood((40, 20), (2,), 10)
    with pytest.raises(ValueError, match="傾き"):
        PublicGood((40,), (0,), 10)
    with pytest.raises(ValueError, match="限界費用"):
        PublicGood((40,), (2,), -1)
    with pytest.raises(ValueError, match="番号"):
        individual_quantity(GOOD, 2)


def test_財の4分類() -> None:
    assert classify_good(rival=True, excludable=True) == "private"
    assert classify_good(rival=False, excludable=True) == "club"
    assert classify_good(rival=True, excludable=False) == "common"
    assert classify_good(rival=False, excludable=False) == "public"


def test_限界便益が負になる人は縦の和に入れない() -> None:
    lopsided = PublicGood((100, 10), (1, 1), 20)
    assert public_good_optimal_quantity(lopsided) == pytest.approx(80)
    assert voluntary_quantity(lopsided) == pytest.approx(80)
    assert under_provision(lopsided) == pytest.approx(0)


def test_最適な量では正の限界便益の和が限界費用に等しい() -> None:
    good = PublicGood((100, 30, 10), (1, 2, 1), 20)
    q = public_good_optimal_quantity(good)
    total = sum(
        max(a - b * q, 0)
        for a, b in zip(good.benefit_intercepts, good.benefit_slopes, strict=True)
    )
    assert total == pytest.approx(good.marginal_cost)
    assert under_provision(good) >= 0


def test_全員の便益が正の範囲なら従来どおり() -> None:
    both = PublicGood((40, 30), (1, 1), 20)
    assert public_good_optimal_quantity(both) == pytest.approx(25)


def test_限界費用が0なら限界便益が0になる数量まで供給する() -> None:
    assert public_good_optimal_quantity(PublicGood((10,), (1,), 0)) == pytest.approx(10)
