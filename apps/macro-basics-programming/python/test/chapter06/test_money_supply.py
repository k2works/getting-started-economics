"""第 6 章: 貨幣供給と貨幣乗数のテスト。"""

import pytest

from lib.chapter06.money_supply import (
    broad_liquidity,
    credit_creation_path,
    m1,
    m3,
    monetary_base,
    money_multiplier,
    money_stock,
    open_market_operation,
    reserve_requirement_change,
)

CASH_RATIO = 0.1  # 現金預金比率 C/D
RESERVE_RATIO = 0.01  # 準備預金比率 R/D
BASE = 110.0  # ハイパワードマネー（現金 100 + 準備預金 10）


def test_M1は現金通貨と預金通貨の和() -> None:
    assert m1(80, 520) == 600


def test_M3はM1に準通貨とCDを足した値() -> None:
    assert m3(600, 300, 20) == 920


def test_広義流動性はM3に投資信託と国債などを足した値() -> None:
    assert broad_liquidity(920, 60, 40) == 1020


def test_範囲が広いほど大きい() -> None:
    first = m1(80, 520)
    second = m3(first, 300, 20)
    third = broad_liquidity(second, 60, 40)
    assert first < second < third


def test_ストックの要素が負ならエラー() -> None:
    with pytest.raises(ValueError, match="現金通貨"):
        m1(-1, 520)
    with pytest.raises(ValueError, match="準通貨"):
        m3(600, -1, 20)
    with pytest.raises(ValueError, match="投資信託"):
        broad_liquidity(920, -1, 40)


def test_ハイパワードマネーは現金通貨と準備預金の和() -> None:
    assert monetary_base(100, 10) == 110


def test_貨幣乗数は現金預金比率0_1と準備率0_01で10() -> None:
    assert money_multiplier(CASH_RATIO, RESERVE_RATIO) == pytest.approx(10)


def test_現金預金比率が上がると貨幣乗数は下がる() -> None:
    assert money_multiplier(0.2, RESERVE_RATIO) == pytest.approx(1.2 / 0.21)
    assert money_multiplier(0.2, RESERVE_RATIO) < money_multiplier(0.1, RESERVE_RATIO)


def test_準備率が上がると貨幣乗数は下がる() -> None:
    assert money_multiplier(CASH_RATIO, 0.02) < money_multiplier(
        CASH_RATIO, RESERVE_RATIO
    )


def test_現金を持たず全額を準備に置くなら貨幣乗数は1() -> None:
    assert money_multiplier(0.0, 1.0) == pytest.approx(1)


def test_貨幣乗数は常に1以上() -> None:
    for cash_ratio in (0.0, 0.1, 1.0, 10.0):
        for reserve_ratio in (0.01, 0.5, 1.0):
            assert money_multiplier(cash_ratio, reserve_ratio) >= 1


def test_比率が範囲外ならエラー() -> None:
    with pytest.raises(ValueError, match="現金預金比率"):
        money_multiplier(-0.1, RESERVE_RATIO)
    with pytest.raises(ValueError, match="準備預金比率"):
        money_multiplier(CASH_RATIO, 0.0)
    with pytest.raises(ValueError, match="準備預金比率"):
        money_multiplier(CASH_RATIO, -0.01)
    with pytest.raises(ValueError, match="準備預金比率"):
        money_multiplier(CASH_RATIO, 1.01)


def test_マネーストックは貨幣乗数にハイパワードマネーを掛けた値() -> None:
    assert money_stock(CASH_RATIO, RESERVE_RATIO, BASE) == pytest.approx(1100)


def test_マネーストックは現金と預金の和に一致する() -> None:
    deposits = BASE / (CASH_RATIO + RESERVE_RATIO)
    cash = CASH_RATIO * deposits
    assert cash + deposits == pytest.approx(
        money_stock(CASH_RATIO, RESERVE_RATIO, BASE)
    )
    assert cash + RESERVE_RATIO * deposits == pytest.approx(BASE)


