"""第 8 章のノートブック（セルの並び）。"""

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import code, markdown
from tools.notebooks.common import title

NAME = "ch08_partial_derivatives_and_utility_maximization"


def cells() -> list[NotebookNode]:
    """ノートブックのセルの並び。"""
    return [
        title(
            8,
            "多変数の微分と効用最大化",
            "08-partial-derivatives-and-utility-maximization",
        ),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
price_x = 2     # 財 x の価格 p_x（正）
price_y = 5     # 財 y の価格 p_y（正）
income = 100    # 所得 m（0 以上）
share = 0.5     # コブ・ダグラス型 U = x^a·y^(1−a) の指数 a（0 < a < 1）
weight = 4      # 準線形効用 U = b·√x + y の重み b（正）
""",
            parameters=True,
        ),
        markdown("## コブ・ダグラス型の効用最大化"),
        code(
            """
from lib.chapter08.utility import (
    best_bundle_on_budget_line,
    cobb_douglas_demand,
    cobb_douglas_lagrange_multiplier,
    cobb_douglas_mrs,
    cobb_douglas_utility,
    quasilinear_demand,
    quasilinear_utility,
)

prices = [price_x, price_y]
x, y = cobb_douglas_demand(prices, income, share)
print(f"最適点（解析解）: x = {x:.3f}、y = {y:.3f}、効用 U = "
      f"{cobb_douglas_utility(x, y, share):.3f}")
print(f"限界代替率 {cobb_douglas_mrs(x, y, share):.3f}、価格比 {price_x / price_y:.3f}")
print(f"ラグランジュ乗数（1 円あたりの限界効用）"
      f"{cobb_douglas_lagrange_multiplier(prices, income, share):.4f}")
grid_x, grid_y = best_bundle_on_budget_line(
    lambda u, v: cobb_douglas_utility(u, v, share), prices, income, 2001
)
print(f"格子探索（2001 点）: x = {grid_x:.3f}、y = {grid_y:.3f}")
"""
        ),
        markdown("## 準線形効用 U = b·√x + y の最適点"),
        code(
            """
qx, qy = quasilinear_demand(prices, income, weight)
kind = "端点解（y = 0）" if qy == 0 else "内側の解"
print(f"x = {qx:.3f}、y = {qy:.3f}（{kind}）、効用 U = "
      f"{quasilinear_utility(qx, qy, weight):.3f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter08.plot import plot_income_expansion_paths, plot_utility_maximization

incomes = [income * k / 5 for k in range(1, 6)]
display(plot_utility_maximization(prices, income, share))
display(plot_income_expansion_paths(prices, incomes, share, weight))
"""
        ),
        markdown(
            """
## 試してみよう

- `share` を 0.3 にすると、最適点は x = 15.000、y = 14.000 に変わります（所得の 3 割を
  x に使う）。限界代替率は 0.400 のままで、価格比に等しいことを確かめてください
- `price_x` を 4 にすると、x は 12.500 に半減し、y は 10.000 のままです（a = 0.5 では、
  x への支出が所得の半分のまま）。ラグランジュ乗数は 0.1118 に下がります
- `income` を 200 にすると、コブ・ダグラス型の x は 25.000 から 50.000 に倍増しますが、
  準線形効用の x は 25.000 のままで、増えた所得はすべて y（10.000 → 30.000）に回ります
- `income` を 10 にすると、準線形効用の最適点は x = 5.000、y = 0.000 の**端点解**です
  （x = 25 を買えないので、所得をすべて x に使う）
"""
        ),
    ]
