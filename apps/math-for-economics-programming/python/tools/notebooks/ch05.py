"""第 5 章のノートブック（セルの並び）。"""

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import code, markdown
from tools.notebooks.common import title

NAME = "ch05_derivatives_and_profit_maximization"


def cells() -> list[NotebookNode]:
    """ノートブックのセルの並び。"""
    return [
        title(5, "1 変数の微分と利潤最大化", "05-derivatives-and-profit-maximization"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
fixed = 100      # 固定費用 c₀（正）
linear = 10      # 費用 C(q) = c₀ + c₁q + c₂q² の c₁（0 以上）
quadratic = 1    # c₂（正。MC が右上がりになる）
price = 50       # 価格（正）
step = 1e-5      # 数値微分の刻み幅 h（正。1e-13 などにすると、丸めの誤差が見える）
""",
            parameters=True,
        ),
        markdown("## 費用の諸概念と、利潤最大化"),
        code(
            """
from lib.chapter05.cost import (
    average_cost,
    competitive_profit,
    marginal_cost,
    minimum_average_cost,
    minimum_average_variable_cost,
    profit_maximizing_quantity,
)
from lib.chapter05.derivative import Polynomial, numerical_derivative

cost = Polynomial((fixed, linear, quadratic))
best = profit_maximizing_quantity(price, cost)
print(f"利潤最大の数量 {best:.2f}、利潤 {competitive_profit(price, cost, best):.2f}")
if best > 0:
    print(f"そこでの MC {marginal_cost(cost, best):.2f}、"
          f"AC {average_cost(cost, best):.2f}")
low_q, low_ac = minimum_average_cost(cost)
print(f"AC の最小（損益分岐点）: 数量 {low_q:.2f}、AC {low_ac:.2f}")
print(f"AVC の最小（操業停止点）: {minimum_average_variable_cost(cost)[1]:.2f}")
slope = numerical_derivative(cost, low_q, step)
print(f"数量 {low_q:.2f} での MC: 公式 {marginal_cost(cost, low_q):.6f}、"
      f"数値微分 {slope:.6f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter05.plot import plot_cost_curves

plot_cost_curves(cost, price, q_max=max(2 * low_q, 1.5 * best))
"""
        ),
        markdown(
            """
## 試してみよう

- `price` を 30（AC の最小値）にすると、数量 10 で利潤は 0.00 です（**損益分岐点**）。
  25 にすると、数量 7.5・利潤 −43.75 と赤字ですが、作らないとき（−100）より損が
  小さいので、生産を続けます
- `price` を 8（AVC の最小値 10 より安い）にすると、数量は 0、利潤は −100 です
  （**操業停止**）。図から、利潤最大の点と利潤の長方形が消えます
- `step` を `1e-13` にすると、数量 10 での数値微分は 29.558578 で、公式の 30 から
  ずれます（丸めの誤差）。`step = 1` でも 30.000000 のままです（2 次の費用では、
  中心差分に打ち切りの誤差がない）
- `fixed = 50`、`linear = 4`、`quadratic = 0.5`、`price = 20` は、記事の冒頭の図です。
  数量 16・利潤 78 です
"""
        ),
    ]
