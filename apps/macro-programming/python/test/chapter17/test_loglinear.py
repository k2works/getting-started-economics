"""第 17 章: 対数線形近似と、線形の動学の解法のテスト。

モデルは、均衡条件 f(x', x) = 0（x': 来期の変数、x: 今期の変数）で与える。
対数線形近似: x̂ = ln(x ÷ x*)。A·x̂' + B·x̂ = 0、A = ∂f/∂ln x'、B = ∂f/∂ln x。
"""

import numpy as np
import pytest
from numpy.typing import NDArray

from lib.chapter05.solow import convergence_speed
from lib.chapter16.solow_stochastic import SolowParameters, steady_state_capital
from lib.chapter17.loglinear import (
    capital_paths,
    find_steady_state,
    linear_transition,
    log_linearize,
    numerical_jacobian,
    solow_equations,
    solve_saddle_path,
)

PARAMS = SolowParameters(
    alpha=0.36, saving=0.2, depreciation=0.025, rho=0.55, sigma=0.0078, hours=1.0
)


def test_数値微分は手計算の導関数と一致する() -> None:
    def f(x: NDArray[np.float64]) -> NDArray[np.float64]:
        return np.array([x[0] ** 2, x[0] * x[1]])

    jacobian = numerical_jacobian(f, np.array([2.0, 3.0]))
    assert jacobian == pytest.approx(np.array([[4.0, 0.0], [3.0, 2.0]]), abs=1e-6)


def test_定常状態は今期と来期が等しい点() -> None:
    def f(x_next: NDArray[np.float64], x: NDArray[np.float64]) -> NDArray[np.float64]:
        return x_next - (0.5 * x + 1.0)

    assert find_steady_state(f, np.array([10.0])) == pytest.approx([2.0])


def test_ソローモデルの定常状態は解析解と一致する() -> None:
    ss = find_steady_state(solow_equations(PARAMS), np.array([1.2, 20.0]))
    assert ss[0] == pytest.approx(1.0)
    assert ss[1] == pytest.approx(steady_state_capital(PARAMS))


def test_定常状態が見つからなければ受け付けない() -> None:
    def f(x_next: NDArray[np.float64], x: NDArray[np.float64]) -> NDArray[np.float64]:
        return np.array([1.0 + 0.0 * x_next[0] * x[0]])

    with pytest.raises(ValueError, match="収束"):
        find_steady_state(f, np.array([1.0]))


def test_繰り返しの回数が足りなければ受け付けない() -> None:
    def f(x_next: NDArray[np.float64], x: NDArray[np.float64]) -> NDArray[np.float64]:
        return np.array([x_next[0] ** 2 + 1.0 - x[0] * 0.0])

    with pytest.raises(ValueError, match="収束"):
        find_steady_state(f, np.array([1.0]), max_iter=5)


def test_対数線形近似の行列は手計算の値() -> None:
    k_star = steady_state_capital(PARAMS)
    ss = np.array([1.0, k_star])
    a_matrix, b_matrix = log_linearize(solow_equations(PARAMS), ss)
    delta, alpha, rho = PARAMS.depreciation, PARAMS.alpha, PARAMS.rho
    assert a_matrix == pytest.approx(np.array([[1.0, 0.0], [0.0, k_star]]), abs=1e-6)
    assert b_matrix == pytest.approx(
        np.array([[-rho, 0.0], [-delta * k_star, -k_star * (1 - (1 - alpha) * delta)]]),
        abs=1e-6,
    )


def test_線形の遷移行列は第5章の収束の速さと一致する() -> None:
    k_star = steady_state_capital(PARAMS)
    transition = linear_transition(
        *log_linearize(solow_equations(PARAMS), np.array([1.0, k_star]))
    )
    speed = convergence_speed(PARAMS.alpha, PARAMS.depreciation)
    assert transition[1, 1] == pytest.approx(1 - speed, abs=1e-6)
    assert transition[1, 0] == pytest.approx(PARAMS.depreciation, abs=1e-6)
    assert transition[0, 0] == pytest.approx(PARAMS.rho, abs=1e-6)
    assert transition[0, 1] == pytest.approx(0.0, abs=1e-6)


def test_先を見る変数が1つのモデルの解は手計算の値() -> None:
    """x(t) = λ·E x(t+1) + a(t)、a(t+1) = ρ·a(t)。解は x = a ÷ (1 - λ·ρ)。"""
    lam, rho = 0.9, 0.5
    a_matrix = np.array([[1.0, 0.0], [0.0, lam]])
    b_matrix = np.array([[-rho, 0.0], [1.0, -1.0]])
    policy, transition = solve_saddle_path(a_matrix, b_matrix, n_state=1)
    assert policy == pytest.approx(np.array([[1 / (1 - lam * rho)]]))
    assert transition == pytest.approx(np.array([[rho]]))


