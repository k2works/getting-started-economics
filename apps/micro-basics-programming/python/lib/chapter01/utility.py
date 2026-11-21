"""効用と無差別曲線。

効用関数 U(x, y) が同じ値になる点を結んだ線が、無差別曲線。
コブ・ダグラス型 U = x^a · y^b は、原点に凸の、ふつうの形をした無差別曲線を作る。
"""

import math
from collections.abc import Sequence

from lib.chapter01.validation import validate_non_negative, validate_positive

# 凸の判定で、直線（2 階差分が 0）に乗る、浮動小数点の誤差を許す
_CONVEX_TOLERANCE = 1e-9


def _check_goods(x: float, y: float) -> None:
    validate_non_negative(x, "財 x の量は、0 以上にする")
    validate_non_negative(y, "財 y の量は、0 以上にする")


def _check_exponents(a: float, b: float) -> None:
    validate_positive(a, "べき指数 a は、正にする")
    validate_positive(b, "べき指数 b は、正にする")


def cobb_douglas_utility(x: float, y: float, a: float = 1.0, b: float = 1.0) -> float:
    """コブ・ダグラス型の効用 U = x^a · y^b。a = b = 1 なら、財の量の積。"""
    _check_goods(x, y)
    _check_exponents(a, b)
    return float(x**a * y**b)


def indifference_curve_y(
    level: float, x: float, a: float = 1.0, b: float = 1.0
) -> float:
    """効用が level になる点の、財 y の量。

    U = x^a · y^b から、y = (level ÷ x^a)^(1/b)。
    """
    validate_positive(level, "効用の水準は、正にする")
    validate_positive(
        x, "財 x の量は、正にする（無差別曲線は、x = 0 で、無限大になる）"
    )
    _check_exponents(a, b)
    return float((level / x**a) ** (1 / b))


def marginal_rate_of_substitution(
    x: float, y: float, a: float = 1.0, b: float = 1.0
) -> float:
    """限界代替率 MRS = (a · y) ÷ (b · x)。

    財 x を 1 単位減らすとき、効用を保つのに必要な財 y の増加量。
    """
    validate_positive(x, "財 x の量は、正にする")
    validate_non_negative(y, "財 y の量は、0 以上にする")
    _check_exponents(a, b)
    return (a * y) / (b * x)


def perfect_substitutes_utility(
    x: float, y: float, a: float = 1.0, b: float = 1.0
) -> float:
    """完全代替財の効用 U = a·x + b·y。限界代替率は、いつも a ÷ b。"""
    _check_goods(x, y)
    _check_exponents(a, b)
    return a * x + b * y


def perfect_substitutes_curve_y(
    level: float, x: float, a: float = 1.0, b: float = 1.0
) -> float:
    """完全代替財の無差別曲線（直線）。y = (level − a·x) ÷ b。"""
    _check_exponents(a, b)
    return (level - a * x) / b


def perfect_complements_utility(x: float, y: float) -> float:
    """完全補完財の効用 U = min(x, y)。多すぎるほうの量は、効用を増やさない。"""
    _check_goods(x, y)
    return min(x, y)


def perfect_complements_curve(level: float, x_max: float) -> list[tuple[float, float]]:
    """完全補完財の無差別曲線（L 字）の 3 点。折れ点は (level, level)。"""
    validate_positive(level, "効用の水準は、正にする")
    if x_max < level:
        raise ValueError("L 字の端は、効用の水準以上にする")
    return [(level, x_max), (level, level), (x_max, level)]


def bad_good_utility(x: float, y: float, weight: float = 1.0) -> float:
    """財 x がマイナスの財（騒音など）のときの効用 U = y − weight·x。"""
    validate_positive(weight, "マイナスの財の重みは、正にする")
    return y - weight * x


def bad_good_curve_y(level: float, x: float, weight: float = 1.0) -> float:
    """マイナスの財の無差別曲線。y = level + weight·x（右上がり）。"""
    validate_positive(weight, "マイナスの財の重みは、正にする")
    return level + weight * x


def concave_utility(x: float, y: float) -> float:
    """別々に消費したいときの効用 U = x² + y²。無差別曲線は、原点に凹。"""
    _check_goods(x, y)
    return x**2 + y**2


def concave_curve_y(level: float, x: float) -> float:
    """U = x² + y² の無差別曲線。y = √(level − x²)。x は √level 以下の範囲だけ。"""
    if x**2 > level:
        raise ValueError("x が、曲線の範囲（√効用の水準）を、超えている")
    return math.sqrt(level - x**2)


def is_convex_to_origin(xs: Sequence[float], ys: Sequence[float]) -> bool:
    """曲線 y(x) が、原点に凸（下に凸）か。

    傾きが、x とともに増える（傾きの大きさは、小さくなる）なら、凸。
    """
    if len(xs) != len(ys):
        raise ValueError("x と y は、同じ長さにする")
    if len(xs) < 3:
        raise ValueError("凸の判定には、3 点以上が必要")
    if any(b <= a for a, b in zip(xs, xs[1:], strict=False)):
        raise ValueError("x は、昇順にする")
    slopes = [
        (y2 - y1) / (x2 - x1)
        for (x1, y1), (x2, y2) in zip(
            zip(xs, ys, strict=True), zip(xs[1:], ys[1:], strict=True), strict=False
        )
    ]
    return all(
        b - a >= -_CONVEX_TOLERANCE for a, b in zip(slopes, slopes[1:], strict=False)
    )
