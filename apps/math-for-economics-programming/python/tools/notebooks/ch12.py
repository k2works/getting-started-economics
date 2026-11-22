"""第 12 章のノートブック（セルの並び）。"""

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import code, markdown
from tools.notebooks.common import title

NAME = "ch12_recurrence_and_economic_growth"


def cells() -> list[NotebookNode]:
    """ノートブックのセルの並び。"""
    return [
        title(12, "漸化式と経済成長", "12-recurrence-and-economic-growth"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
a = 0.5          # 漸化式 x(t+1) = a·x(t) + b の係数 a（1 でもよい）
b = 6            # 定数項 b
x0 = 20          # 初期値 x(0)
saving = 0.3     # 貯蓄率 s（0 以上 1 以下）
alpha = 1 / 3    # 資本の分配率 α（0 より大きく 1 より小さい）
delta = 0.1      # 減耗率 δ（0 より大きく 1 以下）
k0 = 1           # 資本の初期値 k(0)（0 以上）
periods = 60     # 描く期数
""",
            parameters=True,
        ),
        markdown("## 1 次の漸化式: 閉じた解と反復"),
        code(
            """
from lib.chapter04.sequence import iterate_map
from lib.chapter12.recurrence import (
    classify_linear_recurrence,
    recurrence_closed_form,
    recurrence_half_life,
)

closed = [recurrence_closed_form(a, b, x0, t) for t in range(6)]
print("閉じた解 x(0)〜x(5):", [round(x, 4) for x in closed])
print("反復     x(0)〜x(5):", [round(x, 4) for x in iterate_map(a, b, x0, 5)])
print("ふるまい:", classify_linear_recurrence(a))
if 0 < abs(a) < 1:
    print(f"不動点 {b / (1 - a):.4f}、差が半分になる期数 {recurrence_half_life(a):.2f}")
"""
        ),
        markdown("## ソロー・モデル: 定常状態・収束の速さ・黄金律"),
        code(
            """
from lib.chapter12.solow import (
    solow_capital_path,
    solow_convergence_factor,
    solow_steady_state_capital,
    solow_steady_state_consumption,
)

steady = solow_steady_state_capital(saving, alpha, delta)
print(f"定常状態の資本 k* = {steady:.3f}、生産 y* = {steady**alpha:.3f}")
consumption = solow_steady_state_consumption(saving, alpha, delta)
print(f"定常状態の消費 c* = {consumption:.3f}")
gold = solow_steady_state_consumption(alpha, alpha, delta)
print(f"黄金律（s = α = {alpha:.3f}）の消費 = {gold:.3f}")
factor = solow_convergence_factor(alpha, delta)
print(f"定常状態の近くで、差は毎期 {factor:.4f} 倍、"
      f"半分になるまで {recurrence_half_life(factor):.2f} 期")
path = solow_capital_path(k0, saving, alpha, delta, periods)
print(f"k(0) = {k0} から {periods} 期後の資本 = {path[-1]:.3f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter12.plot import (
    plot_golden_rule,
    plot_linear_recurrence_paths,
    plot_solow_convergence,
)

display(plot_linear_recurrence_paths([a], b, x0, 20))
display(plot_solow_convergence([k0, 2 * steady], saving, alpha, delta, periods))
display(plot_golden_rule(alpha, delta, [s / 100 for s in range(1, 100)]))
"""
        ),
        markdown(
            """
## 試してみよう

- `a = -0.5`・`x0 = 0` にすると、閉じた解は 0, 6, 3, 4.5, 3.75, 4.125 と、不動点 4 の
  上下を行き来します（`converges with oscillation`）
- `a = 1.1`・`b = -2`・`x0 = 3` では、3, 1.3, -0.57, … と、不動点 20 から
  離れていきます（`diverges`）
- `saving = 0.6` にすると、定常状態の資本は 5.196 から 14.697 に増えますが、消費は
  1.212 から 0.980 に**減ります**（黄金律 s = α = 0.333 を越えたため）
- `delta = 0.05` にすると、定常状態の資本は 14.697 に増え、差が半分になるまでの期数は
  10.05 から 20.45 に延びます（収束が遅くなる）
"""
        ),
    ]
