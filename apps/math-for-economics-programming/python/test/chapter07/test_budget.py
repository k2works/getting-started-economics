import pytest

from lib.chapter07.budget import (
    budget_expenditure,
    budget_intercepts,
    budget_line_quantity,
    budget_status,
    consumption_given_leisure,
    full_income,
    lifetime_income_present_value,
    second_period_consumption,
    security_price,
)
from lib.chapter07.vectors import vector_dot


def test_価格2と3で15と10を買う支出は60() -> None:
    assert budget_expenditure([2, 3], [15, 10]) == 60


def test_支出は価格ベクトルと数量ベクトルの内積() -> None:
    pairs: list[tuple[list[float], list[float]]] = [
        ([2, 3], [4, 7]),
        ([1.5, 0.2, 8], [2, 10, 0.5]),
    ]
    for prices, bundle in pairs:
        assert budget_expenditure(prices, bundle) == pytest.approx(
            vector_dot(prices, bundle)
        )


def test_支出は浮動小数点の数を返す() -> None:
    assert type(budget_expenditure([2, 3], [15, 10])) is float


def test_予算線上と予算内と予算外() -> None:
    assert budget_status([2, 3], [15, 10], 60) == "on"
    assert budget_status([2, 3], [10, 12], 60) == "inside"
    assert budget_status([2, 3], [12, 13], 60) == "outside"


def test_3財の予算の判定() -> None:
    assert budget_status([1, 2, 5], [10, 5, 2], 30) == "on"
    assert budget_status([1, 2, 5], [10, 5, 2.1], 30) == "outside"


def test_丸め誤差があっても予算線上と判定する() -> None:
    # 0.1 × 1 + 0.2 × 1 は、浮動小数点では 0.30000000000000004
    assert budget_status([0.1, 0.2], [1, 1], 0.3) == "on"


def test_長さの違う価格と数量の支出は決まらない() -> None:
    with pytest.raises(ValueError):
        budget_expenditure([2, 3], [1, 2, 3])


def test_負の数量や正でない価格では予算を判定しない() -> None:
    with pytest.raises(ValueError):
        budget_status([2, 3], [-1, 5], 60)
    with pytest.raises(ValueError):
        budget_status([2, 0], [1, 5], 60)
    with pytest.raises(ValueError):
        budget_status([-2, 3], [1, 5], 60)


def test_数量0の組合せは所得が正なら予算内で0なら予算線上() -> None:
    assert budget_status([2, 3], [0, 0], 60) == "inside"
    assert budget_status([2, 3], [0, 0], 0) == "on"


def test_予算線の切片は所得を各財の価格で割る() -> None:
    assert budget_intercepts([2, 3], 60) == [30, 20]
    assert budget_intercepts([1, 2, 5], 30) == [30, 15, 6]


def test_予算線上の財2の数量() -> None:
    assert budget_line_quantity([2, 3], 60, 15) == 10
    assert budget_line_quantity([2, 3], 60, 0) == 20
    assert budget_line_quantity([4, 5], 100, 10) == 12


def test_予算線上の2点の差は価格ベクトルと直交する() -> None:
    # 価格ベクトルは、予算線の法線ベクトル
    for prices, income, x1, x2 in [([2, 3], 60, 3, 21), ([4, 5], 100, 1, 24.5)]:
        y1 = budget_line_quantity(prices, income, x1)
        y2 = budget_line_quantity(prices, income, x2)
        assert vector_dot(prices, [x2 - x1, y2 - y1]) == pytest.approx(0)


def test_正でない価格では切片も予算線も決まらない() -> None:
    with pytest.raises(ValueError):
        budget_intercepts([2, 0], 60)
    with pytest.raises(ValueError):
        budget_line_quantity([0, 3], 60, 5)
    with pytest.raises(ValueError):
        budget_line_quantity([2, -3], 60, 5)


def test_財1を切片より多く買うと財2の数量は負になるので決まらない() -> None:
    assert budget_line_quantity([2, 3], 60, 30) == 0
    with pytest.raises(ValueError):
        budget_line_quantity([2, 3], 60, 30.5)
    with pytest.raises(ValueError):
        budget_line_quantity([2, 3], 60, -1)


