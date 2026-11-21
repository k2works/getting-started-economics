"""第 10 章: 国際貿易（自由貿易・関税）のテスト。"""

import pytest

from lib.chapter08.market import LinearMarket
from lib.chapter09.surplus import consumer_surplus, producer_surplus
from lib.chapter10.trade import (
    autarky_result,
    free_trade_result,
    gains_from_trade,
    tariff_deadweight_loss,
    tariff_losses,
    tariff_result,
)

# 需要 Q = 100 − P、供給 Q = P − 10。閉鎖経済の均衡は P = 55、Q = 45
MARKET = LinearMarket(100, -1, -10, 1)


def test_閉鎖経済の結果() -> None:
    result = autarky_result(MARKET)
    assert result.domestic_price == 55
    assert result.quantity_demanded == 45
    assert result.quantity_supplied == 45
    assert result.net_imports == 0
    assert result.total_surplus == 2025


def test_世界価格が低ければ輸入国() -> None:
    result = free_trade_result(MARKET, 40)
    assert result.domestic_price == 40
    assert result.quantity_demanded == 60
    assert result.quantity_supplied == 30
    assert result.net_imports == 30


def test_輸入国では消費者余剰が増え生産者余剰が減る() -> None:
    result = free_trade_result(MARKET, 40)
    assert result.consumer_surplus == pytest.approx(1800)
    assert result.producer_surplus == pytest.approx(450)
    assert result.consumer_surplus > consumer_surplus(MARKET, 55)
    assert result.producer_surplus < producer_surplus(MARKET, 55)


def test_輸入国でも総余剰は増える() -> None:
    assert free_trade_result(MARKET, 40).total_surplus == pytest.approx(2250)
    assert gains_from_trade(MARKET, 40) == pytest.approx(225)


def test_世界価格が高ければ輸出国() -> None:
    result = free_trade_result(MARKET, 70)
    assert result.quantity_demanded == 30
    assert result.quantity_supplied == 60
    assert result.net_imports == -30


def test_輸出国では生産者余剰が増え消費者余剰が減る() -> None:
    result = free_trade_result(MARKET, 70)
    assert result.consumer_surplus == pytest.approx(450)
    assert result.producer_surplus == pytest.approx(1800)
    assert result.consumer_surplus < consumer_surplus(MARKET, 55)
    assert result.producer_surplus > producer_surplus(MARKET, 55)


def test_輸出国でも総余剰は増える() -> None:
    assert free_trade_result(MARKET, 70).total_surplus == pytest.approx(2250)
    assert gains_from_trade(MARKET, 70) == pytest.approx(225)


def test_輸出入量は需要と供給の差() -> None:
    for price in (20, 40, 70, 90):
        result = free_trade_result(MARKET, price)
        assert result.net_imports == pytest.approx(
            result.quantity_demanded - result.quantity_supplied
        )


def test_世界価格が均衡と同じなら貿易は起きない() -> None:
    result = free_trade_result(MARKET, 55)
    assert result.net_imports == 0
    assert gains_from_trade(MARKET, 55) == pytest.approx(0, abs=1e-9)


def test_世界価格が正でなければエラー() -> None:
    with pytest.raises(ValueError, match="世界価格"):
        free_trade_result(MARKET, 0)
    with pytest.raises(ValueError, match="世界価格"):
        tariff_result(MARKET, -1, 5)


def test_世界価格が1未満の正の値でも求められる() -> None:
    result = free_trade_result(MARKET, 0.5)
    assert result.quantity_supplied == 0
    assert result.net_imports == pytest.approx(99.5)


def test_関税のもとの国内価格は世界価格に関税を足した値() -> None:
    result = tariff_result(MARKET, 40, 10)
    assert result.domestic_price == 50
    assert result.quantity_demanded == 50
    assert result.quantity_supplied == 40
    assert result.net_imports == 10


def test_関税は消費者余剰を減らし生産者余剰を増やす() -> None:
    free, tariff = free_trade_result(MARKET, 40), tariff_result(MARKET, 40, 10)
    assert tariff.consumer_surplus == pytest.approx(1250)
    assert tariff.producer_surplus == pytest.approx(800)
    assert tariff.consumer_surplus < free.consumer_surplus
    assert tariff.producer_surplus > free.producer_surplus


def test_関税収入は関税かける輸入量() -> None:
    assert tariff_result(MARKET, 40, 10).tariff_revenue == pytest.approx(100)


def test_関税のもとの総余剰は税収を含む() -> None:
    result = tariff_result(MARKET, 40, 10)
    assert result.total_surplus == pytest.approx(1250 + 800 + 100)


def test_関税の死荷重は自由貿易との差で三角形が2つ() -> None:
    assert tariff_deadweight_loss(MARKET, 40, 10) == pytest.approx(100)
    production, consumption = tariff_losses(MARKET, 40, 10)
    assert production == pytest.approx(50)
    assert consumption == pytest.approx(50)
    assert production + consumption == pytest.approx(
        tariff_deadweight_loss(MARKET, 40, 10)
    )


def test_関税が大きいほど死荷重は大きい() -> None:
    losses = [tariff_deadweight_loss(MARKET, 40, t) for t in (0, 5, 10, 15)]
    assert losses == pytest.approx([0, 25, 100, 225])


def test_関税が輸入をなくすほど大きければ閉鎖経済と同じ() -> None:
    result = tariff_result(MARKET, 40, 15)
    assert result.domestic_price == pytest.approx(55)
    assert result.net_imports == pytest.approx(0)
    big = tariff_result(MARKET, 40, 30)
    assert big.domestic_price == pytest.approx(55)
    assert big.tariff_revenue == 0
    assert big.total_surplus == pytest.approx(2025)


def test_関税の死荷重の上限は貿易の利益() -> None:
    assert tariff_deadweight_loss(MARKET, 40, 30) == pytest.approx(
        gains_from_trade(MARKET, 40)
    )


def test_関税が負ならエラー() -> None:
    with pytest.raises(ValueError, match="関税"):
        tariff_result(MARKET, 40, -1)


def test_関税は輸入国だけにかかる() -> None:
    with pytest.raises(ValueError, match="輸入"):
        tariff_result(MARKET, 70, 10)
    with pytest.raises(ValueError, match="輸入"):
        tariff_result(MARKET, 55, 10)


def test_関税0は自由貿易と同じ() -> None:
    free, tariff = free_trade_result(MARKET, 40), tariff_result(MARKET, 40, 0)
    assert tariff.domestic_price == free.domestic_price
    assert tariff.total_surplus == pytest.approx(free.total_surplus)
