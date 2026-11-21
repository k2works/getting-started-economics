"""全体レビュー（2026-11-21）の指摘: 0 より大きく 1 未満の有効な値。"""

import pytest

from lib.chapter10.ad_as import AdEconomy
from lib.chapter11.okun import output_gap_ratio
from lib.chapter11.price_shocks import cost_push_effect, demand_pull_effect

ECONOMY = AdEconomy(mpc=0.6, b=20, intercept=450, k=0.5, h=100, nominal_money=250)


def test_潜在GDPが1未満の正でも需給ギャップを求められる() -> None:
    assert output_gap_ratio(0.25, 0.5) == pytest.approx(-0.5)


def test_需要の増加が1未満の正でもディマンドプルを求められる() -> None:
    dp, dy = demand_pull_effect(ECONOMY, 1000, 480, 400, 0.5)
    assert dp >= 0
    assert dy >= 0


def test_供給の減少が1未満の正でもコストプッシュを求められる() -> None:
    dp, dy = cost_push_effect(ECONOMY, 1000, 480, 400, 0.5)
    assert dp >= 0
    assert dy <= 0
