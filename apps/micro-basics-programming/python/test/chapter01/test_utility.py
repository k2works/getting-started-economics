"""第 1 章: 効用と無差別曲線のテスト。"""

import math

import pytest

from lib.chapter01.utility import (
    bad_good_curve_y,
    bad_good_utility,
    cobb_douglas_utility,
    concave_curve_y,
    concave_utility,
    indifference_curve_y,
    is_convex_to_origin,
    marginal_rate_of_substitution,
    perfect_complements_curve,
    perfect_complements_utility,
    perfect_substitutes_curve_y,
    perfect_substitutes_utility,
)

# U = x·y。点 (20, 40) の効用は 800
XS = [10, 20, 40, 80]


def test_効用は財の量の積() -> None:
    assert cobb_douglas_utility(20, 40) == 800
    assert cobb_douglas_utility(40, 20) == 800


def test_べき乗の効用() -> None:
    assert cobb_douglas_utility(4, 9, 0.5, 0.5) == pytest.approx(6)


def test_財が増えると効用は増える() -> None:
    assert cobb_douglas_utility(21, 40) > cobb_douglas_utility(20, 40)
    assert cobb_douglas_utility(20, 41) > cobb_douglas_utility(20, 40)


def test_財の量が負ならエラー() -> None:
    with pytest.raises(ValueError, match="0 以上"):
        cobb_douglas_utility(-1, 40)
    with pytest.raises(ValueError, match="0 以上"):
        cobb_douglas_utility(20, -1)


def test_財の量0は許される() -> None:
    assert cobb_douglas_utility(0, 40) == 0


def test_べき指数が正でなければエラー() -> None:
    with pytest.raises(ValueError, match="指数"):
        cobb_douglas_utility(20, 40, 0, 1)
    with pytest.raises(ValueError, match="指数"):
        cobb_douglas_utility(20, 40, 1, -1)


def test_べき指数が1未満の正の値でも有効() -> None:
    assert cobb_douglas_utility(16, 16, 0.25, 0.25) == pytest.approx(4)


def test_無差別曲線は同じ効用の点を結ぶ() -> None:
    for x in XS:
        y = indifference_curve_y(800, x)
        assert cobb_douglas_utility(x, y) == pytest.approx(800)


def test_無差別曲線は右下がり() -> None:
    ys = [indifference_curve_y(800, x) for x in XS]
    assert ys == pytest.approx([80, 40, 20, 10])
    assert all(a > b for a, b in zip(ys, ys[1:], strict=False))


def test_効用の高い無差別曲線は右上にあり交わらない() -> None:
    for x in XS:
        assert indifference_curve_y(1200, x) > indifference_curve_y(800, x)


def test_無差別曲線はべき指数が違っても効用を保つ() -> None:
    y = indifference_curve_y(6, 4, 0.5, 0.5)
    assert y == pytest.approx(9)


def test_無差別曲線のxは正でなければエラー() -> None:
    with pytest.raises(ValueError, match="正"):
        indifference_curve_y(800, 0)


def test_効用の水準は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="正"):
        indifference_curve_y(0, 20)


def test_xが1未満の正の値でも無差別曲線を描ける() -> None:
    assert indifference_curve_y(800, 0.5) == pytest.approx(1600)


def test_限界代替率は財yで測った財xの価値() -> None:
    assert marginal_rate_of_substitution(20, 40) == pytest.approx(2)
    assert marginal_rate_of_substitution(40, 20) == pytest.approx(0.5)


def test_限界代替率は無差別曲線の接線の傾きの大きさ() -> None:
    # 点 (20, 40) の前後 ±0.001 の割線の傾きの大きさ
    h = 0.001
    slope = (indifference_curve_y(800, 20 - h) - indifference_curve_y(800, 20 + h)) / (
        2 * h
    )
    assert slope == pytest.approx(marginal_rate_of_substitution(20, 40), rel=1e-6)


def test_限界代替率は無差別曲線に沿って右へ進むほど小さくなる() -> None:
    values = [
        marginal_rate_of_substitution(x, indifference_curve_y(800, x)) for x in XS
    ]
    assert values == pytest.approx([8, 2, 0.5, 0.125])
    assert all(a > b for a, b in zip(values, values[1:], strict=False))


def test_べき指数のある限界代替率() -> None:
    assert marginal_rate_of_substitution(20, 40, 1, 2) == pytest.approx(1)


def test_限界代替率のxは正でなければエラー() -> None:
    with pytest.raises(ValueError, match="正"):
        marginal_rate_of_substitution(0, 40)


def test_原点に凸の無差別曲線は限界代替率逓減() -> None:
    ys = [indifference_curve_y(800, x) for x in XS]
    assert is_convex_to_origin(XS, ys)


def test_完全代替財の無差別曲線は直線で限界代替率は一定() -> None:
    assert perfect_substitutes_utility(10, 20, 2, 1) == 40
    ys = [perfect_substitutes_curve_y(40, x, 2, 1) for x in (0, 5, 10, 20)]
    assert ys == pytest.approx([40, 30, 20, 0])
    slopes = [b - a for a, b in zip(ys, ys[1:], strict=False)]
    assert slopes[0] / 5 == pytest.approx(-2)
    assert slopes[1] / 5 == pytest.approx(-2)
    assert slopes[2] / 10 == pytest.approx(-2)


def test_完全代替財の無差別曲線は凸の境界で凸と判定される() -> None:
    ys = [perfect_substitutes_curve_y(40, x, 2, 1) for x in (0, 5, 10, 20)]
    assert is_convex_to_origin([0, 5, 10, 20], ys)


