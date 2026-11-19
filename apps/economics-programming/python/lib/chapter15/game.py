"""ゲーム理論: 2 人のゲームの純粋戦略ナッシュ均衡。"""

from collections.abc import Mapping

# 小数の計算誤差を許す幅
_EPSILON = 1e-9

Payoffs = Mapping[tuple[str, str], tuple[float, float]]


def _is_best_for_row(payoffs: Payoffs, rows: list[str], row: str, col: str) -> bool:
    """列プレイヤーが col を選んでいるとき、行プレイヤーにとって row が最適か。"""
    return all(payoffs[(r, col)][0] <= payoffs[(row, col)][0] + _EPSILON for r in rows)


def _is_best_for_col(payoffs: Payoffs, cols: list[str], row: str, col: str) -> bool:
    """行プレイヤーが row を選んでいるとき、列プレイヤーにとって col が最適か。"""
    return all(payoffs[(row, c)][1] <= payoffs[(row, col)][1] + _EPSILON for c in cols)


def pure_nash_equilibria(payoffs: Payoffs) -> list[tuple[str, str]]:
    """互いに相手の選択に対して最適な組（純粋戦略のナッシュ均衡）をすべて返す。

    payoffs は {(行の戦略, 列の戦略): (行の利得, 列の利得)}。
    """
    rows = list(dict.fromkeys(row for row, _ in payoffs))
    cols = list(dict.fromkeys(col for _, col in payoffs))
    return [
        (row, col)
        for row in rows
        for col in cols
        if _is_best_for_row(payoffs, rows, row, col)
        and _is_best_for_col(payoffs, cols, row, col)
    ]
