"""対数線形近似と、先を見る変数がある線形モデルの解法。

モデルは、均衡条件 f(x', x) = 0（x': 来期の変数、x: 今期の変数）で与える。
定常状態 x* は、f(x*, x*) = 0 の解。x̂ = ln(x ÷ x*)（定常状態からの乖離）で書くと、
  A·x̂' + B·x̂ = 0、A = ∂f/∂ln x'、B = ∂f/∂ln x（定常状態で、数値微分する）。
x̂' = M·x̂（M = -A⁻¹B）。変数を、状態変数（前の期に決まる）→ ジャンプ変数
（今期に決まる。先を見る）の順に並べたとき、ブランチャード・カーンの条件
（|固有値| > 1 の数 = ジャンプ変数の数）が成り立てば、解が一意に決まる。
"""

from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from lib.chapter16.solow_stochastic import SolowParameters, steady_state_capital

Vector = NDArray[np.float64]
Equations = Callable[[Vector, Vector], Vector]


def numerical_jacobian(
    f: Callable[[Vector], Vector], x: Vector, step: float = 1e-6
) -> NDArray[np.float64]:
    """ヤコビ行列を、中心差分で求める（(f(x + h) - f(x - h)) ÷ 2h）。"""
    columns = []
    for i in range(len(x)):
        shift = np.zeros(len(x))
        shift[i] = step * max(1.0, abs(x[i]))
        columns.append((f(x + shift) - f(x - shift)) / (2 * shift[i]))
    return np.column_stack(columns)


def find_steady_state(
    equations: Equations,
    guess: Vector,
    tol: float = 1e-10,
    max_iter: int = 100,
) -> Vector:
    """f(x, x) = 0 の解を、ニュートン法で探す。"""
    x = np.array(guess, dtype=float)
    for _ in range(max_iter):
        residual = equations(x, x)
        if np.max(np.abs(residual)) < tol:
            return x
        jacobian = numerical_jacobian(lambda v: equations(v, v), x)
        try:
            x = x - np.linalg.solve(jacobian, residual)
        except np.linalg.LinAlgError as error:
            raise ValueError("定常状態が収束しない（ヤコビ行列が特異）") from error
    raise ValueError("定常状態が収束しない（繰り返しの回数が足りない）")


def log_linearize(
    equations: Equations, steady_state: Vector
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """定常状態の近くで、A·x̂' + B·x̂ = 0 の A と B を求める。"""
    n = len(steady_state)

    def in_logs(u: Vector) -> Vector:
        return equations(steady_state * np.exp(u[:n]), steady_state * np.exp(u[n:]))

    jacobian = numerical_jacobian(in_logs, np.zeros(2 * n))
    return jacobian[:, :n], jacobian[:, n:]


def linear_transition(
    a_matrix: NDArray[np.float64], b_matrix: NDArray[np.float64]
) -> NDArray[np.float64]:
    """x̂' = M·x̂ の M = -A⁻¹B。"""
    return -np.linalg.solve(a_matrix, b_matrix)


def solve_saddle_path(
    a_matrix: NDArray[np.float64],
    b_matrix: NDArray[np.float64],
    n_state: int,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """状態変数が n_state 個、残りがジャンプ変数のモデルを解く。

    解は、ジャンプ変数 = P·状態変数、状態変数の遷移 x̂_s' = T·x̂_s。(P, T) を返す。
    M の、|固有値| > 1 の左固有ベクトルが、ジャンプ変数の数だけあるとき、
    それらに直交する経路（W·x̂ = 0）が、爆発しない唯一の解。
    """
    n = a_matrix.shape[0]
    if not 0 <= n_state <= n:
        raise ValueError("状態変数の数は、0 以上、変数の数以下でなければならない")
    n_jump = n - n_state
    m = linear_transition(a_matrix, b_matrix)
    values, vectors = np.linalg.eig(m.T)
    unstable = np.abs(values) > 1 + 1e-9
    if unstable.sum() > n_jump:
        raise ValueError("解が存在しない（不安定な固有値が、ジャンプ変数より多い）")
    if unstable.sum() < n_jump:
        raise ValueError(
            "解が一意に決まらない（不安定な固有値が、ジャンプ変数より少ない）"
        )
    w: Any = np.real_if_close(vectors[:, unstable].T, tol=1000)
    if np.iscomplexobj(w):
        raise ValueError("不安定な固有値が複素数の場合は扱わない")
    policy: Any
    if n_jump == 0:
        policy = np.zeros((0, n_state))
    else:
        policy = -np.linalg.solve(w[:, n_state:], w[:, :n_state])
    transition = m[:n_state, :n_state] + m[:n_state, n_state:] @ policy
    return policy.real, transition.real


def solow_equations(params: SolowParameters) -> Equations:
    """確率的ソロー・モデルの均衡条件（変数は (A, K)）。

    A' = A^ρ、K' = s·A·K^α·H^(1-α) + (1-δ)·K。
    """

    def equations(x_next: Vector, x: Vector) -> Vector:
        tfp = x_next[0] - x[0] ** params.rho
        capital = x_next[1] - (
            params.saving
            * x[0]
            * x[1] ** params.alpha
            * params.hours ** (1 - params.alpha)
            + (1 - params.depreciation) * x[1]
        )
        return np.array([tfp, capital])

    return equations


def capital_paths(
    params: SolowParameters, initial_deviation: float, periods: int
) -> pd.DataFrame:
    """ショックのないソロー・モデルで、資本の乖離（%）の、厳密な経路と、線形近似の経路。

    初期の乖離 ln(K0 ÷ K*) = initial_deviation（0.01 なら 1%）。
    """
    k_star = steady_state_capital(params)
    transition = linear_transition(
        *log_linearize(solow_equations(params), np.array([1.0, k_star]))
    )
    capital = k_star * np.exp(initial_deviation)
    exact = [100 * np.log(capital / k_star)]
    linear = [100 * initial_deviation]
    for _ in range(periods):
        capital = (
            params.saving * capital**params.alpha * params.hours ** (1 - params.alpha)
            + (1 - params.depreciation) * capital
        )
        exact.append(100 * np.log(capital / k_star))
        linear.append(linear[-1] * transition[1, 1])
    return pd.DataFrame({"exact": exact, "linear": linear})
