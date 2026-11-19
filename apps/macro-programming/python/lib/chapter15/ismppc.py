"""IS-MP-PC モデル: 中央銀行が名目利子率を決める、動学的なマクロ・モデル。

  フィッシャー方程式  r(t) = i(t) - E π(t+1)
  適応的期待          E π(t+1) = π(t)
  IS 曲線   y(t) = y* - a·(r(t) - r*) + u(t)
  MP 曲線   i(t) = r* + π(t) + c·(π(t) - π*) + d·(y(t) - y*) + v(t)（テイラー・ルール）
  PC 曲線   π(t) = π(t-1) + b·(y(t) - y*) + e(t)
IS 曲線と MP 曲線から動的総需要（ISMP）、PC 曲線が動的総供給。
2 本を、行列で、A·X(t) = B·X(t-1) + C(t) とまとめる（X = (y, π)）。
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import NDArray


@dataclass(frozen=True)
class IsMpPcParameters:
    """IS 曲線の a、フィリップス曲線の b、MP 曲線の c・d と、定常状態の値。"""

    a: float = 1.0
    b: float = 0.25
    c: float = 1.5
    d: float = 0.5
    y_star: float = 100.0
    pi_star: float = 2.0
    r_star: float = 2.0

    def __post_init__(self) -> None:
        if self.a <= 0 or self.b <= 0 or self.c < 0 or self.d < 0:
            raise ValueError(
                "パラメーターは、a・b が正、c・d が 0 以上でなければならない"
            )

    @property
    def gamma(self) -> float:
        """γ = 1 + a·d。"""
        return 1 + self.a * self.d

    @property
    def phi(self) -> float:
        """インフレ率の差分方程式の係数 φ = (1 + a·d) ÷ (1 + a·b·c + a·d)。"""
        return self.gamma / (1 + self.a * self.b * self.c + self.a * self.d)


def ismppc_matrices(
    params: IsMpPcParameters,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """A·X(t) = B·X(t-1) + C(t) の、行列 A と B（X = (y, π)）。"""
    a_matrix = np.array([[params.gamma, params.a * params.c], [-params.b, 1.0]])
    b_matrix = np.array([[0.0, 0.0], [0.0, 1.0]])
    return a_matrix, b_matrix


def eigenvalues(params: IsMpPcParameters) -> NDArray[np.float64]:
    """A⁻¹·B の固有値（小さい順）。1 つは 0、もう 1 つは φ。"""
    a_matrix, b_matrix = ismppc_matrices(params)
    return np.sort(np.linalg.eigvals(np.linalg.solve(a_matrix, b_matrix)).real)


def is_stable(params: IsMpPcParameters) -> bool:
    """固有値の絶対値が、すべて 1 より小さければ、安定（定常状態に戻る）。"""
    return bool(np.all(np.abs(eigenvalues(params)) < 1))


def policy_rate(params: IsMpPcParameters, y: float, pi: float, v: float = 0.0) -> float:
    """MP 曲線: 名目利子率 i = r* + π + c·(π - π*) + d·(y - y*) + v。"""
    return (
        params.r_star
        + pi
        + params.c * (pi - params.pi_star)
        + params.d * (y - params.y_star)
        + v
    )


def step(
    params: IsMpPcParameters,
    y_prev: float,
    pi_prev: float,
    u: float,
    v: float,
    e: float,
) -> tuple[float, float]:
    """前期の (y, π) と今期のショック (u, v, e) から、今期の (y, π) を求める。"""
    a_matrix, b_matrix = ismppc_matrices(params)
    constants = np.array(
        [
            params.gamma * params.y_star
            + params.a * params.c * params.pi_star
            + u
            - params.a * v,
            -params.b * params.y_star + e,
        ]
    )
    y, pi = np.linalg.solve(
        a_matrix, b_matrix @ np.array([y_prev, pi_prev]) + constants
    )
    return float(y), float(pi)


def _row(params: IsMpPcParameters, y: float, pi: float, v: float) -> dict[str, float]:
    i = policy_rate(params, y, pi, v)
    return {"pi": pi, "y": y, "i": i, "r": i - pi}


def impulse_response(
    params: IsMpPcParameters,
    shock_is: float = 0.0,
    shock_mp: float = 0.0,
    shock_pc: float = 0.0,
    periods_after: int = 20,
) -> pd.DataFrame:
    """1 期間だけのショック（IS: u、MP: v、PC: e）への反応。

    最初の 3 期間は定常状態、4 期目にショック、その後は、ショックなし。
    列は pi（インフレ率）、y（産出量）、i（名目利子率）、r（実質利子率）。
    """
    steady = _row(params, params.y_star, params.pi_star, 0.0)
    rows = [dict(steady) for _ in range(3)]
    y, pi = params.y_star, params.pi_star
    shocks = [(shock_is, shock_mp, shock_pc)] + [(0.0, 0.0, 0.0)] * periods_after
    for u, v, e in shocks:
        y, pi = step(params, y, pi, u, v, e)
        rows.append(_row(params, y, pi, v))
    return pd.DataFrame(rows)


def simulate_without_shocks(
    params: IsMpPcParameters, pi0: float, y0: float, n: int
) -> pd.DataFrame:
    """初期値 (y0, π0) から、ショックなしで、n 期間の移行過程を計算する。"""
    y, pi = y0, pi0
    rows = [_row(params, y, pi, 0.0)]
    for _ in range(n):
        y, pi = step(params, y, pi, 0.0, 0.0, 0.0)
        rows.append(_row(params, y, pi, 0.0))
    return pd.DataFrame(rows)