def test_完全補完財の効用は少ないほうの量() -> None:
    assert perfect_complements_utility(3, 5) == 3
    assert perfect_complements_utility(5, 3) == 3


def test_完全補完財の無差別曲線はL字() -> None:
    assert perfect_complements_curve(4, 10) == [(4, 10), (4, 4), (10, 4)]


def test_完全補完財の曲線の上の点は効用が同じ() -> None:
    for x, y in perfect_complements_curve(4, 10):
        assert perfect_complements_utility(x, y) == 4


def test_完全補完財の曲線は端が効用の水準より小さければエラー() -> None:
    with pytest.raises(ValueError, match="端"):
        perfect_complements_curve(4, 3)


def test_完全補完財の効用の水準は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="正"):
        perfect_complements_curve(0, 3)


def test_マイナスの財があると無差別曲線は右上がり() -> None:
    assert bad_good_utility(2, 10) == 8
    ys = [bad_good_curve_y(8, x) for x in (0, 2, 4)]
    assert ys == pytest.approx([8, 10, 12])
    assert all(a < b for a, b in zip(ys, ys[1:], strict=False))


def test_マイナスの財の重みが大きいほど傾きが急() -> None:
    assert bad_good_curve_y(8, 2, 3) - bad_good_curve_y(8, 0, 3) == pytest.approx(6)
    assert bad_good_utility(2, 14, 3) == 8


def test_マイナスの財の重みが正でなければエラー() -> None:
    with pytest.raises(ValueError, match="重み"):
        bad_good_utility(2, 10, 0)
    with pytest.raises(ValueError, match="重み"):
        bad_good_curve_y(8, 2, -1)


def test_別々に消費したいときの無差別曲線は原点に凹() -> None:
    assert concave_utility(3, 4) == 25
    xs = [0, 1, 2, 3, 4]
    ys = [concave_curve_y(25, x) for x in xs]
    assert ys[0] == pytest.approx(5)
    assert ys[-1] == pytest.approx(3)
    assert not is_convex_to_origin(xs, ys)
    for x, y in zip(xs, ys, strict=True):
        assert concave_utility(x, y) == pytest.approx(25)


def test_凹の曲線はxが範囲外ならエラー() -> None:
    with pytest.raises(ValueError, match="範囲"):
        concave_curve_y(25, 6)


def test_凸の判定は3点以上が必要() -> None:
    with pytest.raises(ValueError, match="3 点"):
        is_convex_to_origin([1, 2], [2, 1])


def test_凸の判定は点の数が揃っていなければエラー() -> None:
    with pytest.raises(ValueError, match="同じ"):
        is_convex_to_origin([1, 2, 3], [3, 2])


def test_凸の判定は昇順でなければエラー() -> None:
    with pytest.raises(ValueError, match="昇順"):
        is_convex_to_origin([1, 3, 2], [3, 2, 1])


def test_凸の判定は許容誤差を持つ() -> None:
    # 直線（2 階差分 0）に、浮動小数点の誤差が乗っても、凸と判定する
    xs = [0.0, 0.1, 0.2, 0.3]
    ys = [1 - 2 * x for x in xs]
    ys[2] += 1e-15
    assert is_convex_to_origin(xs, ys)


def test_無差別曲線の高さは無限大にならない() -> None:
    assert math.isfinite(indifference_curve_y(800, 1e-3))


# --- 独立した変異確認（2026-11-21）で見つかった穴を埋めるテスト ---


def test_べき指数が違う効用は偶然の一致でない値() -> None:
    assert cobb_douglas_utility(16, 9, 0.5, 0.5) == pytest.approx(12)
    assert cobb_douglas_utility(2, 3, 2, 1) == pytest.approx(12)


def test_べき指数が2の無差別曲線() -> None:
    assert indifference_curve_y(36, 3, 2, 1) == pytest.approx(4)
    assert indifference_curve_y(36, 3, 1, 2) == pytest.approx(2 * math.sqrt(3))


def test_完全代替財の既定の重みは1() -> None:
    assert perfect_substitutes_utility(3, 4) == 7
    assert perfect_substitutes_curve_y(10, 3) == 7


def test_完全代替財の無差別曲線はyの重みで割る() -> None:
    assert perfect_substitutes_curve_y(40, 5, 2, 2) == pytest.approx(15)


def test_完全補完財の曲線の端が水準と等しければ折れ点だけ() -> None:
    assert perfect_complements_curve(4, 4) == [(4, 4), (4, 4), (4, 4)]


def test_凸の判定は同じxが並べばエラー() -> None:
    with pytest.raises(ValueError, match="昇順"):
        is_convex_to_origin([1, 1, 2], [3, 2, 1])


def test_凸の判定は傾きの差で決まる() -> None:
    assert not is_convex_to_origin([0, 1, 2], [0, 1, 0])
    assert is_convex_to_origin([0, 1, 3], [0, 1, 4])


def test_凸の判定は隣り合う傾きを比べる() -> None:
    # 傾きは 0、1、0.5。最後の隣り合う組（1 → 0.5）が、凸でない
    assert not is_convex_to_origin([0, 1, 2, 3], [0, 0, 1, 1.5])


def test_凸の判定の許容誤差は1e_9() -> None:
    # 傾きの差が −8e-10（許容誤差の内）なら凸、−1.2e-9（許容誤差の外）なら凸でない
    assert is_convex_to_origin([0, 1, 2], [0, 1, 2 - 8e-10])
    assert not is_convex_to_origin([0, 1, 2], [0, 1, 2 - 1.2e-9])