def test_ハイパワードマネーが負ならエラー() -> None:
    with pytest.raises(ValueError, match="ハイパワードマネー"):
        money_stock(CASH_RATIO, RESERVE_RATIO, -1)


def test_買いオペはハイパワードマネーを増やす() -> None:
    assert open_market_operation(BASE, 22, "買いオペ") == pytest.approx(132)


def test_売りオペはハイパワードマネーを減らす() -> None:
    assert open_market_operation(BASE, 11, "売りオペ") == pytest.approx(99)


def test_買いオペ後のマネーストックの増加は貨幣乗数の倍() -> None:
    before = money_stock(CASH_RATIO, RESERVE_RATIO, BASE)
    after = money_stock(
        CASH_RATIO, RESERVE_RATIO, open_market_operation(BASE, 22, "買いオペ")
    )
    assert after - before == pytest.approx(10 * 22)


def test_売りオペの額がハイパワードマネーを超えるとエラー() -> None:
    assert open_market_operation(BASE, BASE, "売りオペ") == 0
    with pytest.raises(ValueError, match="超えて"):
        open_market_operation(BASE, BASE + 1, "売りオペ")


def test_公開市場操作の入力が不正ならエラー() -> None:
    with pytest.raises(ValueError, match="買いオペ"):
        open_market_operation(BASE, 10, "貸出")
    with pytest.raises(ValueError, match="額"):
        open_market_operation(BASE, -10, "買いオペ")


def test_準備率を上げるとマネーストックは減る() -> None:
    after = reserve_requirement_change(BASE, CASH_RATIO, 0.02)
    assert after == pytest.approx(BASE * 1.1 / 0.12)
    assert after < money_stock(CASH_RATIO, RESERVE_RATIO, BASE)


def test_準備率を下げるとマネーストックは増える() -> None:
    after = reserve_requirement_change(BASE, CASH_RATIO, 0.005)
    assert after > money_stock(CASH_RATIO, RESERVE_RATIO, BASE)


def test_信用創造の1回目はハイパワードマネーと同じ額() -> None:
    assert credit_creation_path(BASE, CASH_RATIO, RESERVE_RATIO, 1) == pytest.approx(
        [110]
    )


def test_信用創造の2回目までの合計() -> None:
    path = credit_creation_path(BASE, CASH_RATIO, RESERVE_RATIO, 2)
    assert path == pytest.approx([110, 209])


def test_信用創造は現金を持たなければ預金が準備率の逆数倍になる() -> None:
    path = credit_creation_path(100, 0.0, 0.1, 200)
    assert path[0] == pytest.approx(100)
    assert path[1] == pytest.approx(190)
    assert path[-1] == pytest.approx(1000)


def test_信用創造は貨幣乗数とハイパワードマネーの積に近づく() -> None:
    path = credit_creation_path(BASE, CASH_RATIO, RESERVE_RATIO, 200)
    assert path[-1] == pytest.approx(money_stock(CASH_RATIO, RESERVE_RATIO, BASE))
    assert path == sorted(path)
    assert all(a < 1100 for a in path)


def test_信用創造のラウンド数が1未満ならエラー() -> None:
    with pytest.raises(ValueError, match="ラウンド"):
        credit_creation_path(BASE, CASH_RATIO, RESERVE_RATIO, 0)


def test_ストックが0でも有効() -> None:
    assert m1(0, 0) == 0
    assert monetary_base(0, 0) == 0
    assert money_stock(CASH_RATIO, RESERVE_RATIO, 0) == 0


def test_信用創造の比率が範囲外ならエラー() -> None:
    with pytest.raises(ValueError, match="現金預金比率"):
        credit_creation_path(BASE, -0.1, RESERVE_RATIO, 3)
    with pytest.raises(ValueError, match="準備預金比率"):
        credit_creation_path(BASE, CASH_RATIO, 0.0, 3)