def test_予算線上の数量は2財のときだけ() -> None:
    with pytest.raises(ValueError):
        budget_line_quantity([1, 2, 5], 30, 4)


def test_24時間で賃金10なら消費と余暇の予算は240() -> None:
    assert full_income(10, 24) == 240
    assert full_income(8, 24, 40) == 232


def test_余暇16時間なら8時間働いて消費は80() -> None:
    assert consumption_given_leisure(16, 10, 24) == 80
    assert consumption_given_leisure(24, 10, 24, 50) == 50
    assert consumption_given_leisure(0, 8, 24, 40) == 232


def test_消費と余暇は価格1と賃金の予算線上にある() -> None:
    # 余暇の価格は賃金（1 時間休むと、賃金を 1 時間分あきらめる）
    for leisure, wage, nonlabor in [(16, 10, 0), (10, 12.5, 30), (20.5, 8, 40)]:
        c = consumption_given_leisure(leisure, wage, 24, nonlabor)
        assert budget_expenditure([1, wage], [c, leisure]) == pytest.approx(
            full_income(wage, 24, nonlabor)
        )


def test_2期間の予算で今期100のうち60を消費すると来期は利子付きで() -> None:
    assert second_period_consumption(60, 100, 0, 0.05) == pytest.approx(42)
    assert second_period_consumption(60, 100, 50, 0.1) == pytest.approx(94)


def test_今期に借りると来期の消費は利子の分だけ減る() -> None:
    assert second_period_consumption(120, 100, 50, 0.1) == pytest.approx(28)


def test_生涯所得の現在価値は来期の所得を割り引いて足す() -> None:
    assert lifetime_income_present_value(100, 110, 0.1) == pytest.approx(200)
    assert lifetime_income_present_value(100, 0, 0.05) == 100


def test_2期間の消費は価格1と1割る1プラスrの予算線上にある() -> None:
    for c1, y1, y2, rate in [(60, 100, 50, 0.1), (120, 100, 50, 0.1), (30, 80, 20, 0)]:
        c2 = second_period_consumption(c1, y1, y2, rate)
        assert budget_expenditure([1, 1 / (1 + rate)], [c1, c2]) == pytest.approx(
            lifetime_income_present_value(y1, y2, rate)
        )


def test_余暇は0時間以上で総時間以下() -> None:
    assert consumption_given_leisure(24, 10, 24) == 0
    with pytest.raises(ValueError):
        consumption_given_leisure(-1, 10, 24)
    with pytest.raises(ValueError):
        consumption_given_leisure(24.5, 10, 24)


def test_利子率がマイナス100パーセント以下なら2期間の予算は決まらない() -> None:
    with pytest.raises(ValueError):
        second_period_consumption(60, 100, 0, -1)
    with pytest.raises(ValueError):
        lifetime_income_present_value(100, 50, -1.5)
    assert second_period_consumption(60, 100, 0, -0.5) == pytest.approx(20)


def test_来期に返せないほど借りると来期の消費は決まらない() -> None:
    # 40 借りると、来期に 40 × 1.25 = 50 返す。来期の所得 50 で、ちょうど返し切る
    assert second_period_consumption(140, 100, 50, 0.25) == 0
    with pytest.raises(ValueError):
        second_period_consumption(141, 100, 50, 0.25)


def test_ペイオフ10と20で状態価格0点4と0点5の証券の価格は14() -> None:
    assert security_price([10, 20], [0.4, 0.5]) == pytest.approx(14)


def test_どの状態でも1を払う安全な証券の価格から利子率がわかる() -> None:
    price = security_price([1, 1, 1], [0.3, 0.45, 0.2])
    assert price == pytest.approx(0.95)
    assert 1 / price - 1 == pytest.approx(0.05263, abs=1e-5)


def test_負の状態価格では証券の価格は決まらない() -> None:
    with pytest.raises(ValueError):
        security_price([10, 20], [0.4, -0.1])
    assert security_price([10, 20], [0, 0.5]) == 10
