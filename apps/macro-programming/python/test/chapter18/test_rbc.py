"""第 18 章: 実物的景気循環（RBC）モデルのテスト。

効用  u = (C^(1-θ) - 1) ÷ (1-θ) + m·ln(1 - L)（基本モデルは L 一定）
オイラー条件  C(t)^(-θ) = β·E[(1 + R(t+1))·C(t+1)^(-θ)]
労働供給  C(t)^(-θ) = m ÷ ((1 - L(t))·W(t))（内生的労働供給のとき）
生産関数  Y = A·K^α·L^(1-α)、資本  K' = I + (1-δ)·K、Y = C + I
利子率  R = α·Y/K - δ、賃金  W = (1-α)·Y/L、TFP  A' = A^ρ·e^v
"""

import numpy as np
import pytest

from lib.chapter08.stochastic import white_noise
from lib.chapter09.cycles import cycle
from lib.chapter18.rbc import (
    RbcParameters,
    calibrate_leisure_weight,
    equilibrium_equations,
    euler_residual,
    impulse_response,
    simulate_with_shocks,
    solve_rbc,
    steady_state,
    stochastic_simulation,
)

BASIC = RbcParameters()
THIRD = RbcParameters(alpha=1 / 3)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"alpha": 0.0},
        {"beta": 1.0},
        {"delta": 0.0},
        {"rho": 1.0},
        {"sigma": -0.1},
        {"theta": 0.0},
        {"hours": 0.0},
        {"leisure_weight": 0.0},
    ],
)
def test_パラメーターの範囲が合わなければ受け付けない(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError, match="パラメーター"):
        RbcParameters(**kwargs)


def test_実質利子率はβの逆数マイナス1() -> None:
    ss = steady_state(THIRD)
    assert ss["r"] == pytest.approx(1 / 0.99 - 1)
    assert ss["r"] == pytest.approx(0.0101, abs=0.0001)


def test_資本産出比率はαを実質利子率と減耗率の和で割った値() -> None:
    ss = steady_state(THIRD)
    assert ss["k"] / ss["y"] == pytest.approx((1 / 3) / (ss["r"] + 0.025))
    assert ss["k"] / ss["y"] == pytest.approx(9.5, abs=0.01)


def test_定常状態の資本は投資と減耗が等しく消費は産出から投資を引いた値() -> None:
    ss = steady_state(BASIC)
    assert ss["i"] == pytest.approx(BASIC.delta * ss["k"])
    assert ss["c"] == pytest.approx(ss["y"] - ss["i"])
    assert ss["w"] == pytest.approx((1 - BASIC.alpha) * ss["y"] / BASIC.hours)
    assert ss["y"] == pytest.approx(
        ss["k"] ** BASIC.alpha * BASIC.hours ** (1 - BASIC.alpha)
    )


@pytest.mark.parametrize("endogenous_labour", [False, True])
def test_定常状態はすべての均衡条件を満たす(endogenous_labour: bool) -> None:
    ss = steady_state(BASIC, endogenous_labour)
    state = np.array([ss["a"], ss["k"], ss["c"]])
    residual = equilibrium_equations(BASIC, endogenous_labour)(state, state)
    assert residual == pytest.approx(np.zeros(3), abs=1e-10)


def test_内生的労働供給の定常状態では労働供給の条件が成り立つ() -> None:
    ss = steady_state(BASIC, endogenous_labour=True)
    assert (1 - ss["l"]) * ss["w"] == pytest.approx(BASIC.leisure_weight * ss["c"])


def test_余暇の重みから労働時間は約3分の1() -> None:
    assert steady_state(BASIC, True)["l"] == pytest.approx(0.332, abs=0.001)


def test_余暇の重みを決めると定常状態の労働時間が目標になる() -> None:
    m = calibrate_leisure_weight(BASIC, target_hours=1 / 3)
    params = RbcParameters(leisure_weight=m)
    assert steady_state(params, True)["l"] == pytest.approx(1 / 3)


def test_ショックがなければ定常状態にとどまる() -> None:
    solution = solve_rbc(BASIC)
    df = simulate_with_shocks(solution, np.zeros(10))
    assert df.to_numpy() == pytest.approx(0.0, abs=1e-12)


def test_基本モデルのインパクト効果は元の記事のlinearsolveの結果と一致する() -> None:
    df = impulse_response(solve_rbc(BASIC), shock=0.01)
    impact = df.iloc[3] / 1.0
    assert impact["a"] == pytest.approx(1.0)
    assert impact["k"] == pytest.approx(0.0)
    assert impact["y"] == pytest.approx(1.0)
    assert impact["w"] == pytest.approx(1.0)
    assert impact["r"] == pytest.approx(3.475, abs=0.001)
    assert impact["c"] == pytest.approx(0.0874, abs=0.0001)
    assert impact["i"] == pytest.approx(3.6466, abs=0.001)


