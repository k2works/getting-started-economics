"""第 1 章のノートブック（セルの並び）。"""

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import code, markdown
from tools.notebooks.common import title

NAME = "ch01_linear_functions_and_markets"


def cells() -> list[NotebookNode]:
    """ノートブックのセルの並び。"""
    return [
        title(1, "1 次関数と市場メカニズム", "01-linear-functions-and-markets"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
demand_intercept = 120       # 需要 q = a − b·p の a（正）
demand_slope = 2             # 需要の傾き b（正）
supply_intercept = 0         # 供給 q = c + d·p の c（a より小さく）
supply_slope = 1             # 供給の傾き d（正）
supply_intercept_after = 20  # 豊作のあとの供給の切片（c より大きく）
""",
            parameters=True,
        ),
        markdown("## 均衡と余剰"),
        code(
            """
from lib.chapter01.market import (
    consumer_surplus,
    equilibrium,
    producer_surplus,
)

a, b = demand_intercept, demand_slope
c, d, c_after = supply_intercept, supply_slope, supply_intercept_after
eq = equilibrium(a, b, c, d)
print(f"均衡: 価格 {eq.price:.2f}、数量 {eq.quantity:.2f}、収入 {eq.revenue:.2f}")
cs, ps = consumer_surplus(eq.price, a, b), producer_surplus(eq.price, c, d)
print(f"消費者余剰 {cs:.2f}、生産者余剰 {ps:.2f}、総余剰 {cs + ps:.2f}")
after = equilibrium(a, b, c_after, d)
print(f"豊作のあと: 価格 {after.price:.2f}、数量 {after.quantity:.2f}、"
      f"収入 {after.revenue:.2f}（変化 {after.revenue - eq.revenue:+.2f}）")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter01.plot import plot_harvest_paradox, plot_market

display(plot_market(a, b, c, d))
display(plot_harvest_paradox(a, b, c, d, c_after))
"""
        ),
        markdown(
            """
## 試してみよう

- 既定の数字（需要 q = 120 − 2p、供給 q = p）では、均衡は価格 40・数量 40 です。
  `supply_slope` を 2 にすると、価格 30・数量 60 になり、総余剰は 1800 に増えます
- 豊作の前後で、収入は 1600 から 1777.78 に**増えます**。需要を
  `demand_intercept = 100`、`demand_slope = 0.5` にし、供給の切片を 10 → 40 にすると、
  収入は 4200 から 3200 に**減ります**（豊作貧乏）。需要が非弾力的なときです
- `supply_intercept` を `demand_intercept` 以上にすると、均衡がなく、`ValueError` に
  なります（価格も数量も正になる交点がない）
"""
        ),
    ]
