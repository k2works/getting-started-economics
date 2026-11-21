"""三面等価: 生産・分配・支出の GDP と、在庫品増加。"""

from collections.abc import Sequence


def gdp_production(output: Sequence[float], intermediate: Sequence[float]) -> float:
    """生産面の GDP = 産出額の合計 − 中間投入の合計（付加価値の合計）。"""
    if len(output) != len(intermediate):
        raise ValueError("産出額と中間投入は、同じ長さ（産業の数）にする")
    return sum(output) - sum(intermediate)


def gdp_distribution(
    compensation: float,
    operating_surplus: float,
    depreciation: float,
    indirect_taxes: float,
    subsidies: float,
) -> float:
    """分配面の GDP = 雇用者報酬 + 営業余剰 + 固定資本減耗 + 間接税 − 補助金。"""
    return compensation + operating_surplus + depreciation + indirect_taxes - subsidies


def gdp_expenditure(
    consumption: float,
    government: float,
    fixed_capital_formation: float,
    inventory: float,
    net_exports: float,
) -> float:
    """支出面の GDP = 民間消費 + 政府消費 + 総固定資本形成 + 在庫品増加 + 純輸出。"""
    return consumption + government + fixed_capital_formation + inventory + net_exports


def inventory_change(production: float, sales: float) -> float:
    """在庫品増加 = 生産 − 販売。売れ残りは、在庫への投資として、支出に数える。"""
    return production - sales


def is_three_way_equal(
    production: float,
    distribution: float,
    expenditure: float,
    tolerance: float = 1e-9,
) -> bool:
    """3 つの面の GDP の、最大と最小の差が、誤差 tolerance 以内か。"""
    values = (production, distribution, expenditure)
    return max(values) - min(values) <= tolerance
