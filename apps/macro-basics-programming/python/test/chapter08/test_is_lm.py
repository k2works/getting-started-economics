"""第 8 章: IS 曲線と IS-LM の均衡のテスト。"""

import pytest

from lib.chapter04.multiplier import equilibrium_income
from lib.chapter07.money_market import lm_interest
from lib.chapter08.is_lm import (
    goods_market_state,
    investment_demand,
    is_income,
    is_intercept,
    is_interest,
    is_lm_residuals,
    is_shift_for_government,
    is_slope,
    solve_is_lm,
)

# c = 0.6、b = 20、C0 = 100、T = 0、I0 = 300、G = 50 なので、切片 A = 450
MPC = 0.6
B = 20
A = 450
# LM: k = 0.5、h = 100、M/P = 250
K = 0.5
H = 100
M = 250


def test_投資は利子率の減少関数() -> None:
    assert investment_demand(0, 300, B) == 300
    assert investment_demand(2.5, 300, B) == 250
    assert investment_demand(5, 300, B) < investment_demand(2.5, 300, B)


def test_投資の利子感応度が負ならエラー() -> None:
    with pytest.raises(ValueError, match="利子感応度"):
        investment_demand(2.5, 300, -1)


def test_ISの切片は独立支出の合計() -> None:
    assert is_intercept(MPC, 100, 300, 50) == 450


def test_課税は切片を租税乗数の分子の分だけ下げる() -> None:
    assert is_intercept(MPC, 100, 300, 50, tax=100) == pytest.approx(450 - 60)


def test_IS曲線上の所得() -> None:
    assert is_income(2.5, A, MPC, B) == pytest.approx(1000)
    assert is_income(0, A, MPC, B) == pytest.approx(1125)


def test_IS曲線上の利子率() -> None:
    assert is_interest(1000, A, MPC, B) == pytest.approx(2.5)
    assert is_interest(0, A, MPC, B) == pytest.approx(22.5)


def test_所得と利子率は逆関数の関係() -> None:
    for r in (0, 1, 2.5, 10):
        y = is_income(r, A, MPC, B)
        assert is_interest(y, A, MPC, B) == pytest.approx(r)


def test_IS曲線は第4章の45度線の均衡所得と一致する() -> None:
    for r in (0, 2.5, 5):
        investment = investment_demand(r, 300, B)
        y45 = equilibrium_income(MPC, 100, investment, 50, 0)
        assert is_income(r, A, MPC, B) == pytest.approx(y45)


def test_IS曲線は右下がり() -> None:
    assert is_slope(MPC, B) == pytest.approx(-0.02)
    assert is_income(5, A, MPC, B) < is_income(2.5, A, MPC, B)


def test_投資の利子感応度が大きいほど緩やか() -> None:
    assert abs(is_slope(MPC, 40)) < abs(is_slope(MPC, 20))
    assert is_slope(MPC, 40) == pytest.approx(-0.01)


def test_限界消費性向が大きいほど緩やか() -> None:
    assert abs(is_slope(0.8, B)) < abs(is_slope(0.6, B))
    assert is_slope(0.8, B) == pytest.approx(-0.01)


def test_政府支出が増えるとISは右へ動く() -> None:
    assert is_shift_for_government(MPC, 10) == pytest.approx(25)
    shifted = is_income(2.5, A + 10, MPC, B)
    assert shifted - is_income(2.5, A, MPC, B) == pytest.approx(25)


def test_政府支出が減ると左へ動く() -> None:
    assert is_shift_for_government(MPC, -10) == pytest.approx(-25)


def test_限界消費性向が1ならエラー() -> None:
    with pytest.raises(ValueError, match="限界消費性向"):
        is_income(2.5, A, 1, B)
    with pytest.raises(ValueError, match="限界消費性向"):
        is_shift_for_government(1, 10)


def test_利子感応度が0のISは垂直で利子率を求められない() -> None:
    assert is_income(2.5, A, MPC, 0) == pytest.approx(1125)
    with pytest.raises(ValueError, match="垂直"):
        is_interest(1000, A, MPC, 0)
    with pytest.raises(ValueError, match="垂直"):
        is_slope(MPC, 0)


def test_ISの下の点は財の需要超過で上の点は供給超過() -> None:
    assert goods_market_state(1000, 2.5, A, MPC, B) == "均衡"
    assert goods_market_state(1100, 2.5, A, MPC, B) == "供給超過"
    assert goods_market_state(900, 2.5, A, MPC, B) == "需要超過"
    assert goods_market_state(1000, 5, A, MPC, B) == "供給超過"
    assert goods_market_state(1000, 0, A, MPC, B) == "需要超過"


def test_IS_LMの均衡は所得1000で利子率2_5() -> None:
    y, r = solve_is_lm(MPC, B, A, K, H, M)
    assert y == pytest.approx(1000)
    assert r == pytest.approx(2.5)


def test_均衡はISとLMの両方の式を満たす() -> None:
    y, r = solve_is_lm(MPC, B, A, K, H, M)
    is_residual, lm_residual = is_lm_residuals(y, r, MPC, B, A, K, H, M)
    assert is_residual == pytest.approx(0, abs=1e-9)
    assert lm_residual == pytest.approx(0, abs=1e-9)


def test_均衡でない点は残差が0でない() -> None:
    is_residual, lm_residual = is_lm_residuals(1000, 5, MPC, B, A, K, H, M)
    assert is_residual == pytest.approx(0.4 * 1000 + 20 * 5 - 450)
    assert lm_residual == pytest.approx(0.5 * 1000 - 100 * 5 - 250)


def test_均衡の利子率はLM曲線の式とも一致する() -> None:
    y, r = solve_is_lm(MPC, B, A, K, H, M)
    assert r == pytest.approx(lm_interest(y, M, K, H))


def test_政府支出が増えると所得も利子率も上がる() -> None:
    y0, r0 = solve_is_lm(MPC, B, A, K, H, M)
    y1, r1 = solve_is_lm(MPC, B, A + 10, K, H, M)
    assert y1 > y0
    assert r1 > r0


def test_実質貨幣供給が増えると所得は上がり利子率は下がる() -> None:
    y0, r0 = solve_is_lm(MPC, B, A, K, H, M)
    y1, r1 = solve_is_lm(MPC, B, A, K, H, M + 10)
    assert y1 > y0
    assert r1 < r0


def test_ソルバーは有限の値だけ() -> None:
    with pytest.raises(ValueError, match="有限"):
        solve_is_lm(MPC, B, A, K, float("inf"), M)


def test_ソルバーはkとhが正でなければエラー() -> None:
    with pytest.raises(ValueError, match="k と h"):
        solve_is_lm(MPC, B, A, 0, H, M)
    with pytest.raises(ValueError, match="k と h"):
        solve_is_lm(MPC, B, A, K, 0, M)
