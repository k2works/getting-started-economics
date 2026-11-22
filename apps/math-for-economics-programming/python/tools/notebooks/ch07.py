"""第 7 章のノートブック（セルの並び）。"""

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import code, markdown
from tools.notebooks.common import title

NAME = "ch07_vectors_and_budget_constraint"


def cells() -> list[NotebookNode]:
    """ノートブックのセルの並び。"""
    return [
        title(7, "ベクトルと予算制約", "07-vectors-and-budget-constraint"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
price1 = 2            # 財 1 の価格（正）
price2 = 3            # 財 2 の価格（正）
income = 60           # 所得（0 以上）
bundle = [15, 10]     # 調べる財の組合せ (x1, x2)（0 以上）
wage = 10             # 労働と余暇: 時給（正）
new_wage = 15         # 時給が変わった後（図の破線）
total_hours = 24      # 1 日の時間
nonlabor_income = 0   # 非労働所得（0 以上）
leisure = 16          # 余暇の時間（0 以上、total_hours 以下）
""",
            parameters=True,
        ),
        markdown("## 予算制約と、価格ベクトル"),
        code(
            """
from lib.chapter07.budget import budget_expenditure, budget_intercepts, budget_status
from lib.chapter07.vectors import vector_angle_degrees, vector_dot

prices = [price1, price2]
spending = budget_expenditure(prices, bundle)
status = budget_status(prices, bundle, income)
print(f"支出 p·x = {spending:.2f}（所得 {income}）: {status}")
x1_end, x2_end = budget_intercepts(prices, income)
print(f"予算線の切片: 財 1 だけなら {x1_end:.2f}、財 2 だけなら {x2_end:.2f}")
along = [x1_end, -x2_end]  # 予算線に沿った向き（切片から切片へ）
print(f"価格ベクトルと予算線の向きの内積 {vector_dot(prices, along):.2f}、"
      f"なす角 {vector_angle_degrees(prices, along):.1f} 度")
"""
        ),
        markdown("## 労働と余暇"),
        code(
            """
from lib.chapter07.budget import consumption_given_leisure, full_income

whole = full_income(wage, total_hours, nonlabor_income)
print(f"完全所得（全部の時間を働く）: {whole:.2f}")
consumption = consumption_given_leisure(leisure, wage, total_hours, nonlabor_income)
work = total_hours - leisure
print(f"余暇 {leisure} 時間（労働 {work} 時間）の消費: {consumption:.2f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter07.plot import plot_budget_set, plot_labor_leisure

plot_budget_set(prices, income, [bundle])
"""
        ),
        code(
            """
plot_labor_leisure(wage, new_wage, total_hours, nonlabor_income)
"""
        ),
        markdown(
            """
## 試してみよう

- `bundle = [12, 13]` にすると、支出は 63.00 で `outside`（予算外）です。
  `[10, 12]` なら 56.00 で `inside` です
- `price1 = 4` にすると、財 1 の切片が 15.00 に半分になり、`[15, 10]` は支出 90.00 で
  予算外になります。価格ベクトルと予算線の向きのなす角は、価格を変えても
  90.0 度のままです（価格ベクトルは、予算線の**法線ベクトル**）
- `nonlabor_income = 40` にすると、完全所得は 280.00、余暇 16 時間の消費は 120.00 です。
  図では、2 本の予算線が、余暇 24 時間・消費 40 の点で交わります
"""
        ),
    ]
