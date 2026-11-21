"""第 7 章: 貨幣需要と LM 曲線のテスト（中核）。"""

import pytest

from lib.chapter07.money_market import (
    lm_income,
    lm_interest,
    lm_slope,
    money_demand,
)

K = 0.5  # 所得に対する貨幣需要の感応度
H = 100.0  # 利子率に対する貨幣需要の感応度


def test_貨幣需要は所得の増加関数で利子率の減少関数() -> None:
    assert money_demand(1000, 2.5, K, H) == pytest.approx(250)
    assert money_demand(1200, 2.5, K, H) > money_demand(1000, 2.5, K, H)
    assert money_demand(1000, 4.0, K, H) < money_demand(1000, 2.5, K, H)


def test_LM曲線上の利子率は貨幣市場を均衡させる() -> None:
    assert lm_interest(1000, 250, K, H) == pytest.approx(2.5)
    demand = money_demand(1000, lm_interest(1000, 250, K, H), K, H)
    assert demand == pytest.approx(250)


def test_LM曲線は右上がりで所得が増えると利子率が上がる() -> None:
    assert lm_interest(1200, 250, K, H) > lm_interest(1000, 250, K, H)


def test_所得から利子率を求める式と逆の関係() -> None:
    interest = lm_interest(1000, 250, K, H)
    assert lm_income(interest, 250, K, H) == pytest.approx(1000)


def test_実質貨幣供給が増えるとLM曲線は右にシフトする() -> None:
    assert lm_income(2.5, 300, K, H) > lm_income(2.5, 250, K, H)
    assert lm_interest(1000, 300, K, H) < lm_interest(1000, 250, K, H)


def test_LM曲線の傾きは_k_を_h_で割った値() -> None:
    assert lm_slope(K, H) == pytest.approx(0.005)
    assert lm_slope(K, 200.0) < lm_slope(K, H)


def test_感応度が正でなければエラー() -> None:
    with pytest.raises(ValueError, match="所得への感応度"):
        money_demand(1000, 2.5, 0.0, H)
    with pytest.raises(ValueError, match="利子率への感応度"):
        lm_interest(1000, 250, K, 0.0)
    with pytest.raises(ValueError, match="利子率への感応度"):
        lm_slope(K, -1.0)
