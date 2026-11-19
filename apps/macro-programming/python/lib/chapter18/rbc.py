"""実物的景気循環（RBC）モデル: 消費者の最適化から、景気循環を説明する。

  効用  u = (C^(1-θ) - 1) ÷ (1-θ) + m·ln(1 - L)
        （基本モデルでは L が一定で、余暇の項はない）
  オイラー条件  C(t)^(-θ) = β·E[(1 + R(t+1))·C(t+1)^(-θ)]
  労働供給（内生的労働供給のとき）  C(t)^(-θ) = m ÷ ((1 - L(t))·W(t))
  生産関数  Y = A·K^α·L^(1-α)、資本の蓄積  K' = I + (1-δ)·K、所得恒等式  Y = C + I
  実質利子率  R = α·Y/K - δ、実質賃金  W = (1-α)·Y/L、TFP  A' = A^ρ·e^v

状態変数は (A, K)、ジャンプ変数は C（今期に、将来を見据えて決まる）。
他の変数（Y, I, R, W, L）は、(A, K, C) から決まる。第 17 章の、対数線形近似と
解法（solve_saddle_path）で、解く。
"""

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from lib.chapter08.stochastic import white_noise
from lib.chapter17.loglinear import (
    Equations,
    Vector,
    log_linearize,
    numerical_jacobian,
    solve_saddle_path,
)


@dataclass(frozen=True)
class RbcParameters:
    """α（資本分配率）、β（割引因子）、δ（減耗率）、ρ・σ（TFP）、θ、L、m（余暇の重み）。"""

    alpha: float = 0.36
    beta: float = 0.99
    delta: float = 0.025
    rho: float = 0.551
    sigma: float = 0.0078
    theta: float = 1.0
    hours: float = 0.33
    leisure_weight: float = 1.73

    def __post_init__(self) -> None:
        if not (
            0 < self.alpha < 1
            and 0 < self.beta < 1
            and 0 < self.delta < 1
            and abs(self.rho) < 1
            and self.sigma >= 0
            and self.theta > 0
            and self.hours > 0
            and self.leisure_weight > 0
        ):
            raise ValueError(
                "パラメーターは、α・β・δ が 0 と 1 の間、|ρ| < 1、σ ≥ 0、"
                "θ・L・m > 0 でなければならない"
            )


def _capital_labour_ratio(params: RbcParameters) -> float:
    """K ÷ L = (α ÷ (R + δ))^(1÷(1-α))、R = 1 ÷ β - 1。"""
    r = 1 / params.beta - 1
    return float((params.alpha / (r + params.delta)) ** (1 / (1 - params.alpha)))


def _steady_hours(params: RbcParameters) -> float:
    """内生的労働供給の定常状態の労働時間 L = (1-α)·y ÷ ((1-α)·y + m·(y - δ·z))。

    z = K ÷ L、y = z^α（1 人当たりの産出量）。
    """
    z = _capital_labour_ratio(params)
    y = z**params.alpha
    wage = (1 - params.alpha) * y
    return float(wage / (wage + params.leisure_weight * (y - params.delta * z)))


def calibrate_leisure_weight(params: RbcParameters, target_hours: float) -> float:
    """定常状態の労働時間が target_hours になる、余暇の重み m。"""
    z = _capital_labour_ratio(params)
    y = z**params.alpha
    return float(
        (1 - target_hours)
        * (1 - params.alpha)
        * y
        / (target_hours * (y - params.delta * z))
    )


def steady_state(
    params: RbcParameters, endogenous_labour: bool = False
) -> dict[str, float]:
    """定常状態（A = 1）の、A・K・C・Y・I・R・W・L。"""
    hours = _steady_hours(params) if endogenous_labour else params.hours
    k = _capital_labour_ratio(params) * hours
    y = k**params.alpha * hours ** (1 - params.alpha)
    return {
        "a": 1.0,
        "k": k,
        "c": y - params.delta * k,
        "y": y,
        "i": params.delta * k,
        "r": 1 / params.beta - 1,
        "w": (1 - params.alpha) * y / hours,
        "l": hours,
    }


def _solve_labour(params: RbcParameters, a: float, k: float, c: float) -> float:
    """労働供給の条件 (1 - L)·W = m·C^θ を満たす L を、二分法で求める。"""
    low, high = 1e-12, 1 - 1e-12
    for _ in range(100):
        mid = (low + high) / 2
        wage = (1 - params.alpha) * a * k**params.alpha * mid**-params.alpha
        if (1 - mid) * wage > params.leisure_weight * c**params.theta:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def _statics(
    params: RbcParameters, endogenous_labour: bool, a: float, k: float, c: float
) -> dict[str, float]:
    """(A, K, C) から決まる、Y・I・R・W・L。"""
    hours = _solve_labour(params, a, k, c) if endogenous_labour else params.hours
    y = a * k**params.alpha * hours ** (1 - params.alpha)
    return {
        "y": y,
        "i": y - c,
        "r": params.alpha * y / k - params.delta,
        "w": (1 - params.alpha) * y / hours,
        "l": hours,
    }


