"""価格弾力性と所得弾力性。"""


def price_elasticity(
    price_before: float,
    price_after: float,
    quantity_before: float,
    quantity_after: float,
) -> float:
    """価格弾力性 = -(需要量の変化率) / (価格の変化率) を返す。"""
    if price_after == price_before:
        raise ValueError("価格が変わらないので価格弾力性は求められない")
    price_change_rate = (price_after - price_before) / price_before
    quantity_change_rate = (quantity_after - quantity_before) / quantity_before
    return -quantity_change_rate / price_change_rate


def income_elasticity(
    income_before: float,
    income_after: float,
    quantity_before: float,
    quantity_after: float,
) -> float:
    """所得弾力性 = (需要量の変化率) / (所得の変化率) を返す。"""
    if income_after == income_before:
        raise ValueError("所得が変わらないので所得弾力性は求められない")
    income_change_rate = (income_after - income_before) / income_before
    quantity_change_rate = (quantity_after - quantity_before) / quantity_before
    return quantity_change_rate / income_change_rate


def classify_income_elasticity(elasticity: float) -> str:
    """所得弾力性から財を分類する。

    1 以上は奢侈品、0 以上 1 未満は必需品、負は下級財。
    """
    if elasticity >= 1:
        return "奢侈品"
    if elasticity >= 0:
        return "必需品"
    return "下級財"


def is_price_elastic(elasticity: float) -> bool:
    """価格弾力性が 1 より大きければ弾力的。"""
    return elasticity > 1
