"""第 14 章: インパルス反応と確率的シミュレーションのテスト。"""

import numpy as np
import pandas as pd
import pytest

from lib.chapter13.adas import AdasParameters, data_features, model_moments
from lib.chapter14.simulation import (
    convergence_path,
    impulse_response,
    is_stable,
    price_half_life,
    simulate,
    variance_contributions,
    variance_decomposition,
)

TRUE = AdasParameters(a=0.8, c=0.3, sigma_u=1.5, sigma_v=1.2)
UNIT = AdasParameters(a=1, c=1, sigma_u=1, sigma_v=1)


@pytest.mark.parametrize(
    ("h", "stable"), [(0.8, True), (-0.5, True), (1.0, False), (-1.2, False)]
)
def test_遷移係数の絶対値が1より小さければ安定(h: float, stable: bool) -> None:
    assert is_stable(h) is stable


def test_aとcが正ならモデルは必ず安定() -> None:
    assert is_stable(TRUE.h)
    assert is_stable(AdasParameters(a=100, c=100, sigma_u=1, sigma_v=1).h)


def test_ショックがなければ物価はhずつ縮み産出量はAD曲線の上にある() -> None:
    path = convergence_path(1.0, TRUE, periods=5)
    assert len(path) == 6
    assert path["p"].iloc[0] == 1.0
    assert path["p"].iloc[1] == pytest.approx(TRUE.h)
    assert path["p"].iloc[5] == pytest.approx(TRUE.h**5)
    assert path["y"].to_numpy() == pytest.approx((-TRUE.c * path["p"]).to_numpy())


def test_初期値が負でも0に近づく() -> None:
    path = convergence_path(-1.0, TRUE, periods=30)
    assert path["p"].iloc[-1] == pytest.approx(0, abs=1e-2)
    assert (path["p"] < 0).all()


def test_変化率はhマイナス1でaが大きいほど速く収束する() -> None:
    slow = AdasParameters(a=0.2, c=0.3, sigma_u=1, sigma_v=1)
    fast = AdasParameters(a=2.0, c=0.3, sigma_u=1, sigma_v=1)
    assert fast.h < slow.h
    path = convergence_path(1.0, fast, periods=1)
    assert path["p"].iloc[1] / path["p"].iloc[0] - 1 == pytest.approx(fast.h - 1)


def test_半減期は物価の持続性から決まる() -> None:
    assert price_half_life(TRUE) == pytest.approx(np.log(0.5) / np.log(TRUE.h))
    assert TRUE.h ** price_half_life(TRUE) == pytest.approx(0.5)


def test_インパルス反応は最初の3期間が定常状態() -> None:
    df = impulse_response(TRUE, u=1.0)
    assert df.iloc[:3].to_numpy() == pytest.approx(0)


def test_インパルス反応の列と長さ() -> None:
    df = impulse_response(TRUE, u=1.0, periods_after=20)
    assert list(df.columns) == ["y", "p", "u", "v"]
    assert len(df) == 3 + 1 + 20


def test_需要ショックの反応は手計算と一致する() -> None:
    df = impulse_response(UNIT, u=1.0, periods_after=2)
    assert df["u"].tolist() == [0, 0, 0, 1.0, 0, 0]
    assert df["p"].iloc[3] == pytest.approx(0.5)
    assert df["y"].iloc[3] == pytest.approx(0.5)
    assert df["p"].iloc[4] == pytest.approx(0.25)
    assert df["y"].iloc[4] == pytest.approx(-0.25)
    assert df["p"].iloc[5] == pytest.approx(0.125)


def test_供給ショックは物価を上げて産出量を下げ長期には戻る() -> None:
    df = impulse_response(UNIT, v=1.0, periods_after=40)
    assert df["v"].iloc[3] == 1.0
    assert df["p"].iloc[3] > 0
    assert df["y"].iloc[3] < 0
    assert abs(df["p"].iloc[-1]) < 1e-9
    assert abs(df["y"].iloc[-1]) < 1e-9


def test_ショックが小さければ反応も比例して小さい() -> None:
    one = impulse_response(TRUE, u=1.0)
    two = impulse_response(TRUE, u=2.0)
    assert two[["y", "p"]].to_numpy() == pytest.approx(2 * one[["y", "p"]].to_numpy())


def test_需要と供給のショックの反応は足し合わせられる() -> None:
    u_only = impulse_response(TRUE, u=1.0)
    v_only = impulse_response(TRUE, v=1.0)
    both = impulse_response(TRUE, u=1.0, v=1.0)
    assert both[["y", "p"]].to_numpy() == pytest.approx(
        (u_only[["y", "p"]] + v_only[["y", "p"]]).to_numpy()
    )