def equilibrium_equations(
    params: RbcParameters, endogenous_labour: bool = False
) -> Equations:
    """均衡条件 f(x', x) = 0（x = (A, K, C)）: TFP、資本の蓄積、オイラー方程式。"""

    def equations(x_next: Vector, x: Vector) -> Vector:
        now = _statics(params, endogenous_labour, *x)
        nxt = _statics(params, endogenous_labour, *x_next)
        tfp = x_next[0] - x[0] ** params.rho
        capital = x_next[1] - (now["y"] - x[2] + (1 - params.delta) * x[1])
        euler = (
            params.beta * (1 + nxt["r"]) / x_next[2] ** params.theta
            - 1 / x[2] ** params.theta
        )
        return np.array([tfp, capital, euler])

    return equations


@dataclass(frozen=True)
class RbcSolution:
    """対数線形近似した RBC モデルの解。

    policy: ジャンプ変数（消費）= policy @ (a, k)。transition: (a, k) の遷移行列。
    statics: (a, k, c) から、y・i・r・w（・l）の乖離を求める行列。
    """

    params: RbcParameters
    endogenous_labour: bool
    steady: dict[str, float]
    policy: NDArray[np.float64]
    transition: NDArray[np.float64]
    statics: NDArray[np.float64]
    static_names: tuple[str, ...]


def solve_rbc(params: RbcParameters, endogenous_labour: bool = False) -> RbcSolution:
    """RBC モデルを、定常状態の近くで、対数線形近似して解く。"""
    ss = steady_state(params, endogenous_labour)
    x_star = np.array([ss["a"], ss["k"], ss["c"]])
    a_matrix, b_matrix = log_linearize(
        equilibrium_equations(params, endogenous_labour), x_star
    )
    policy, transition = solve_saddle_path(a_matrix, b_matrix, n_state=2)
    names = ("y", "i", "r", "w", "l") if endogenous_labour else ("y", "i", "r", "w")

    def static_logs(u: Vector) -> Vector:
        values = _statics(params, endogenous_labour, *(x_star * np.exp(u)))
        return np.array([np.log(values[name]) for name in names])

    statics = numerical_jacobian(static_logs, np.zeros(3))
    return RbcSolution(
        params=params,
        endogenous_labour=endogenous_labour,
        steady=ss,
        policy=policy,
        transition=transition,
        statics=statics,
        static_names=names,
    )


def _responses(solution: RbcSolution, states: NDArray[np.float64]) -> pd.DataFrame:
    """状態変数 (a, k)（対数の乖離）の系列から、すべての変数の乖離（%）を求める。"""
    consumption = states @ solution.policy.T
    core = np.column_stack([states, consumption])
    others = core @ solution.statics.T
    data: dict[str, Any] = {
        "a": states[:, 0],
        "k": states[:, 1],
        "c": consumption[:, 0],
    }
    for i, name in enumerate(solution.static_names):
        data[name] = others[:, i]
    return pd.DataFrame(data) * 100


def simulate_with_shocks(
    solution: RbcSolution, shocks: NDArray[np.float64]
) -> pd.DataFrame:
    """TFP のショック v(t) の系列から、すべての変数の乖離（%）を計算する。"""
    state = np.zeros(2)
    states = []
    for shock in shocks:
        state = solution.transition @ state + np.array([float(shock), 0.0])
        states.append(state)
    return _responses(solution, np.array(states))


def impulse_response(
    solution: RbcSolution,
    shock: float = 0.01,
    periods_after: int = 40,
    periods_before: int = 3,
) -> pd.DataFrame:
    """1 期間だけの TFP ショック（既定は 1%）への反応（定常状態からの乖離、%）。"""
    shocks = np.zeros(periods_before + 1 + periods_after)
    shocks[periods_before] = shock
    return simulate_with_shocks(solution, shocks)


def stochastic_simulation(
    solution: RbcSolution, n: int, rng: np.random.Generator
) -> pd.DataFrame:
    """毎期、TFP にショックが起きる、n 期間のシミュレーション（乱数の生成器を渡す）。"""
    return simulate_with_shocks(solution, white_noise(n, solution.params.sigma, rng))


def euler_residual(solution: RbcSolution, a_dev: float, k_dev: float) -> float:
    """対数線形の解（政策関数）を、非線形のオイラー方程式に入れたときの、誤差。

    状態 (ln A, ln K - ln K*) = (a_dev, k_dev)。消費は政策関数、来期の状態は
    非線形の式（ショックなし）で求め、β·(1 + R')·(C ÷ C')^θ - 1 を返す。
    定常状態では 0。解が正しければ、乖離の 2 乗に比例して、小さい。
    """
    params, ss = solution.params, solution.steady
    consumption = ss["c"] * np.exp(solution.policy[0] @ np.array([a_dev, k_dev]))
    a, k = np.exp(a_dev), ss["k"] * np.exp(k_dev)
    now = _statics(params, solution.endogenous_labour, a, k, consumption)
    a_next = a**params.rho
    k_next = now["y"] - consumption + (1 - params.delta) * k
    states_next = np.array([np.log(a_next), np.log(k_next / ss["k"])])
    consumption_next = ss["c"] * np.exp(solution.policy[0] @ states_next)
    nxt = _statics(params, solution.endogenous_labour, a_next, k_next, consumption_next)
    return float(
        params.beta * (1 + nxt["r"]) * (consumption / consumption_next) ** params.theta
        - 1
    )
