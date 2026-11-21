"""開放経済: 為替レートと純輸出、購買力平価、IS バランス。"""

import math


def net_exports_from_exchange_rate(
    exchange_rate: float,
    base_net_exports: float,
    base_rate: float,
    slope: float,
) -> float:
    """純輸出 X = X0 + s(e − e0)。e は、1 ドルあたりの円（上がると円安）。

    円安（e が上がる）と、輸出が増え、輸入が減るので、純輸出は増える。
    傾き s は、0 以上にする。
    """
    if slope < 0:
        raise ValueError("為替レートに対する純輸出の傾きは、0 以上にする")
    return base_net_exports + slope * (exchange_rate - base_rate)


def ppp_exchange_rate(domestic_price: float, foreign_price: float) -> float:
    """購買力平価 = 自国の価格 ÷ 外国の価格（1 ドルあたりの円）。"""
    if foreign_price == 0:
        raise ValueError("外国の価格が 0 のとき、購買力平価は計算できない")
    return domestic_price / foreign_price


def ppp_after_inflation(
    domestic_price: float, foreign_price: float, domestic_inflation: float
) -> float:
    """自国の物価が上がったあとの、購買力平価。上がると、円安になる。"""
    if domestic_inflation <= -1:
        raise ValueError("物価上昇率は、−1（−100%）より大きくする")
    return ppp_exchange_rate(domestic_price * (1 + domestic_inflation), foreign_price)


def net_exports_from_balance(
    saving: float, investment: float, tax: float, government: float
) -> float:
    """IS バランス X = (S − I) + (T − G)。純輸出 = 民間の貯蓄超過 + 財政黒字。"""
    return (saving - investment) + (tax - government)


def is_balance_consistent(
    income: float,
    consumption: float,
    investment: float,
    government: float,
    tax: float,
    net_exports: float,
) -> bool:
    """支出面 Y = C + I + G + X と、IS バランスが、同じ結論になるかを確かめる。"""
    saving = income - tax - consumption
    balance = net_exports_from_balance(saving, investment, tax, government)
    return math.isclose(balance, net_exports, abs_tol=1e-9)