def test_列と長さ() -> None:
    basic = impulse_response(solve_rbc(BASIC), shock=0.01)
    assert list(basic.columns) == ["a", "k", "c", "y", "i", "r", "w"]
    assert len(basic) == 3 + 1 + 40
    extended = impulse_response(solve_rbc(BASIC, True), shock=0.01, periods_after=10)
    assert list(extended.columns) == ["a", "k", "c", "y", "i", "r", "w", "l"]
    assert len(extended) == 3 + 1 + 10


def test_ショック前の3期間は定常状態() -> None:
    df = impulse_response(solve_rbc(BASIC), shock=0.01)
    assert df.iloc[:3].to_numpy() == pytest.approx(0.0)


def test_TFPはAR1で戻り資本は翌期から増える() -> None:
    df = impulse_response(solve_rbc(BASIC), shock=0.01)
    assert df["a"].iloc[4] == pytest.approx(BASIC.rho * df["a"].iloc[3])
    assert df["k"].iloc[4] > 0
    assert df["k"].iloc[5] > df["k"].iloc[4]


def test_消費は産出量より滑らかで投資は産出量より大きく動く() -> None:
    df = impulse_response(solve_rbc(BASIC), shock=0.01)
    assert df["c"].abs().max() < df["y"].abs().max()
    assert df["i"].abs().max() > df["y"].abs().max()


def test_モデルの均衡経路はすべての変数が定常状態に戻る() -> None:
    df = impulse_response(solve_rbc(BASIC), shock=0.01, periods_after=400)
    assert df.iloc[-1].abs().max() < 1e-2


def test_ショックは比例し足し合わせられる() -> None:
    solution = solve_rbc(BASIC)
    one = impulse_response(solution, shock=0.01)
    three = impulse_response(solution, shock=0.03)
    assert three.to_numpy() == pytest.approx(3 * one.to_numpy())


def test_シミュレーションは単位ショックの反応の重ね合わせ() -> None:
    solution = solve_rbc(BASIC)
    shocks = white_noise(60, 0.0078, np.random.default_rng(1))
    df = simulate_with_shocks(solution, shocks)
    unit = (
        impulse_response(solution, shock=1.0, periods_after=60)["y"].iloc[3:].to_numpy()
    )
    expected = np.convolve(shocks, unit)[:60]
    assert df["y"].to_numpy() == pytest.approx(expected)


def test_内生的労働供給では労働が増え産出量の反応が大きくなる() -> None:
    basic = impulse_response(solve_rbc(BASIC), shock=0.01)
    extended = impulse_response(solve_rbc(BASIC, True), shock=0.01)
    assert extended["l"].iloc[3] > 0
    assert extended["y"].iloc[3] > basic["y"].iloc[3]
    assert extended["w"].iloc[3] < basic["w"].iloc[3]
    assert extended["i"].iloc[3] > basic["i"].iloc[3]


@pytest.mark.parametrize("endogenous_labour", [False, True])
def test_オイラー方程式の誤差は定常状態で0(endogenous_labour: bool) -> None:
    solution = solve_rbc(BASIC, endogenous_labour)
    assert euler_residual(solution, 0.0, 0.0) == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("endogenous_labour", [False, True])
def test_オイラー方程式の誤差は乖離の2乗に比例して小さい(
    endogenous_labour: bool,
) -> None:
    solution = solve_rbc(BASIC, endogenous_labour)
    small = abs(euler_residual(solution, 0.005, 0.005))
    large = abs(euler_residual(solution, 0.01, 0.01))
    assert 0 < small < large < 1e-3
    assert 3 < large / small < 5


def test_βが1に近いほど資本産出比率が大きい() -> None:
    patient = RbcParameters(beta=0.995)
    assert steady_state(patient)["k"] / steady_state(patient)["y"] > (
        steady_state(BASIC)["k"] / steady_state(BASIC)["y"]
    )


def test_危険回避度θを変えても定常状態は変わらない() -> None:
    for theta in (0.5, 1.0, 2.0):
        params = RbcParameters(theta=theta)
        assert steady_state(params)["k"] == pytest.approx(steady_state(BASIC)["k"])
        assert euler_residual(solve_rbc(params), 0.0, 0.0) == pytest.approx(
            0.0, abs=1e-9
        )


def test_基本モデルの政策関数と遷移行列の固有値() -> None:
    solution = solve_rbc(BASIC)
    assert solution.policy[0] == pytest.approx([0.0874, 0.6182], abs=0.0001)
    eigenvalues = sorted(float(v) for v in np.linalg.eigvals(solution.transition).real)
    assert eigenvalues == pytest.approx([0.551, 0.9653], abs=0.0001)


