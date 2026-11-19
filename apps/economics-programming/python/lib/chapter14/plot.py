"""AD-AS 分析とフィリップス曲線の図。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter13.islm import IsLmModel
from lib.chapter14.adas import (
    aggregate_demand,
    classical_supply,
    equilibrium_price_and_income,
)
from lib.chapter14.indicators import phillips_inflation

_PRICE_LEVELS = [round(0.6 + 0.05 * i, 2) for i in range(21)]
_UNEMPLOYMENT = [0.5 * i for i in range(21)]


def plot_adas(
    model: IsLmModel,
    full_employment_income: float,
    after: IsLmModel | None = None,
) -> Figure:
    """総需要曲線（AD）、古典派の総供給曲線（垂直）、均衡点を描く。

    after を渡すと、モデルが変わった後の総需要曲線と均衡点も重ねて描く。
    """
    fig, ax = plt.subplots()
    models = [(model, "")] + ([(after, " (after)")] if after is not None else [])
    for index, (current, suffix) in enumerate(models):
        ax.plot(
            [aggregate_demand(current, p) for p in _PRICE_LEVELS],
            _PRICE_LEVELS,
            label=f"AD{suffix}",
        )
        if index == 0:
            ax.plot(
                [full_employment_income] * 2,
                [_PRICE_LEVELS[0], _PRICE_LEVELS[-1]],
                label="AS (classical)",
            )
        price, income = equilibrium_price_and_income(
            current, lambda p: classical_supply(p, full_employment_income)
        )
        ax.plot(
            [income],
            [price],
            "o" if index == 0 else "s",
            color="black",
            label=f"Equilibrium{suffix}",
        )
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Price level P")
    ax.legend()
    plt.close(fig)
    return fig


def plot_phillips_curve(
    natural_rate: float,
    expected_inflation: float,
    slope: float,
    new_expected_inflation: float | None = None,
) -> Figure:
    """フィリップス曲線（失業率が高いほど、物価上昇率が低い）と、自然失業率の点を描く。

    new_expected_inflation を渡すと、期待物価上昇率が変わった後の曲線も重ねて描く。
    """
    fig, ax = plt.subplots()
    ax.plot(
        _UNEMPLOYMENT,
        [
            phillips_inflation(u, natural_rate, expected_inflation, slope)
            for u in _UNEMPLOYMENT
        ],
        label="Phillips curve",
    )
    ax.plot(
        [natural_rate], [expected_inflation], "o", color="black", label="Natural rate"
    )
    if new_expected_inflation is not None:
        ax.plot(
            _UNEMPLOYMENT,
            [
                phillips_inflation(u, natural_rate, new_expected_inflation, slope)
                for u in _UNEMPLOYMENT
            ],
            label="Phillips curve (after)",
        )
    ax.set_xlabel("Unemployment rate (%)")
    ax.set_ylabel("Inflation rate (%)")
    ax.legend()
    plt.close(fig)
    return fig
