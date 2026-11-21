"""第 12 章: 消費の理論のテスト。"""

import pytest

from lib.chapter12.consumption import (
    average_propensity,
    consumption_from_absolute_income,
    consumption_from_liquid_assets,
    lifecycle_consumption,
    lifecycle_saving,
    permanent_consumption,
    permanent_income,
    ratchet_consumption,
)


def test_絶対所得仮説の消費は所得の一定割合と基礎消費の和() -> None:
    assert consumption_from_absolute_income(100, 0.8, 20) == pytest.approx(100)
    assert consumption_from_absolute_income(200, 0.8, 20) == pytest.approx(180)


def test_短期では所得が増えると平均消費性向が下がる() -> None:
    low = average_propensity(100, 0.8, 20)
    high = average_propensity(200, 0.8, 20)
    assert low == pytest.approx(1.0)
    assert high == pytest.approx(0.9)
    assert high < low


def test_長期は基礎消費がないので平均消費性向は一定() -> None:
    rates = [average_propensity(y, 0.8, 0) for y in (100, 200, 400)]
    assert rates == pytest.approx([0.8, 0.8, 0.8])


def test_所得が0なら平均消費性向は計算できない() -> None:
    with pytest.raises(ValueError, match="所得"):
        average_propensity(0, 0.8, 20)


def test_ライフサイクル仮説は生涯所得を生涯の年数で割る() -> None:
    assert lifecycle_consumption(600, 40, 60) == pytest.approx(400)


def test_働いている間の貯蓄は年収から消費を引いた額() -> None:
    assert lifecycle_saving(600, 40, 60) == pytest.approx(200)


def test_生涯の貯蓄は0になる() -> None:
    working, lifetime = 40, 60
    saving = lifecycle_saving(600, working, lifetime)
    dissaving = lifecycle_consumption(600, working, lifetime)
    assert saving * working - dissaving * (lifetime - working) == pytest.approx(0)


def test_働く年数が0年から生涯の年数までなら有効() -> None:
    assert lifecycle_consumption(600, 0, 60) == pytest.approx(0)
    assert lifecycle_consumption(600, 60, 60) == pytest.approx(600)


@pytest.mark.parametrize(
    ("working", "lifetime", "message"),
    [(0, 0, "生涯の年数は、正"), (-1, 60, "働く年数"), (70, 60, "働く年数")],
)
def test_ライフサイクル仮説の年数が不正ならエラー(
    working: int, lifetime: int, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        lifecycle_consumption(600, working, lifetime)


def test_恒常所得は過去の所得の加重平均() -> None:
    path = permanent_income([100, 100, 130, 100], 0.5)
    assert path == pytest.approx([100, 100, 115, 107.5])


def test_調整係数が1なら恒常所得は今期の所得に等しい() -> None:
    incomes = [100, 130, 90]
    assert permanent_income(incomes, 1) == pytest.approx(incomes)


@pytest.mark.parametrize("adjust", [0, -0.1, 1.5])
def test_調整係数が範囲外ならエラー(adjust: float) -> None:
    with pytest.raises(ValueError, match="調整係数"):
        permanent_income([100], adjust)


def test_所得の系列が空ならエラー() -> None:
    with pytest.raises(ValueError, match="空"):
        permanent_income([], 0.5)


def test_一時的な所得の増加は恒常所得仮説ではあまり消費されない() -> None:
    incomes = [100, 100, 130, 100]
    absolute = [consumption_from_absolute_income(y, 0.8, 0) for y in incomes]
    permanent = permanent_consumption(incomes, 0.8, 0.2)
    assert absolute[2] - absolute[1] == pytest.approx(24)
    assert permanent[2] - permanent[1] == pytest.approx(4.8)


def test_ラチェット効果で所得が下がっても消費は下がらない() -> None:
    incomes = [100, 120, 90, 110, 130]
    assert ratchet_consumption(incomes, 0.8) == pytest.approx([80, 96, 96, 96, 104])


def test_流動資産仮説の消費は所得と資産の両方に依存する() -> None:
    assert consumption_from_liquid_assets(100, 50, 0.6, 0.1) == pytest.approx(65)
    assert consumption_from_liquid_assets(100, 150, 0.6, 0.1) == pytest.approx(75)
