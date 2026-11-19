"""効用最大化と利潤最大化の図。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from lib.chapter04.cost import average_cost, average_variable_cost, marginal_cost
from lib.chapter04.utility import cobb_douglas_utility
from lib.chapter10.optimization import maximize_utility, profit_maximizing_quantity

_POINTS = 50


def plot_utility_maximization(
    price_x: float, price_y: float, income: float, alpha: float = 0.5
) -> Figure:
    """予算線と、最適点を通る無差別曲線を描く。無差別曲線は、最適点で予算線に接する。"""
    best_x, best_y = maximize_utility(price_x, price_y, income, alpha)
    utility = cobb_douglas_utility(best_x, best_y, alpha)
    max_x = income / price_x
    xs = [max_x * i / _POINTS for i in range(1, _POINTS + 1)]
    # 無差別曲線 U = x^a · y^(1-a) を y について解く
    curve = [(utility / x**alpha) ** (1 / (1 - alpha)) for x in xs]

    fig, ax = plt.subplots()
    ax.plot([0, max_x], [income / price_y, 0], label="Budget line")
    ax.plot(xs, curve, label="Indifference curve")
    ax.plot([best_x], [best_y], "o", color="black", label="Optimum")
    ax.set_xlabel("Good x")
    ax.set_ylabel("Good y")
    ax.set_xlim(0, max_x * 1.1)
    ax.set_ylim(0, income / price_y * 1.5)
    ax.legend()
    plt.close(fig)
    return fig


def plot_profit_maximization(price: float, max_quantity: float = 6) -> Figure:
    """限界費用・平均可変費用・平均費用と価格の線、利潤を最大にする生産量と利潤を描く。

    利潤は、(価格 - 平均費用) × 生産量の長方形。価格が操業停止点を下回れば、描かない。
    """
    quantities = [max_quantity * i / 60 for i in range(1, 61)]
    best = profit_maximizing_quantity(price)

    fig, ax = plt.subplots()
    if best > 0:
        cost = average_cost(best)
        ax.add_patch(
            Rectangle(
                (0, cost),
                best,
                price - cost,
                alpha=0.3,
                color="tab:green",
                label="Profit",
            )
        )
    ax.plot(quantities, [marginal_cost(q) for q in quantities], label="MC")
    ax.plot(quantities, [average_variable_cost(q) for q in quantities], label="AVC")
    ax.plot(quantities, [average_cost(q) for q in quantities], label="AC")
    ax.plot(
        [quantities[0], quantities[-1]],
        [price, price],
        "--",
        color="gray",
        label="Price",
    )
    if best > 0:
        ax.plot([best], [price], "o", color="black", label="Optimum")
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Cost per unit")
    ax.set_ylim(0, 30)
    ax.legend()
    plt.close(fig)
    return fig
