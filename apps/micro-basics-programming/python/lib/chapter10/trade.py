"""国際貿易（小国の仮定）と関税。

小国は、世界価格を、与えられたものとして受け入れる。国内の価格 = 世界価格のもとで、
国内の需要量と供給量の差が、輸入（または輸出）になる。
- 自由貿易: 輸入国は、消費者余剰が増え、生産者余剰が減る。輸出国は、逆。
  どちらも、総余剰は増える
- 関税: 国内価格が、世界価格 + 関税に上がり、輸入が減る。死荷重の三角形が、2 つできる
"""

from dataclasses import dataclass, replace

from lib.chapter01.validation import validate_non_negative, validate_positive
from lib.chapter08.market import (
    LinearMarket,
    equilibrium,
    quantity_demanded,
    quantity_supplied,
)
from lib.chapter09.surplus import consumer_surplus, producer_surplus


@dataclass(frozen=True)
class TradeResult:
    """ある国内価格のもとの、需要・供給・輸入（負なら輸出）と、余剰。"""

    domestic_price: float
    quantity_demanded: float
    quantity_supplied: float
    net_imports: float
    consumer_surplus: float
    producer_surplus: float
    tariff_revenue: float

    @property
    def total_surplus(self) -> float:
        """総余剰 = 消費者余剰 + 生産者余剰 + 関税収入。"""
        return self.consumer_surplus + self.producer_surplus + self.tariff_revenue


def _result(market: LinearMarket, price: float) -> TradeResult:
    demanded = quantity_demanded(market, price)
    supplied = quantity_supplied(market, price)
    return TradeResult(
        price,
        demanded,
        supplied,
        demanded - supplied,
        consumer_surplus(market, price),
        producer_surplus(market, price),
        0.0,
    )


def autarky_result(market: LinearMarket) -> TradeResult:
    """閉鎖経済（貿易なし）の結果。国内の均衡で、輸入は 0。"""
    price, _ = equilibrium(market)
    return _result(market, price)


def free_trade_result(market: LinearMarket, world_price: float) -> TradeResult:
    """自由貿易の結果。国内価格 = 世界価格。輸入 = 需要量 − 供給量（負なら輸出）。"""
    validate_positive(world_price, "世界価格は、正にする")
    return _result(market, world_price)


def gains_from_trade(market: LinearMarket, world_price: float) -> float:
    """貿易の利益 = 自由貿易の総余剰 − 閉鎖経済の総余剰。輸入国でも輸出国でも、正。"""
    return (
        free_trade_result(market, world_price).total_surplus
        - autarky_result(market).total_surplus
    )


def tariff_result(
    market: LinearMarket, world_price: float, tariff: float
) -> TradeResult:
    """関税（輸入 1 単位あたり tariff 円）のもとの結果。輸入国だけが対象。

    国内価格は、世界価格 + 関税。ただし、閉鎖経済の均衡価格を超えない
    （超えれば、輸入がなくなる）。
    """
    validate_positive(world_price, "世界価格は、正にする")
    validate_non_negative(tariff, "関税は、0 以上にする")
    autarky_price, _ = equilibrium(market)
    if world_price >= autarky_price:
        raise ValueError(
            "関税がかかるのは、輸入国だけ（世界価格が、閉鎖経済の価格より低い）"
        )
    result = _result(market, min(world_price + tariff, autarky_price))
    return replace(result, tariff_revenue=tariff * result.net_imports)


def tariff_deadweight_loss(
    market: LinearMarket, world_price: float, tariff: float
) -> float:
    """関税の死荷重 = 自由貿易の総余剰 − 関税のもとの総余剰。"""
    return (
        free_trade_result(market, world_price).total_surplus
        - tariff_result(market, world_price, tariff).total_surplus
    )


def tariff_losses(
    market: LinearMarket, world_price: float, tariff: float
) -> tuple[float, float]:
    """関税の死荷重の、2 つの三角形 (生産の歪み, 消費の歪み)。

    生産の歪み: 国内価格が上がり、割高な国内生産が増える。消費の歪み: 消費が減る。
    """
    free = free_trade_result(market, world_price)
    taxed = tariff_result(market, world_price, tariff)
    rise = taxed.domestic_price - world_price
    production = 0.5 * rise * (taxed.quantity_supplied - free.quantity_supplied)
    consumption = 0.5 * rise * (free.quantity_demanded - taxed.quantity_demanded)
    return production, consumption
