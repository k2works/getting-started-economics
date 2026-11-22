"""第 2 章のノートブック（セルの並び）。"""

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import code, markdown
from tools.notebooks.common import title

NAME = "ch02_quadratics_monopoly_and_oligopoly"


def cells() -> list[NotebookNode]:
    """ノートブックのセルの並び。"""
    return [
        title(2, "2 次関数と独占・寡占市場", "02-quadratics-monopoly-and-oligopoly"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
demand_intercept = 100  # 逆需要 P = a − b·Q の a（費用より大きく）
demand_slope = 1        # 逆需要の傾き b（正）
unit_cost = 20          # 1 単位あたりの費用 c（0 以上、a より小さく）
firms = 2               # クールノー競争の企業の数 n（1 以上の整数）
""",
            parameters=True,
        ),
        markdown("## 独占・完全競争・クールノー均衡"),
        code(
            """
from lib.chapter02.monopoly import (
    competitive_outcome,
    cournot_outcome,
    monopoly_deadweight_loss,
    monopoly_outcome,
)
from lib.chapter02.quadratic import complete_the_square

a, b, c = demand_intercept, demand_slope, unit_cost
coef, h, k = complete_the_square(-b, a - c, 0)
print(f"利潤 π(Q) = {coef:g}·(Q − {h:.2f})² + {k:.2f}")
for name, result in [
    ("独占", monopoly_outcome(a, b, c)),
    ("完全競争", competitive_outcome(a, b, c)),
    (f"クールノー（{firms} 社）", cournot_outcome(firms, a, b, c)),
]:
    print(f"{name}: 数量 {result.quantity:.2f}、価格 {result.price:.2f}、"
          f"利潤 {result.profit:.2f}")
print(f"独占の死荷重 {monopoly_deadweight_loss(a, b, c):.2f}")
print(f"クールノーの 1 社の数量 {cournot_outcome(firms, a, b, c).quantity / firms:.2f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter02.plot import plot_cournot_convergence, plot_monopoly_profit

display(plot_monopoly_profit(a, b, c))
display(plot_cournot_convergence(a, b, c, max(firms, 10)))
"""
        ),
        markdown(
            """
## 試してみよう

- `demand_slope` を 2 にすると、独占の数量は 20、利潤は 800 に半減しますが、
  **価格は 60 のまま**です（P* = (a + c) ÷ 2 に、b が入らない）
- `unit_cost` を 40 に上げると、独占の価格は 70 に上がります。費用の上がり分 20 の
  **半分**だけが、価格に転嫁されます
- `firms` を 1 にすると、クールノー均衡は独占と同じ（数量 40・価格 60）です。
  `firms = 4` では価格 36、`firms = 19` では価格 24 で、費用 20 に近づきます
"""
        ),
    ]
