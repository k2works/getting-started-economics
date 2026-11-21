"""GDP と付加価値、フローとストック、成長会計。"""

from collections.abc import Sequence
from dataclasses import dataclass

# GDP に含めるもの（帰属計算を含む）と、含めないもの
_INCLUDED = {"政府サービス", "持ち家の家賃", "農家の自家消費"}
_EXCLUDED = {"キャピタルゲイン", "中古品の売買", "家事労働"}


def value_added(output: Sequence[float], intermediate: Sequence[float]) -> list[float]:
    """各段階の付加価値 = 生産額 − 中間投入。"""
    if len(output) != len(intermediate):
        raise ValueError("生産額と中間投入は、同じ長さ（段階の数）にする")
    if any(i > o for o, i in zip(output, intermediate, strict=True)):
        raise ValueError("中間投入が、生産額より大きい段階がある")
    return [o - i for o, i in zip(output, intermediate, strict=True)]


def gdp_from_stages(output: Sequence[float], intermediate: Sequence[float]) -> float:
    """付加価値の合計。最終財の価値に等しい。"""
    return sum(value_added(output, intermediate))


def gni(gdp: float, income_from_abroad: float, income_to_abroad: float) -> float:
    """GNI = GDP + 海外からの受取 − 海外への支払。"""
    return gdp + income_from_abroad - income_to_abroad


def ndp(gdp: float, depreciation: float) -> float:
    """NDP = GDP − 固定資本減耗。"""
    return gdp - depreciation


def is_in_gdp(item: str) -> bool:
    """項目が、GDP に含まれるか。政府サービス・持ち家の家賃などは、帰属計算で含める。"""
    if item in _INCLUDED:
        return True
    if item in _EXCLUDED:
        return False
    raise ValueError(f"知らない項目: {item}")


def stock_path(initial: float, flows: Sequence[float]) -> list[float]:
    """ストックの経路。各期のストック = 前の期のストック + その期のフロー。"""
    path = [initial]
    for flow in flows:
        path.append(path[-1] + flow)
    return path


@dataclass(frozen=True)
class GrowthAccounting:
    """成長会計の結果（単位は、すべて % ポイント）。"""

    growth: float
    labor: float
    capital: float
    technology: float


def growth_accounting(
    growth: float,
    labor_growth: float,
    labor_share: float,
    capital_growth: float,
    capital_share: float,
) -> GrowthAccounting:
    """成長率 = 労働分配率 × 労働増加率 + 資本分配率 × 資本増加率 + 技術進歩率。

    技術進歩率（全要素生産性の成長率）は、残差として求める。
    """
    if abs(labor_share + capital_share - 1) > 1e-9:
        raise ValueError("労働分配率と資本分配率の合計が 1 でない")
    labor = labor_share * labor_growth
    capital = capital_share * capital_growth
    return GrowthAccounting(growth, labor, capital, growth - labor - capital)
