"""絶対優位・比較優位・生産可能性フロンティア（リカードの 2 財モデル）。

1 単位を作るのに必要な労働者の数（人）で、技術を表す。
- 絶対優位: 必要な労働が、少ない国（生産性が高い）
- 比較優位: 機会費用が、低い国（相対的に得意）。全部の財で、比較優位のある国は、ない
"""

import math
from dataclasses import dataclass

from lib.chapter01.validation import validate_positive

_TOLERANCE = 1e-9  # 浮動小数点の誤差だけの差は、同じと見なす
_GOODS = ("industry", "agriculture")


@dataclass(frozen=True)
class Country:
    """国の技術。工業・農業の、1 単位あたりの必要な労働者数（人）。"""

    name: str
    labor_industry: float
    labor_agriculture: float

    def __post_init__(self) -> None:
        validate_positive(self.labor_industry, "工業 1 単位に必要な労働は、正にする")
        validate_positive(self.labor_agriculture, "農業 1 単位に必要な労働は、正にする")


def _check_good(good: str) -> None:
    if good not in _GOODS:
        raise ValueError("財は、industry か agriculture にする")


def opportunity_cost_of_industry(country: Country) -> float:
    """工業 1 単位を作るために、あきらめる農業の量。"""
    return country.labor_industry / country.labor_agriculture


def opportunity_cost_of_agriculture(country: Country) -> float:
    """農業 1 単位を作るために、あきらめる工業の量。"""
    return country.labor_agriculture / country.labor_industry


def _labor(country: Country, good: str) -> float:
    _check_good(good)
    return country.labor_industry if good == "industry" else country.labor_agriculture


def _cost(country: Country, good: str) -> float:
    _check_good(good)
    if good == "industry":
        return opportunity_cost_of_industry(country)
    return opportunity_cost_of_agriculture(country)


def absolute_advantage(a: Country, b: Country, good: str) -> str | None:
    """財 good の、絶対優位のある国の名前。必要な労働が同じなら、None。"""
    if math.isclose(_labor(a, good), _labor(b, good), rel_tol=_TOLERANCE):
        return None
    return a.name if _labor(a, good) < _labor(b, good) else b.name


def comparative_advantage(a: Country, b: Country, good: str) -> str | None:
    """財 good の、比較優位のある国の名前。機会費用が同じなら、None。"""
    if math.isclose(_cost(a, good), _cost(b, good), rel_tol=_TOLERANCE):
        return None
    return a.name if _cost(a, good) < _cost(b, good) else b.name


def ppf_endpoints(
    country: Country, labor: float
) -> tuple[tuple[float, float], tuple[float, float]]:
    """生産可能性フロンティアの両端 ((工業の最大, 0), (0, 農業の最大))。

    傾きの大きさは、工業の機会費用。
    """
    validate_positive(labor, "労働量は、正にする")
    return (labor / country.labor_industry, 0.0), (
        0.0,
        labor / country.labor_agriculture,
    )


def mutually_beneficial_terms(a: Country, b: Country) -> tuple[float, float]:
    """両国が得をする、交換比率（工業 1 単位と交換する農業の量）の範囲 (下限, 上限)。

    2 国の、工業の機会費用の間にある。範囲の外では、一方の国が、損をする。
    """
    costs = (opportunity_cost_of_industry(a), opportunity_cost_of_industry(b))
    return min(costs), max(costs)


def trade_gain_per_unit(own_opportunity_cost: float, terms_of_trade: float) -> float:
    """輸出する財 1 単位あたりの利益 = 交換で得られる量 − 自国で作るときの機会費用。"""
    return terms_of_trade - own_opportunity_cost
