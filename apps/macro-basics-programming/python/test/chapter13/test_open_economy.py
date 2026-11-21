"""第 13 章: 為替・購買力平価・IS バランスのテスト。"""

import pytest

from lib.chapter13.open_economy import (
    is_balance_consistent,
    net_exports_from_balance,
    net_exports_from_exchange_rate,
    ppp_after_inflation,
    ppp_exchange_rate,
)


def test_基準の為替レートでは純輸出は基準の値() -> None:
    assert net_exports_from_exchange_rate(125, 20, 125, 0.4) == pytest.approx(20)


def test_円安で為替レートが上がると純輸出が増える() -> None:
    weak_yen = net_exports_from_exchange_rate(135, 20, 125, 0.4)
    assert weak_yen == pytest.approx(24)
    assert weak_yen > 20


def test_円高で為替レートが下がると純輸出が減る() -> None:
    strong_yen = net_exports_from_exchange_rate(115, 20, 125, 0.4)
    assert strong_yen == pytest.approx(16)
    assert strong_yen < 20


def test_純輸出は赤字にもなる() -> None:
    assert net_exports_from_exchange_rate(65, 20, 125, 0.4) == pytest.approx(-4)


def test_為替レートに対する純輸出の傾きが負ならエラー() -> None:
    with pytest.raises(ValueError, match="傾き"):
        net_exports_from_exchange_rate(125, 20, 125, -0.4)


def test_購買力平価は自国の価格を外国の価格で割る() -> None:
    assert ppp_exchange_rate(500, 4) == pytest.approx(125)


def test_外国の価格が0なら購買力平価は計算できない() -> None:
    with pytest.raises(ValueError, match="外国の価格"):
        ppp_exchange_rate(500, 0)


def test_自国の物価が10パーセント上がると購買力平価は10パーセント円安() -> None:
    assert ppp_after_inflation(500, 4, 0.10) == pytest.approx(137.5)


def test_自国の物価が下がると購買力平価は円高になる() -> None:
    assert ppp_after_inflation(500, 4, -0.2) == pytest.approx(100)


def test_物価が100パーセント以上下がることはない() -> None:
    with pytest.raises(ValueError, match="物価上昇率"):
        ppp_after_inflation(500, 4, -1.0)


def test_純輸出は民間の貯蓄超過と財政黒字の和() -> None:
    assert net_exports_from_balance(130, 100, 80, 90) == pytest.approx(20)


def test_貯蓄超過が財政赤字を上回る分が純輸出() -> None:
    # S − I = 30、T − G = −10
    assert net_exports_from_balance(130, 100, 80, 90) == pytest.approx(30 - 10)


def test_国内の支出面の恒等式とISバランスは同じ結論() -> None:
    # Y = C + I + G + X = 290 + 110 + 80 + 20 = 500、T = 80
    assert is_balance_consistent(500, 290, 110, 80, 80, 20) is True


def test_純輸出が合わなければ整合しない() -> None:
    assert is_balance_consistent(500, 290, 110, 80, 80, 30) is False


def test_純輸出が0でも整合を判定できる() -> None:
    assert is_balance_consistent(100, 60, 20, 20, 20, 0) is True


@pytest.mark.parametrize("net_exports", [-10, 0, 20, 30])
def test_ISバランスの整合は支出面の恒等式の成立と一致する(net_exports: float) -> None:
    income, consumption, investment, government, tax = 500, 290, 110, 80, 80
    expenditure = consumption + investment + government + net_exports
    consistent = is_balance_consistent(
        income, consumption, investment, government, tax, net_exports
    )
    assert consistent == (income == expenditure)


def test_傾きが0なら為替レートが動いても純輸出は変わらない() -> None:
    assert net_exports_from_exchange_rate(200, 20, 125, 0) == pytest.approx(20)


def test_純輸出が0のときの浮動小数点数の誤差は許す() -> None:
    assert is_balance_consistent(0.3, 0.1, 0.1, 0.1, 0, 0) is True
