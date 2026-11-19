"""第 15 章: IS-MP-PC モデルのテスト。

フィッシャー方程式  r(t) = i(t) - E π(t+1)、適応的期待 E π(t+1) = π(t)
IS 曲線   y(t) = y* - a·(r(t) - r*) + u(t)
MP 曲線   i(t) = r* + π(t) + c·(π(t) - π*) + d·(y(t) - y*) + v(t)
PC 曲線   π(t) = π(t-1) + b·(y(t) - y*) + e(t)
"""

import numpy as np
import pytest

from lib.chapter15.ismppc import (
    IsMpPcParameters,
    eigenvalues,
    impulse_response,
    is_stable,
    ismppc_matrices,
    policy_rate,
    simulate_without_shocks,
    step,
)

DEFAULT = IsMpPcParameters()
CASE_2 = IsMpPcParameters(c=0.5, d=1.5)
SIMPLE = IsMpPcParameters(c=0, d=0)
STEADY = [2.0, 100.0, 4.0, 2.0]


@pytest.mark.parametrize(
    ("a", "b", "c", "d"),
    [(0, 0.25, 1.5, 0.5), (1, 0, 1.5, 0.5), (1, 0.25, -0.1, 0.5), (1, 0.25, 1.5, -0.1)],
)
def test_パラメーターの符号が合わなければ受け付けない(
    a: float, b: float, c: float, d: float
) -> None:
    with pytest.raises(ValueError, match="パラメーター"):
        IsMpPcParameters(a=a, b=b, c=c, d=d)


def test_cとdが0でもパラメーターとして受け付ける() -> None:
    assert IsMpPcParameters(c=0, d=0).c == 0
    assert IsMpPcParameters(c=1.5, d=0).d == 0


def test_行列は手計算の値と一致する() -> None:
    a_matrix, b_matrix = ismppc_matrices(DEFAULT)
    assert a_matrix == pytest.approx(np.array([[1.5, 1.5], [-0.25, 1.0]]))
    assert b_matrix == pytest.approx(np.array([[0.0, 0.0], [0.0, 1.0]]))


def test_固有値は0とφ() -> None:
    assert eigenvalues(DEFAULT) == pytest.approx([0.0, 0.8])
    assert DEFAULT.phi == pytest.approx(1.5 / 1.875)


def test_インフレ率に反応する中央銀行のもとでは安定() -> None:
    assert is_stable(DEFAULT)
    assert is_stable(CASE_2)


def test_インフレ率に反応しなければ安定ではない() -> None:
    assert not is_stable(SIMPLE)
    assert eigenvalues(SIMPLE) == pytest.approx([0.0, 1.0])
    assert SIMPLE.phi == pytest.approx(1.0)


def test_cがあればテイラー原則で名目利子率はインフレ率より大きく動く() -> None:
    low = policy_rate(DEFAULT, y=100, pi=2.0)
    high = policy_rate(DEFAULT, y=100, pi=3.0)
    assert high - low == pytest.approx(1 + DEFAULT.c)


def test_名目利子率は自然利子率とインフレ率と政策ルールの和() -> None:
    assert policy_rate(DEFAULT, y=100, pi=2.0) == pytest.approx(4.0)
    assert policy_rate(DEFAULT, y=99, pi=3.0, v=0.5) == pytest.approx(
        2 + 3 + 1.5 * 1.0 + 0.5 * (-1) + 0.5
    )


def test_ショックがなければ定常状態にとどまる() -> None:
    assert step(DEFAULT, 100.0, 2.0, 0, 0, 0) == pytest.approx((100.0, 2.0))


def test_単純なケースでは初期のインフレ率が持続する() -> None:
    y, pi = step(SIMPLE, 100.0, 3.0, 0, 0, 0)
    assert y == pytest.approx(100.0)
    assert pi == pytest.approx(3.0)


def test_フィリップス曲線のショックは手計算の値() -> None:
    y, pi = step(DEFAULT, 100.0, 2.0, 0, 0, 1.0)
    assert pi == pytest.approx(2.8)
    assert y == pytest.approx(99.2)


def test_IS曲線のショックは手計算の値() -> None:
    y, pi = step(DEFAULT, 100.0, 2.0, 1.0, 0, 0)
    assert y - 100 == pytest.approx(1 / 1.875)
    assert pi - 2 == pytest.approx(0.25 / 1.875)


def test_MP曲線のショックは手計算の値() -> None:
    y, pi = step(DEFAULT, 100.0, 2.0, 0, 1.0, 0)
    assert y - 100 == pytest.approx(-1 / 1.875)
    assert pi - 2 == pytest.approx(-0.25 / 1.875)


@pytest.mark.parametrize(
    ("pi_prev", "u", "v", "e"),
    [(2.0, 1.0, 0.0, 0.0), (3.1, -0.4, 0.7, 0.2), (1.2, 0.3, -0.5, -0.8)],
)
def test_均衡はIS曲線とフィリップス曲線を同時に満たす(
    pi_prev: float, u: float, v: float, e: float
) -> None:
    params = DEFAULT
    y, pi = step(params, 100.0, pi_prev, u, v, e)
    r = policy_rate(params, y, pi, v) - pi
    assert y == pytest.approx(params.y_star - params.a * (r - params.r_star) + u)
    assert pi == pytest.approx(pi_prev + params.b * (y - params.y_star) + e)


