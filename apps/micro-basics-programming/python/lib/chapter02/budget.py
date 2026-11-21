"""予算制約と最適消費。

予算制約線 Px·x + Py·y = m は、所得 m を使い切る組み合わせ。
最適消費点は、予算線の上で、効用が最大になる点（無差別曲線と、予算線が接する点）。
コブ・ダグラス型 U = x^a · y^b では、所得の a/(a+b) を財 x に、b/(a+b) を財 y に使う。
"""

from lib.chapter01.utility import (
    cobb_douglas_utility,
    marginal_rate_of_substitution,
)
from lib.chapter01.validation import validate_non_negative, validate_positive

# 予算線の上かの判定で、浮動小数点の誤差を許す
_AFFORDABLE_TOLERANCE = 1e-9


def _check_budget(income: float, px: float, py: float) -> None:
    validate_non_negative(income, "所得は、0 以上にする")
    validate_positive(px, "財 x の価格は、正にする")
    validate_positive(py, "財 y の価格は、正にする")


def _check_exponents(a: float, b: float) -> None:
    validate_positive(a, "べき指数 a は、正にする")
    validate_positive(b, "べき指数 b は、正にする")


def budget_line_y(income: float, px: float, py: float, x: float) -> float:
    """予算線の上の、財 y の量。y = (m − Px·x) ÷ Py。"""
    _check_budget(income, px, py)
    return (income - px * x) / py


def budget_slope(px: float, py: float) -> float:
    """予算線の傾き −Px ÷ Py（価格比のマイナス）。"""
    validate_positive(px, "財 x の価格は、正にする")
    validate_positive(py, "財 y の価格は、正にする")
    return -px / py


def budget_intercepts(income: float, px: float, py: float) -> tuple[float, float]:
    """予算線の切片 (m ÷ Px, m ÷ Py)。全部を、財 x だけ・財 y だけに使った量。"""
    _check_budget(income, px, py)
    return income / px, income / py


def is_affordable(x: float, y: float, income: float, px: float, py: float) -> bool:
    """組み合わせ (x, y) が、所得で買えるか（予算線の上か内側か）。"""
    _check_budget(income, px, py)
    return px * x + py * y <= income + _AFFORDABLE_TOLERANCE


def optimal_bundle(
    income: float, px: float, py: float, a: float = 1.0, b: float = 1.0
) -> tuple[float, float]:
    """コブ・ダグラス型の最適消費点（閉じた式）。

    x = a/(a+b) · m/Px、y = b/(a+b) · m/Py。所得の割合を、指数の比で配分する。
    """
    _check_budget(income, px, py)
    _check_exponents(a, b)
    share_x = a / (a + b)
    return share_x * income / px, (1 - share_x) * income / py


def optimal_bundle_by_grid(
    income: float,
    px: float,
    py: float,
    a: float = 1.0,
    b: float = 1.0,
    steps: int = 400,
) -> tuple[float, float]:
    """予算線の上を steps 等分して、効用が最大の点を探す（閉じた式の答え合わせ用）。"""
    _check_budget(income, px, py)
    _check_exponents(a, b)
    validate_positive(steps - 1, "格子の分割数は、2 以上にする")
    x_max = income / px
    xs = [x_max * i / steps for i in range(steps + 1)]
    points = [(x, max(0.0, (income - px * x) / py)) for x in xs]
    # 効用が同じ点が複数あれば、先に見つけた点（x の小さいほう）を返す
    return max(points, key=lambda p: cobb_douglas_utility(p[0], p[1], a, b))


def tangency_gap(
    x: float, y: float, px: float, py: float, a: float = 1.0, b: float = 1.0
) -> float:
    """限界代替率と価格比の差 MRS − Px ÷ Py。

    最適消費点では 0（無差別曲線が、予算線に接する）。
    """
    validate_positive(px, "財 x の価格は、正にする")
    validate_positive(py, "財 y の価格は、正にする")
    return marginal_rate_of_substitution(x, y, a, b) - px / py
