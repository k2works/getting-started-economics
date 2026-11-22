"""第 6 章のノートブック（セルの並び）。"""

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import code, markdown
from tools.notebooks.common import title

NAME = "ch06_elasticity_and_growth_rates"


def cells() -> list[NotebookNode]:
    """ノートブックのセルの並び。"""
    return [
        title(6, "指数・対数の微分と弾力性", "06-elasticity-and-growth-rates"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
a = 120            # 需要 q = a − b·p の切片（正）
b = 2              # 需要の傾き（正）
price = 40         # 弾力性を調べる価格（0 以上で、a − b·price > 0 になる範囲）
other_price = 30   # 弧弾力性を測る、もう 1 つの価格（price と違う値）
x = 0.1            # テイラー展開で近似する e^x の x
max_order = 4      # テイラー展開の次数の上限（1 以上の整数）
firms = 10         # 費用 C(q) = q² + 10q + 100 の企業の数（0 以上の整数）
supply_price = 30  # 総供給を調べる価格（0 以上）
""",
            parameters=True,
        ),
        markdown("## 需要の価格弾力性と収入"),
        code(
            """
from lib.chapter01.market import demand_quantity
from lib.chapter06.elasticity import (
    arc_price_elasticity,
    classify_elasticity,
    linear_demand_elasticity,
    point_price_elasticity,
    revenue_price_slope,
    sales_revenue,
)


def demand(p: float) -> float:
    return demand_quantity(p, a, b)


e = linear_demand_elasticity(price, a, b)
print(f"価格 {price} での需要量 {demand(price):.2f}")
print(f"点弾力性: 公式 {e:.4f}、数値微分 {point_price_elasticity(demand, price):.4f}"
      f"（{classify_elasticity(e)}）")
print(f"収入 {sales_revenue(demand, price):.2f}、"
      f"収入の価格についての傾き {revenue_price_slope(demand, price):.2f}")
arc = arc_price_elasticity(demand, price, other_price)
print(f"価格 {price} → {other_price} の弧弾力性 {arc:.4f}")
"""
        ),
        markdown("## e^x のテイラー展開"),
        code(
            """
import math

from lib.chapter06.growth import taylor_exp_approximation

print(f"本当の値 e^{x} = {math.exp(x):.9f}")
for order in range(max_order + 1):
    value = taylor_exp_approximation(x, order)
    print(f"{order} 次まで: {value:.9f}（誤差 {abs(value - math.exp(x)):.2e}）")
"""
        ),
        markdown("## 総供給"),
        code(
            """
from lib.chapter05.derivative import Polynomial
from lib.chapter06.supply import aggregate_supply_quantity

cost = Polynomial((100, 10, 1))
total = aggregate_supply_quantity(supply_price, [cost] * firms)
print(f"価格 {supply_price} での {firms} 社の総供給: {total:.2f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter06.plot import plot_elasticity_regions

plot_elasticity_regions(a, b)
"""
        ),
        code(
            """
from lib.chapter06.plot import plot_taylor_exp

plot_taylor_exp(-2, 2, list(range(1, max_order + 1)), 1)
"""
        ),
        markdown(
            """
## 試してみよう

- `price` を 20 にすると、弾力性は 0.5（inelastic）になります。収入は 40 のときと同じ
  1600 ですが、収入の傾きは −40 から +40 に変わります。値下げで収入が増えるのは、
  弾力的な側（中点の価格 30 より上）だけです
- `price = 30`・`other_price = 20` にすると、点弾力性はちょうど 1（unit elastic）で、
  収入の傾きは 0 です。収入 1800 が、この需要での最大です。弧弾力性は 0.7143 です
- `x = 1`・`max_order = 6` にすると、2 次までの誤差は 0.218、6 次までで 0.000226 です。
  x が大きいほど、同じ誤差にするのに、多くの項が要ります
- `firms = 20`・`supply_price = 15` にすると、総供給は 20 × (15 − 10) ÷ 2 = 50 です。
  `supply_price` を 10 以下にすると、どの企業も作らず 0 になります
"""
        ),
    ]
