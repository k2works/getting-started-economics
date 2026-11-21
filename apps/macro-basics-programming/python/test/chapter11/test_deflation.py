"""第 11 章: デフレと実質利子率、物価ショックのテスト。"""

import math

import pytest

from lib.chapter10.ad_as import AdEconomy
from lib.chapter11.deflation import debt_burden, real_interest_rate
from lib.chapter11.price_shocks import cost_push_effect, demand_pull_effect

ECONOMY = AdEconomy(mpc=0.6, b=20, intercept=450, k=0.5, h=100, nominal_money=250)


def test_デフレでは実質利子率が名目利子率より高い() -> None:
    assert real_interest_rate(0.02, -0.01) == pytest.approx(0.03)


def test_インフレでは実質利子率が名目利子率より低い() -> None:
    assert real_interest_rate(0.02, 0.01) == pytest.approx(0.01)


def test_名目利子率が0でもデフレなら実質利子率は正() -> None:
    assert real_interest_rate(0.0, -0.02) == pytest.approx(0.02)


def test_物価が変わらなければ名目の借金の負担は変わらない() -> None:
    assert debt_burden(1000, 0.0) == pytest.approx(1000)


def test_デフレで名目の借金の実質的な負担は増える() -> None:
    assert debt_burden(1000, -0.1) == pytest.approx(1000 / 0.9)
    assert debt_burden(1000, -0.1) > 1000


def test_インフレで名目の借金の実質的な負担は減る() -> None:
    assert debt_burden(1000, 0.25) == pytest.approx(800)


def test_デフレが続くと負担は複利で増える() -> None:
    assert debt_burden(1000, -0.1, years=2) == pytest.approx(1000 / 0.81)


def test_物価が0以下になる下落はエラー() -> None:
    with pytest.raises(ValueError, match="インフレ率"):
        debt_burden(1000, -1.0)


def test_年数が負ならエラー() -> None:
    with pytest.raises(ValueError, match="年数"):
        debt_burden(1000, 0.0, years=-1)


def test_ディマンドプルは物価も所得も上げる() -> None:
    d_price, d_income = demand_pull_effect(ECONOMY, 1000, 480, 400, 10)
    assert d_price == pytest.approx((4.4 + math.sqrt(35.36)) / 8 - 1.25)
    assert d_income == pytest.approx(480 + 400 * (1.25 + d_price) - 980)
    assert d_price > 0
    assert d_income > 0


def test_コストプッシュは物価を上げ所得を下げる() -> None:
    d_price, d_income = cost_push_effect(ECONOMY, 1000, 480, 400, 20)
    assert d_price == pytest.approx((440 + math.sqrt(353600)) / 800 - 1.25)
    assert d_price > 0
    assert d_income < 0


def test_コストプッシュで供給が大きく減ると垂直部分で物価が2に上がる() -> None:
    d_price, d_income = cost_push_effect(ECONOMY, 1000, 480, 400, 50)
    assert d_price == pytest.approx(0.75)
    assert d_income == pytest.approx(-30)


def test_ディマンドプルの需要の増加が0以下ならエラー() -> None:
    with pytest.raises(ValueError, match="増加"):
        demand_pull_effect(ECONOMY, 1000, 480, 400, 0)


def test_コストプッシュの供給の減少が0以下ならエラー() -> None:
    with pytest.raises(ValueError, match="減少"):
        cost_push_effect(ECONOMY, 1000, 480, 400, 0)


def test_0年後の負担は額面のまま() -> None:
    assert debt_burden(1000, 0.1, years=0) == pytest.approx(1000)
