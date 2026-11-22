"""ベクトルを、リスト（標準ライブラリ）で扱う。内積・大きさ・なす角・平均と分散・直線の式。"""

import math
from collections.abc import Sequence


def vector_dot(u: Sequence[float], v: Sequence[float]) -> float:
    """内積 u·v = u₁v₁ + u₂v₂ + … + uₙvₙ。長さが違えば ValueError（zip の strict）。"""
    return sum(a * b for a, b in zip(u, v, strict=True))


def vector_length(v: Sequence[float]) -> float:
    """大きさ |v| = √(v·v)。"""
    return math.sqrt(vector_dot(v, v))


def vector_angle_degrees(u: Sequence[float], v: Sequence[float]) -> float:
    """2 本のベクトルのなす角（度）。cos θ = u·v ÷ (|u||v|)。"""
    lengths = vector_length(u) * vector_length(v)
    if lengths == 0:
        raise ValueError("0 ベクトルとのなす角は、決まりません")
    cosine = vector_dot(u, v) / lengths
    # 丸め誤差で ±1 をわずかに超えると、acos が ValueError を出すので、範囲に収める
    return math.degrees(math.acos(max(-1.0, min(1.0, cosine))))


def mean_by_dot(xs: Sequence[float]) -> float:
    """平均 = x·1 ÷ n（1 は、成分がすべて 1 のベクトル）。"""
    if not xs:
        raise ValueError("空のデータの平均は、決まりません")
    return vector_dot(xs, [1] * len(xs)) / len(xs)


def variance_by_dot(xs: Sequence[float]) -> float:
    """分散 = d·d ÷ n（d は、平均からの偏差のベクトル）。"""
    mean = mean_by_dot(xs)
    deviations = [x - mean for x in xs]
    return vector_dot(deviations, deviations) / len(xs)


def line_normal_form(
    p: Sequence[float], q: Sequence[float]
) -> tuple[list[float], float]:
    """2 点 p・q を通る直線を、n·x = c（n は法線ベクトル）の形で表す。"""
    direction = [q[0] - p[0], q[1] - p[1]]
    if direction == [0, 0]:
        raise ValueError("同じ 2 点では、直線が決まりません")
    normal = [direction[1], -direction[0]]
    return normal, vector_dot(normal, p)
