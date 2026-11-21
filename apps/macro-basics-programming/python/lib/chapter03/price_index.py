"""物価指数（ラスパイレス・パーシェ）と、名目・実質 GDP、GDP デフレータ。"""

from collections.abc import Sequence

import pandas as pd


def _spending(prices: Sequence[float], quantities: Sequence[float]) -> float:
    """支出額 = 価格 × 数量 の合計。品目の数が違えばエラー。"""
    if len(prices) != len(quantities):
        raise ValueError("価格と数量は、同じ長さ（品目の数）にする")
    return sum(p * q for p, q in zip(prices, quantities, strict=True))


def _ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        raise ValueError("基準時の支出が 0 で、指数を計算できない")
    return numerator / denominator


def laspeyres(
    base_prices: Sequence[float],
    base_quantities: Sequence[float],
    current_prices: Sequence[float],
) -> float:
    """ラスパイレス指数 = Σ(比較時の価格 × 基準時の数量) ÷ Σ(基準時の支出)。

    数量は、基準時のものを使う。
    """
    return _ratio(
        _spending(current_prices, base_quantities),
        _spending(base_prices, base_quantities),
    )


def paasche(
    base_prices: Sequence[float],
    current_prices: Sequence[float],
    current_quantities: Sequence[float],
) -> float:
    """パーシェ指数 = Σ(比較時の価格 × 比較時の数量) ÷ Σ(基準時の価格 × 比較時の数量)。

    数量は、比較時のものを使う。
    """
    return _ratio(
        _spending(current_prices, current_quantities),
        _spending(base_prices, current_quantities),
    )


def real_gdp(nominal: float, deflator: float) -> float:
    """実質 GDP = 名目 GDP ÷ GDP デフレータ × 100（デフレータは、基準時 = 100）。"""
    if deflator <= 0:
        raise ValueError("GDP デフレータは、正の値にする")
    return nominal / deflator * 100


def gdp_deflator(nominal: float, real: float) -> float:
    """GDP デフレータ = 名目 GDP ÷ 実質 GDP × 100。"""
    if real == 0:
        raise ValueError("実質 GDP が 0 で、デフレータを計算できない")
    return nominal / real * 100


def price_indexes(
    prices: pd.DataFrame, quantities: pd.DataFrame, base: str
) -> pd.DataFrame:
    """各期のラスパイレス指数とパーシェ指数の表（行は期間、列は laspeyres・paasche）。

    prices・quantities は、行が期間、列が品目の表。base は、基準時の期間の名前。
    """
    if not (
        prices.index.equals(quantities.index)
        and prices.columns.equals(quantities.columns)
    ):
        raise ValueError("価格と数量の表は、期間と品目をそろえる")
    if base not in prices.index:
        raise ValueError(f"基準時 {base} が、表の期間にない")
    base_prices, base_quantities = prices.loc[base], quantities.loc[base]
    # 基準時の価格で測った、各期の支出。基準時の値が、基準時の支出
    paasche_base = (quantities * base_prices).sum(axis=1)
    if (paasche_base == 0).any():
        raise ValueError("基準時の支出が 0 の期間があり、指数を計算できない")
    base_spending = paasche_base[base]
    return pd.DataFrame(
        {
            "laspeyres": (prices * base_quantities).sum(axis=1) / base_spending,
            "paasche": (prices * quantities).sum(axis=1) / paasche_base,
        }
    )
