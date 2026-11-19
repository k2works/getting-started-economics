"""需要曲線の上の価格弾力性の図。縦軸が価格、横軸が数量。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter01.demand import choke_price, quantity_demanded

_STEPS = 10


def plot_elasticity_regions(intercept: float, slope: float) -> Figure:
    """需要曲線を、弾力的な部分（e > 1）と非弾力的な部分（e < 1）に分けて描く。

    直線の需要曲線では、価格弾力性 e = b × P ÷ Q は、真ん中の点（P = a / 2b）で
    1 になり、それより価格が高い部分は弾力的、低い部分は非弾力的になる。
    """
    top = choke_price(intercept, slope)
    middle = top / 2
    elastic = [middle + (top - middle) * i / _STEPS for i in range(_STEPS + 1)]
    inelastic = [middle * i / _STEPS for i in range(_STEPS + 1)]

    fig, ax = plt.subplots()
    ax.plot(
        [quantity_demanded(p, intercept, slope) for p in elastic],
        elastic,
        label="Elastic (e > 1)",
    )
    ax.plot(
        [quantity_demanded(p, intercept, slope) for p in inelastic],
        inelastic,
        label="Inelastic (e < 1)",
    )
    ax.plot(
        [quantity_demanded(middle, intercept, slope)],
        [middle],
        "o",
        color="black",
        label="Unit elasticity",
    )
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Price")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend()
    plt.close(fig)
    return fig