def test_インフレ率の差分方程式の係数はφ() -> None:
    _, pi1 = step(DEFAULT, 100.0, 3.0, 0, 0, 0)
    assert pi1 - 2 == pytest.approx(DEFAULT.phi * (3.0 - 2))


def test_インパルス反応の列と長さ() -> None:
    df = impulse_response(DEFAULT, shock_pc=1.0)
    assert list(df.columns) == ["pi", "y", "i", "r"]
    assert len(df) == 3 + 1 + 20


def test_ショック前の3期間は定常状態() -> None:
    df = impulse_response(DEFAULT, shock_pc=1.0)
    assert df.iloc[:3]["pi"].tolist() == [2.0, 2.0, 2.0]
    assert df.iloc[:3]["y"].tolist() == [100.0, 100.0, 100.0]
    assert df.iloc[:3]["i"].tolist() == [4.0, 4.0, 4.0]
    assert df.iloc[:3]["r"].tolist() == [2.0, 2.0, 2.0]


def test_インフレ率の乖離は毎期φ倍になって0に戻る() -> None:
    df = impulse_response(DEFAULT, shock_pc=1.0, periods_after=40)
    gap = df["pi"] - 2
    assert gap.iloc[3] == pytest.approx(0.8)
    assert gap.iloc[4] == pytest.approx(0.64)
    assert gap.iloc[5] == pytest.approx(0.512)
    assert abs(gap.iloc[-1]) < 1e-3


def test_ショックの翌期から産出量の乖離もφ倍で縮む() -> None:
    df = impulse_response(DEFAULT, shock_pc=1.0)
    assert df["y"].iloc[3] - 100 == pytest.approx(-0.8)
    assert df["y"].iloc[4] - 100 == pytest.approx(-0.64)


def test_単純なケースではインフレ率の変化が持続する() -> None:
    df = impulse_response(SIMPLE, shock_pc=1.0)
    assert df["pi"].iloc[3:].tolist() == pytest.approx([3.0] * 21)
    assert df["y"].tolist() == pytest.approx([100.0] * 24)


def test_ショックは比例する() -> None:
    one = impulse_response(DEFAULT, shock_is=1.0) - STEADY
    two = impulse_response(DEFAULT, shock_is=2.0) - STEADY
    assert two.to_numpy() == pytest.approx(2 * one.to_numpy())


def test_ショックは足し合わせられる() -> None:
    is_only = impulse_response(DEFAULT, shock_is=1.0) - STEADY
    pc_only = impulse_response(DEFAULT, shock_pc=1.0) - STEADY
    both = impulse_response(DEFAULT, shock_is=1.0, shock_pc=1.0) - STEADY
    assert both.to_numpy() == pytest.approx((is_only + pc_only).to_numpy())


def test_金融引き締めのショックは産出量とインフレ率を下げる() -> None:
    df = impulse_response(DEFAULT, shock_mp=1.0)
    assert df["y"].iloc[3] < 100
    assert df["pi"].iloc[3] < 2


def test_ショックのない移行過程は定常状態に向かう() -> None:
    df = simulate_without_shocks(DEFAULT, pi0=3.0, y0=99.0, n=60)
    assert len(df) == 61
    assert df["pi"].iloc[0] == 3.0
    assert df["pi"].iloc[-1] == pytest.approx(2.0, abs=1e-3)
    assert df["y"].iloc[-1] == pytest.approx(100.0, abs=1e-3)
    assert df["r"].iloc[-1] == pytest.approx(2.0, abs=1e-3)


def test_移行過程の最初の期は初期値とMP曲線から決まる() -> None:
    df = simulate_without_shocks(DEFAULT, pi0=3.0, y0=99.0, n=2)
    assert df["y"].iloc[0] == 99.0
    assert df["i"].iloc[0] == pytest.approx(2 + 3 + 1.5 * 1 + 0.5 * (-1))
    assert df["r"].iloc[0] == pytest.approx(df["i"].iloc[0] - 3.0)


def test_初期の産出量は移行に影響しない() -> None:
    low = simulate_without_shocks(DEFAULT, pi0=3.0, y0=90.0, n=5)
    high = simulate_without_shocks(DEFAULT, pi0=3.0, y0=110.0, n=5)
    assert low["pi"].iloc[1:].tolist() == pytest.approx(high["pi"].iloc[1:].tolist())
    assert low["y"].iloc[1:].tolist() == pytest.approx(high["y"].iloc[1:].tolist())


def test_産出量を重視する政策では物価の乖離は大きく長く続く() -> None:
    case1 = impulse_response(DEFAULT, shock_pc=1.0)
    case2 = impulse_response(CASE_2, shock_pc=1.0)
    assert case2["pi"].iloc[3] - 2 == pytest.approx(1 / 1.05)
    assert case2["y"].iloc[3] - 100 == pytest.approx(-0.2 / 1.05)
    assert abs(case2["y"].iloc[3] - 100) < abs(case1["y"].iloc[3] - 100)
    assert case2["pi"].iloc[3] > case1["pi"].iloc[3]
    assert CASE_2.phi > DEFAULT.phi
    assert case2["pi"].iloc[10] > case1["pi"].iloc[10]


def test_ショック前の期間の数を変えられる() -> None:
    df = impulse_response(DEFAULT, shock_pc=1.0, periods_after=5, periods_before=6)
    assert len(df) == 6 + 1 + 5
    assert df.iloc[:6]["pi"].tolist() == [2.0] * 6
    assert df["pi"].iloc[6] == pytest.approx(2.8)