def test_内生的労働供給の政策関数と遷移行列の固有値() -> None:
    solution = solve_rbc(BASIC, True)
    assert solution.policy[0] == pytest.approx([0.1307, 0.569], abs=0.0001)
    eigenvalues = sorted(float(v) for v in np.linalg.eigvals(solution.transition).real)
    assert eigenvalues == pytest.approx([0.551, 0.9536], abs=0.0001)


def test_内生的労働供給のインパクト効果() -> None:
    impact = impulse_response(solve_rbc(BASIC, True), shock=0.01).iloc[3]
    assert impact["y"] == pytest.approx(1.649, abs=0.001)
    assert impact["c"] == pytest.approx(0.131, abs=0.001)
    assert impact["i"] == pytest.approx(6.051, abs=0.001)
    assert impact["r"] == pytest.approx(5.730, abs=0.001)
    assert impact["w"] == pytest.approx(0.635, abs=0.001)
    assert impact["l"] == pytest.approx(1.014, abs=0.001)


def test_労働供給は数期後に定常状態を下回る() -> None:
    df = impulse_response(solve_rbc(BASIC, True), shock=0.01)
    assert df["l"].iloc[3] > 0
    assert df["l"].iloc[9] < 0
    assert df["l"].iloc[15] < 0


def test_危険回避度が大きいほど消費の最初の反応は小さい() -> None:
    impacts = [
        float(
            impulse_response(solve_rbc(RbcParameters(theta=theta)), shock=0.01)[
                "c"
            ].iloc[3]
        )
        for theta in (0.5, 1.0, 2.0, 5.0)
    ]
    assert impacts == pytest.approx([0.0927, 0.0874, 0.0758, 0.0599], abs=0.0001)
    assert impacts == sorted(impacts, reverse=True)


def test_基本モデルのシミュレーションの特徴() -> None:
    sim = stochastic_simulation(solve_rbc(BASIC), 100000, np.random.default_rng(0))
    assert sim["c"].std() / sim["y"].std() == pytest.approx(0.393, abs=0.001)
    assert sim["i"].std() / sim["y"].std() == pytest.approx(3.395, abs=0.001)
    assert sim["c"].autocorr() == pytest.approx(0.984, abs=0.001)
    assert sim["i"].autocorr() == pytest.approx(0.537, abs=0.001)
    assert sim["y"].corr(sim["c"]) == pytest.approx(0.561, abs=0.001)
    assert sim["y"].corr(sim["i"]) == pytest.approx(0.961, abs=0.001)


def test_内生的労働供給のシミュレーションの特徴() -> None:
    sim = stochastic_simulation(
        solve_rbc(BASIC, True), 100000, np.random.default_rng(0)
    )
    assert sim["y"].std() == pytest.approx(1.583, abs=0.001)
    assert sim["c"].std() / sim["y"].std() == pytest.approx(0.328, abs=0.001)
    assert sim["i"].std() / sim["y"].std() == pytest.approx(3.509, abs=0.001)
    assert sim["l"].std() / sim["y"].std() == pytest.approx(0.586, abs=0.001)
    assert sim["y"].corr(sim["l"]) == pytest.approx(0.947, abs=0.001)


def test_シミュレーションの種が同じなら同じ結果() -> None:
    solution = solve_rbc(BASIC)
    first = stochastic_simulation(solution, 50, np.random.default_rng(3))
    second = stochastic_simulation(solution, 50, np.random.default_rng(3))
    assert first.to_numpy() == pytest.approx(second.to_numpy())


def test_HPフィルターをかけたシミュレーションの特徴() -> None:
    for labour, y_std, c_rel, i_rel, c_ac in (
        (False, 0.815, 0.140, 3.693, 0.828),
        (True, 1.349, 0.129, 3.715, 0.834),
    ):
        sim = stochastic_simulation(
            solve_rbc(BASIC, labour), 2000, np.random.default_rng(0)
        )
        y, c, i = cycle(sim["y"]), cycle(sim["c"]), cycle(sim["i"])
        assert y.std() == pytest.approx(y_std, abs=0.001)
        assert c.std() / y.std() == pytest.approx(c_rel, abs=0.001)
        assert i.std() / y.std() == pytest.approx(i_rel, abs=0.001)
        assert c.autocorr() == pytest.approx(c_ac, abs=0.001)
        assert y.corr(i) == pytest.approx(0.996, abs=0.001)


def test_減耗率が1ならパラメーターとして受け付けない() -> None:
    with pytest.raises(ValueError, match="パラメーター"):
        RbcParameters(delta=1.0)


def test_ショックの標準偏差が0でも受け付ける() -> None:
    assert RbcParameters(sigma=0.0).sigma == 0.0
