"""IS-LM 分析（線形のモデル）。

財市場（IS 曲線）:
    Y = C + I + G、C = C0 + c(Y - T)、I = I0 - b·r
    より  (1 - c)·Y + b·r = C0 - c·T + I0 + G
貨幣市場（LM 曲線）:
    M / P = k·Y - h·r
"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure


@dataclass(frozen=True)
class IsLmModel:
    """IS-LM モデルの係数。既定値は、本書の標準のモデル。"""

    autonomous_consumption: float = 100  # C0: 基礎消費
    mpc: float = 0.8  # c: 限界消費性向
    tax: float = 50  # T: 定額税
    autonomous_investment: float = 140  # I0: 利子率が 0 のときの投資
    investment_sensitivity: float = 10  # b: 投資の利子率感応度
    government: float = 100  # G: 政府支出
    money_supply: float = 525  # M: 名目貨幣供給
    price_level: float = 1  # P: 物価水準
    money_income_sensitivity: float = 0.5  # k: 貨幣需要の所得感応度
    money_interest_sensitivity: float = 20  # h: 貨幣需要の利子率感応度
    interest_floor: float | None = None  # 利子率の下限（流動性のわな）

    def __post_init__(self) -> None:
        if not 0 <= self.mpc < 1:
            raise ValueError("限界消費性向は 0 以上 1 未満でなければならない")
        if self.investment_sensitivity <= 0:
            raise ValueError("投資の利子率感応度は正でなければならない")
        if self.money_interest_sensitivity <= 0:
            raise ValueError("貨幣需要の利子率感応度は正でなければならない")
        if self.money_income_sensitivity <= 0:
            raise ValueError("貨幣需要の所得感応度は正でなければならない")
        if self.price_level <= 0:
            raise ValueError("物価水準は正でなければならない")


def autonomous_spending(model: IsLmModel) -> float:
    """利子率と所得に依存しない支出 A = C0 - c·T + I0 + G。"""
    return (
        model.autonomous_consumption
        - model.mpc * model.tax
        + model.autonomous_investment
        + model.government
    )


def is_income(model: IsLmModel, rate: float) -> float:
    """IS 曲線: 利子率 r のときに財市場を均衡させる所得。"""
    return (autonomous_spending(model) - model.investment_sensitivity * rate) / (
        1 - model.mpc
    )


def lm_interest(model: IsLmModel, income: float) -> float:
    """LM 曲線: 所得 Y のときに貨幣市場を均衡させる利子率（下限があれば、それ以上）。"""
    rate = (
        model.money_income_sensitivity * income - model.money_supply / model.price_level
    ) / model.money_interest_sensitivity
    if model.interest_floor is not None:
        return max(rate, model.interest_floor)
    return rate


def solve_equilibrium(model: IsLmModel) -> tuple[float, float]:
    """IS 曲線と LM 曲線の交点（所得, 利子率）を、連立方程式として解く。

    利子率に下限があり、解がそれを下回るときは、利子率を下限に固定して、
    IS 曲線から所得を求める（流動性のわな: LM 曲線が水平になる）。
    """
    coefficients = np.array(
        [
            [1 - model.mpc, model.investment_sensitivity],
            [model.money_income_sensitivity, -model.money_interest_sensitivity],
        ]
    )
    constants = np.array(
        [autonomous_spending(model), model.money_supply / model.price_level]
    )
    income, rate = np.linalg.solve(coefficients, constants)
    if model.interest_floor is not None and rate < model.interest_floor:
        rate = model.interest_floor
        income = is_income(model, rate)
    return float(income), float(rate)


def _draw_curves(
    ax: Axes, model: IsLmModel, incomes: list[float], suffix: str, style: str
) -> None:
    is_rates = [
        (autonomous_spending(model) - (1 - model.mpc) * y)
        / model.investment_sensitivity
        for y in incomes
    ]
    lm_rates = [lm_interest(model, y) for y in incomes]
    income, rate = solve_equilibrium(model)
    ax.plot(incomes, is_rates, style, color="tab:blue", label=f"IS{suffix}")
    ax.plot(incomes, lm_rates, style, color="tab:orange", label=f"LM{suffix}")
    ax.plot([income], [rate], "o", color="black", label=f"Equilibrium{suffix}")


def plot_islm(model: IsLmModel, after: IsLmModel | None = None) -> Figure:
    """IS 曲線・LM 曲線・均衡点の図を返す。after があれば、政策後を破線で重ねる。"""
    base_income, _ = solve_equilibrium(model)
    incomes = [base_income * (0.7 + 0.01 * i) for i in range(61)]
    fig, ax = plt.subplots()
    _draw_curves(ax, model, incomes, suffix="", style="-")
    if after is not None:
        _draw_curves(ax, after, incomes, suffix=" (after)", style="--")
    ax.set_xlabel("Income (Y)")
    ax.set_ylabel("Interest rate (r)")
    ax.set_ylim(bottom=0)
    ax.legend()
    plt.close(fig)
    return fig