def test_先を見る変数がなければ遷移行列がそのまま解() -> None:
    k_star = steady_state_capital(PARAMS)
    a_matrix, b_matrix = log_linearize(solow_equations(PARAMS), np.array([1.0, k_star]))
    policy, transition = solve_saddle_path(a_matrix, b_matrix, n_state=2)
    assert policy.shape == (0, 2)
    assert transition == pytest.approx(linear_transition(a_matrix, b_matrix), abs=1e-9)


def test_不安定な固有値がなければ解は決まらない() -> None:
    """λ > 1 だと 1/λ < 1 で、先を見る変数の解が、一意に決まらない。"""
    a_matrix = np.array([[1.0, 0.0], [0.0, 1.5]])
    b_matrix = np.array([[-0.5, 0.0], [1.0, -1.0]])
    with pytest.raises(ValueError, match="一意"):
        solve_saddle_path(a_matrix, b_matrix, n_state=1)


def test_不安定な固有値が多すぎれば解は存在しない() -> None:
    a_matrix = np.eye(2)
    b_matrix = -np.diag([1.5, 2.0])
    with pytest.raises(ValueError, match="存在"):
        solve_saddle_path(a_matrix, b_matrix, n_state=1)


def test_複素数の固有値は扱わない() -> None:
    angle = 0.3
    rotation = 1.5 * np.array(
        [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
    )
    with pytest.raises(ValueError, match="複素数"):
        solve_saddle_path(np.eye(2), -rotation, n_state=0)


def test_厳密な経路の最初の期は初期の乖離そのもの() -> None:
    df = capital_paths(PARAMS, initial_deviation=0.01, periods=10)
    assert list(df.columns) == ["exact", "linear"]
    assert len(df) == 11
    assert df["exact"].iloc[0] == pytest.approx(1.0)
    assert df["linear"].iloc[0] == pytest.approx(1.0)


def test_近似の経路は遷移係数の累乗() -> None:
    df = capital_paths(PARAMS, initial_deviation=0.01, periods=10)
    coefficient = 1 - (1 - PARAMS.alpha) * PARAMS.depreciation
    assert df["linear"].iloc[10] == pytest.approx(coefficient**10, abs=1e-6)


def test_定常状態に近ければ近似の誤差は小さい() -> None:
    df = capital_paths(PARAMS, initial_deviation=0.01, periods=40)
    assert (df["exact"] - df["linear"]).abs().max() < 1e-3


def test_定常状態から遠いほど近似の誤差は大きい() -> None:
    errors = []
    for size in (0.01, 0.1, 0.5):
        df = capital_paths(PARAMS, initial_deviation=size, periods=20)
        errors.append(float((df["exact"] - df["linear"]).abs().max()) / (100 * size))
    assert errors[0] < errors[1] < errors[2]


def test_厳密な経路は単調に減って定常状態に近づく() -> None:
    df = capital_paths(PARAMS, initial_deviation=0.5, periods=400)
    assert df["exact"].is_monotonic_decreasing
    assert df["exact"].iloc[-1] > 0
    assert df["exact"].iloc[-1] < 0.01 * df["exact"].iloc[0]


def test_複素数の固有値でも不安定でなければ遷移行列がそのまま解() -> None:
    angle = 0.3
    rotation = 0.5 * np.array(
        [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
    )
    policy, transition = solve_saddle_path(np.eye(2), -rotation, n_state=2)
    assert policy.shape == (0, 2)
    assert transition == pytest.approx(rotation)


def test_隔離環境のlinearsolveの結果と一致する() -> None:
    """linearsolve（pandas 2 の隔離環境）が、α = 0.5、s = 0.2、δ = 0.05 で出した 0.975。"""
    params = SolowParameters(alpha=0.5, saving=0.2, depreciation=0.05)
    k_star = steady_state_capital(params)
    transition = linear_transition(
        *log_linearize(solow_equations(params), np.array([1.0, k_star]))
    )
    assert transition[1, 1] == pytest.approx(0.975, abs=1e-6)


def test_絶対値がちょうど1の固有値は不安定とは数えない() -> None:
    policy, transition = solve_saddle_path(np.eye(1), -np.eye(1), n_state=1)
    assert policy.shape == (0, 1)
    assert transition == pytest.approx(np.eye(1))


@pytest.mark.parametrize("n_state", [-1, 3])
def test_状態変数の数が範囲外なら受け付けない(n_state: int) -> None:
    with pytest.raises(ValueError, match="状態変数"):
        solve_saddle_path(np.eye(2), -np.eye(2) * 0.5, n_state=n_state)
