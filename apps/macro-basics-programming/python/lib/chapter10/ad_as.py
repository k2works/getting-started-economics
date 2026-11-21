"""総需要（AD）と総供給（AS）。

AD は、IS-LM から導く。物価 P が上がると、実質貨幣供給 M/P が減り、LM が左へ動いて、
均衡の所得が減る（右下がり）。AS は、労働市場から導く。古典派は完全雇用所得で垂直、
ケインズは右上がりのち垂直。
"""

from collections.abc import Callable
from dataclasses import dataclass, replace

from lib.chapter01.validation import validate_positive
from lib.chapter08.is_lm import solve_is_lm

_BISECTION_STEPS = 200


@dataclass(frozen=True)
class AdEconomy:
    """IS-LM を作る定数。IS: (1 − c)Y + b·r = A、LM: k·Y − h·r = M/P。"""

    mpc: float
    b: float
    intercept: float
    k: float
    h: float
    nominal_money: float


def _check_price(price: float) -> None:
    validate_positive(price, "物価は、正にする")


def aggregate_demand_income(economy: AdEconomy, price: float) -> float:
    """AD 上の所得。実質貨幣供給 M/P で、第 8 章の IS-LM を解いた均衡所得。"""
    _check_price(price)
    income, _ = solve_is_lm(
        economy.mpc,
        economy.b,
        economy.intercept,
        economy.k,
        economy.h,
        economy.nominal_money / price,
    )
    return income


def classical_supply(price: float, full_employment_income: float) -> float:
    """古典派の AS。物価によらず、完全雇用所得（垂直）。"""
    _check_price(price)
    return full_employment_income


def keynesian_supply(
    price: float, full_employment_income: float, base_income: float, slope: float
) -> float:
    """ケインズの AS。Y = min(完全雇用所得, 基準の所得 + 傾き × P)。"""
    _check_price(price)
    validate_positive(slope, "総供給の傾きは、正にする")
    return min(full_employment_income, base_income + slope * price)


def solve_ad_as(
    economy: AdEconomy,
    supply: Callable[[float], float],
    price_low: float = 0.01,
    price_high: float = 100.0,
) -> tuple[float, float]:
    """AD と AS の交点 (物価, 所得)。二分法で、AD − AS = 0 となる物価を探す。

    AD は物価の減少関数、AS は非減少関数なので、AD − AS は物価とともに減る。
    """

    def gap(price: float) -> float:
        return aggregate_demand_income(economy, price) - supply(price)

    low, high = price_low, price_high
    if gap(low) < 0 or gap(high) > 0:
        raise ValueError("探す範囲に、AD と AS の交点が無い")
    for _ in range(_BISECTION_STEPS):
        middle = (low + high) / 2
        if gap(middle) > 0:
            low = middle
        else:
            high = middle
    price = (low + high) / 2
    return price, supply(price)


def expand_demand(
    economy: AdEconomy, delta_government: float = 0, delta_nominal_money: float = 0
) -> AdEconomy:
    """政府支出の増加 ΔG と、名目貨幣供給の増加で、AD を右へ動かした経済。"""
    return replace(
        economy,
        intercept=economy.intercept + delta_government,
        nominal_money=economy.nominal_money + delta_nominal_money,
    )


def shift_supply(
    full_employment_income: float, base_income: float, gain: float
) -> tuple[float, float]:
    """生産性の向上（gain > 0）で AS を右へ。負なら左へ。動かした後の両方の値を返す。"""
    if full_employment_income + gain <= 0:
        raise ValueError("動かしたあとの完全雇用所得が、0 以下になる")
    return full_employment_income + gain, base_income + gain
