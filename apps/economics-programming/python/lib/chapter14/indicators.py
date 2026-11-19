"""フィリップス曲線・需給ギャップ・オークンの法則・フィッシャー方程式・貨幣数量説。"""


def phillips_inflation(
    unemployment: float,
    natural_rate: float,
    expected_inflation: float,
    slope: float,
) -> float:
    """フィリップス曲線。

    物価上昇率 = 期待物価上昇率 - slope × (失業率 - 自然失業率)。
    """
    return expected_inflation - slope * (unemployment - natural_rate)


def output_gap(actual: float, potential: float) -> float:
    """需給ギャップ（%）= (実際の GDP - 潜在 GDP) ÷ 潜在 GDP × 100。"""
    if potential <= 0:
        raise ValueError("潜在 GDP は正でなければならない")
    return (actual - potential) / potential * 100


def okun_unemployment(
    gap: float, natural_rate: float, coefficient: float = 0.5
) -> float:
    """オークンの法則: 失業率 = 自然失業率 - 係数 × 需給ギャップ。"""
    return natural_rate - coefficient * gap


def real_interest_rate(nominal: float, inflation: float) -> float:
    """フィッシャー方程式: 実質利子率 = 名目利子率 - インフレ率。"""
    return nominal - inflation


def price_level_by_quantity_theory(
    money_supply: float, velocity: float, real_income: float
) -> float:
    """貨幣数量説（交換方程式 MV = PY）から、物価水準 P = MV ÷ Y を求める。"""
    if real_income <= 0:
        raise ValueError("実質所得は正でなければならない")
    return money_supply * velocity / real_income