def test_シミュレーションは種が同じなら同じ結果() -> None:
    first = simulate(TRUE, 50, np.random.default_rng(3))
    second = simulate(TRUE, 50, np.random.default_rng(3))
    pd.testing.assert_frame_equal(first, second)


def test_シミュレーションの列と長さ() -> None:
    df = simulate(TRUE, 50, np.random.default_rng(0))
    assert list(df.columns) == ["y", "p", "u", "v"]
    assert len(df) == 50


def test_シミュレーションの各期はAS曲線とAD曲線を満たす() -> None:
    df = simulate(TRUE, 50, np.random.default_rng(0))
    p_prev = df["p"].shift(fill_value=0.0)
    assert df["p"].to_numpy() == pytest.approx(
        (p_prev + TRUE.a * df["y"] + df["v"]).to_numpy()
    )
    assert df["y"].to_numpy() == pytest.approx((-TRUE.c * df["p"] + df["u"]).to_numpy())


def test_最初の期は定常状態から始まる() -> None:
    df = simulate(TRUE, 10, np.random.default_rng(0))
    assert df["p"].iloc[0] == pytest.approx(
        TRUE.h * (TRUE.a * df["u"].iloc[0] + df["v"].iloc[0])
    )


def test_ショックの標準偏差はパラメーターに近い() -> None:
    df = simulate(TRUE, 100000, np.random.default_rng(2))
    assert df["u"].std() == pytest.approx(1.5, abs=0.02)
    assert df["v"].std() == pytest.approx(1.2, abs=0.02)


def test_長いシミュレーションの特徴は理論の積率に近づく() -> None:
    df = simulate(TRUE, 200000, np.random.default_rng(5))
    simulated = data_features(df["y"], df["p"])
    theory = model_moments(TRUE)
    for key, value in theory.items():
        assert simulated[key] == pytest.approx(value, abs=0.02)


def test_シミュレーションの長さは1以上() -> None:
    with pytest.raises(ValueError, match="1 以上"):
        simulate(TRUE, 0, np.random.default_rng(0))


def test_分散分解の割合は列ごとに合計1() -> None:
    shares = variance_decomposition(TRUE)
    assert list(shares.index) == ["demand", "supply"]
    assert list(shares.columns) == ["p", "y"]
    assert shares.sum().to_numpy() == pytest.approx(1.0)


def test_物価の分散分解は需要ショックの寄与度の式と一致する() -> None:
    shares = variance_decomposition(TRUE)
    a2su2 = TRUE.a**2 * TRUE.sigma_u**2
    assert shares["p"]["demand"] == pytest.approx(a2su2 / (a2su2 + TRUE.sigma_v**2))


def test_手計算の例で産出量の分散分解の割合を確かめる() -> None:
    params = AdasParameters(a=2, c=1, sigma_u=1, sigma_v=1)
    shares = variance_decomposition(params)
    assert shares["p"]["demand"] == pytest.approx(0.8)
    assert shares["y"]["demand"] == pytest.approx(4 / 7)
    assert shares["y"]["supply"] == pytest.approx(3 / 7)


def test_需要ショックだけなら寄与度は需要が1() -> None:
    params = AdasParameters(a=0.8, c=0.3, sigma_u=1.5, sigma_v=0)
    shares = variance_decomposition(params)
    assert shares["p"]["demand"] == pytest.approx(1.0)
    assert shares["y"]["demand"] == pytest.approx(1.0)


def test_寄与の合計は理論の分散に等しい() -> None:
    contributions = variance_contributions(TRUE)
    moments = model_moments(TRUE)
    assert contributions["p"].sum() == pytest.approx(moments["p_std"] ** 2)
    assert contributions["y"].sum() == pytest.approx(moments["y_std"] ** 2)


def test_ショックを片方だけにしたシミュレーションの分散は寄与に近い() -> None:
    contributions = variance_contributions(TRUE)
    only_u = AdasParameters(a=TRUE.a, c=TRUE.c, sigma_u=TRUE.sigma_u, sigma_v=0)
    df = simulate(only_u, 200000, np.random.default_rng(8))
    assert df["p"].var() == pytest.approx(contributions["p"]["demand"], rel=0.03)
    assert df["y"].var() == pytest.approx(contributions["y"]["demand"], rel=0.03)


def test_インパルス反応の既定の長さはショック前3期とショック1期とショック後20期() -> (
    None
):
    assert len(impulse_response(TRUE, u=1.0)) == 24
