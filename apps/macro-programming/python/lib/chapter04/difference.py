"""1 階差分方程式 x(t+1) = a·x(t) + b と、経済モデルへの応用。

定常状態 x* = b ÷ (1 − a) のまわりで、x(t) − x* は、毎期 a 倍になる。
|a| < 1 なら、x は定常状態に近づく（安定）。a < 0 なら、上下に往復する。
"""

from collections.abc import Callable


def iterate(f: Callable[[float], float], initial: float, periods: int) -> list[float]:
    """x(t+1) = f(x(t)) を periods 回繰り返した値を、初期値から順に並べる。"""
    if periods < 0:
        raise ValueError("繰り返しの回数は 0 以上でなければならない")
    path = [initial]
    for _ in range(periods):
        path.append(f(path[-1]))
    return path


def linear_path(a: float, b: float, initial: float, periods: int) -> list[float]:
    """x(t+1) = a·x(t) + b の経路（初期値を含めて periods + 1 個）を返す。"""
    return iterate(lambda x: a * x + b, initial, periods)


def steady_state(a: float, b: float) -> float:
    """定常状態 x* = b ÷ (1 − a)。a = 1 のときは、求められない。"""
    if a == 1:
        raise ValueError("a が 1 のときは、定常状態が決まらない")
    return b / (1 - a)


def is_stable(a: float) -> bool:
    """|a| < 1 なら、どの初期値からでも、定常状態に近づく。"""
    return abs(a) < 1


def closed_form(a: float, b: float, initial: float, t: int) -> float:
    """t 期の値を、繰り返さずに求める。x(t) = a^t·(x(0) − x*) + x*。"""
    steady = steady_state(a, b)
    return a**t * (initial - steady) + steady


def income_adjustment(
    autonomous_consumption: float,
    mpc: float,
    investment: float,
    initial_income: float,
    periods: int,
) -> list[float]:
    """45 度線モデルの所得の調整: Y(t+1) = C0 + c·Y(t) + I の経路。

    今期の所得が、来期の消費を決める。定常状態は、乗数を使った国民所得と同じ。
    """
    return linear_path(
        mpc, autonomous_consumption + investment, initial_income, periods
    )


def cobweb_coefficients(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
) -> tuple[float, float]:
    """蜘蛛の巣モデルを、P(t) = a·P(t−1) + b の形にしたときの (a, b) を返す。

    需要 Q = a₀ − b₀·P(t)、供給は前期の価格で決まる Q = c + d·P(t−1) なので、
    P(t) = (a₀ − c) ÷ b₀ − (d ÷ b₀)·P(t−1)。
    """
    if demand_slope <= 0:
        raise ValueError("需要曲線の傾きは正でなければならない")
    return (
        -supply_slope / demand_slope,
        (demand_intercept - supply_intercept) / demand_slope,
    )
