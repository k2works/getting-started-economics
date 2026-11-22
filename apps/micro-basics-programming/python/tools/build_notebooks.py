"""Jupyter Notebook（notebooks/）を、書き出す。

    uv run python -m tools.build_notebooks

各ノートブックは、(1) 説明、(2) 数字を書き換えるセル（Parameters）、(3) 各章の関数を
呼んで、結果を表示するセル、(4) 図、(5) 「試してみよう」の順にそろえる。
`試してみよう` に書く数値は、実際に実行して確かめた値だけにする。
"""

from collections.abc import Callable
from pathlib import Path

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import code, markdown, write

NOTEBOOKS_DIR = Path(__file__).resolve().parents[1] / "notebooks"
HOW_TO_RUN = (
    "**使い方**: 「Parameters」のセルの数字を書き換えて、上から順に実行します"
    "（メニューの Run → Run All Cells）。数字を変えるたびに、結果と図が変わります。\n\n"
    "起動: アプリのディレクトリで `uv run --with jupyterlab jupyter lab notebooks/` "
    "を実行します。"
)


def ch09_surplus_and_tax() -> list[NotebookNode]:
    return [
        markdown(
            "# 第 9 章 余剰分析と課税: 数字を変えて確かめる\n\n"
            + HOW_TO_RUN
            + "\n\n記事: `docs/article/micro-basics-programming/09-surplus-and-tax.md`"
        ),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
demand_intercept = 100  # 需要 Q = a + s_d·P の切片 a
demand_slope = -1       # 需要の傾き s_d（負）
supply_intercept = -10  # 供給 Q = c + s_s·P の切片 c
supply_slope = 1        # 供給の傾き s_s（正）
tax = 9                 # 従量税（売り手に、1 単位あたり課す）
""",
            parameters=True,
        ),
        markdown("## 均衡と、課税のあとの結果"),
        code(
            """
from lib.chapter08.market import LinearMarket, equilibrium
from lib.chapter09.surplus import tax_equilibrium, tax_incidence

market = LinearMarket(demand_intercept, demand_slope, supply_intercept, supply_slope)
price, quantity = equilibrium(market)
print(f"課税前の均衡: 価格 {price:.2f}、数量 {quantity:.2f}")

result = tax_equilibrium(market, tax)
print(f"課税後: 買い手の価格 {result.buyer_price:.2f}、売り手の手取り "
      f"{result.seller_price:.2f}、数量 {result.quantity:.2f}")
print(f"税収 {result.tax_revenue:.2f}、死荷重 {result.deadweight_loss:.2f}")
buyer, seller = tax_incidence(market, tax)
print(f"税の負担: 買い手 {buyer:.2f}、売り手 {seller:.2f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter09.plot import plot_tax

plot_tax(market, tax, q_max=100, p_max=100)
"""
        ),
        markdown(
            """
## 試してみよう

- `tax` を 0 にすると、税収も死荷重も 0 になります。18 にすると、死荷重は 81 です
  （9 のときの 20.25 の 4 倍。死荷重は、税額の **2 乗**に比例します）
- 需要を急にする（`demand_intercept = 72.5`、`demand_slope = -0.5`）と、買い手が多く
  負担し（6.0 対 3.0）、死荷重は 13.5 に小さくなります。需要が**非弾力的**なほど、
  税の死荷重は小さくなります
- 供給を急にする（`supply_intercept = 17.5`、`supply_slope = 0.5`）と、売り手が多く
  負担します（3.0 対 6.0）。**弾力性の小さい側**が、多く負担します
"""
        ),
    ]


def _title(number: int, title: str, article: str) -> NotebookNode:
    """先頭の説明のセル（章のタイトル、使い方、記事のパス）。"""
    return markdown(
        f"# 第 {number} 章 {title}: 数字を変えて確かめる\n\n"
        + HOW_TO_RUN
        + f"\n\n記事: `docs/article/micro-basics-programming/{article}.md`"
    )


def ch01_utility_and_indifference_curves() -> list[NotebookNode]:
    return [
        _title(1, "効用と無差別曲線", "01-utility-and-indifference-curves"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
a = 1.0          # 効用 U = x^a · y^b の、x のべき指数
b = 1.0          # y のべき指数
x = 20           # 調べる点の x（財 x の量）
y = 40           # 調べる点の y（財 y の量）
level = 800      # 無差別曲線の効用の水準
x_at = 10        # この x のとき、水準 level の曲線の y を求める
levels = [400, 800, 1200]  # 図に描く効用の水準
x_min = 5        # 図の x の範囲
x_max = 80
""",
            parameters=True,
        ),
        markdown("## 効用と限界代替率"),
        code(
            """
from lib.chapter01.utility import (
    cobb_douglas_utility,
    indifference_curve_y,
    marginal_rate_of_substitution,
)

utility = cobb_douglas_utility(x, y, a, b)
print(f"点 ({x}, {y}) の効用: {utility:.2f}")
mrs = marginal_rate_of_substitution(x, y, a, b)
print(f"点 ({x}, {y}) の限界代替率（MRS）: {mrs:.4f}")
curve_y = indifference_curve_y(level, x_at, a, b)
print(f"効用 {level} の曲線の、x = {x_at} のときの y: {curve_y:.2f}")
"""
        ),
        markdown(
            "## 図\n\n無差別曲線の図は、U = x·y（a = b = 1）で描きます。"
            "a・b は、上の計算にだけ効きます。"
        ),
        code(
            """
from lib.chapter01.plot import plot_indifference_curves

plot_indifference_curves(levels, x_min, x_max)
"""
        ),
        code(
            """
from lib.chapter01.plot import plot_special_utilities

plot_special_utilities()
"""
        ),
        markdown(
            """
## 試してみよう

- `a = 2` にすると、(20, 40) の効用は 16000、MRS は 4.0 になります。MRS は、
  **a ÷ b と、y ÷ x** で決まります
- `a = 0.5`、`b = 0.5` にすると、効用は約 28.28 ですが、MRS は 2.0 のまま変わりません
  （a ÷ b が、1 のままだから）
- `x = 40`、`y = 20` にすると、MRS は 0.5 に下がります。右へ進むほど MRS が小さい
  （逓減する）ので、曲線は**原点に凸**です
- `a = 2` で `x_at = 10` にすると、曲線の y は 8.0 です（a = 1 のときは 80）
"""
        ),
    ]


def ch02_budget_and_optimal_choice() -> list[NotebookNode]:
    return [
        _title(2, "予算制約と最適消費", "02-budget-and-optimal-choice"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
income = 80     # 所得
px = 2          # 財 x の価格
py = 1          # 財 y の価格
a = 1.0         # 効用 U = x^a · y^b の、x のべき指数
b = 1.0         # y のべき指数
levels = [400, 800, 1200]  # 図に描く無差別曲線の効用の水準
x_max = 45      # 図の x の範囲
""",
            parameters=True,
        ),
        markdown("## 予算線と最適消費点"),
        code(
            """
from lib.chapter01.utility import cobb_douglas_utility
from lib.chapter02.budget import (
    budget_intercepts,
    budget_slope,
    optimal_bundle,
    optimal_bundle_by_grid,
    tangency_gap,
)

print(f"予算線の傾き: {budget_slope(px, py):.2f}")
x_intercept, y_intercept = budget_intercepts(income, px, py)
print(f"予算線の切片: x = {x_intercept:.2f}、y = {y_intercept:.2f}")
x, y = optimal_bundle(income, px, py, a, b)
print(f"最適消費点: ({x:.2f}, {y:.2f})、効用 {cobb_douglas_utility(x, y, a, b):.2f}")
print(f"接点の条件（MRS − 価格比）: {tangency_gap(x, y, px, py, a, b):.6f}")
grid_x, grid_y = optimal_bundle_by_grid(income, px, py, a, b)
print(f"格子点の探索: ({grid_x:.2f}, {grid_y:.2f})")
"""
        ),
        markdown(
            "## 図\n\n図は、U = x·y（a = b = 1）で描きます。"
            "a・b は、上の計算にだけ効きます。"
        ),
        code(
            """
from lib.chapter02.plot import plot_optimal_choice

plot_optimal_choice(income, px, py, levels, x_max)
"""
        ),
        markdown(
            """
## 試してみよう

- `px = 1` にすると、最適点は (40.0, 40.0) になります。x は 20 から 40 に増えますが、
  y は 40 のまま変わりません（コブ・ダグラス型は、所得の半分を、いつも財 y に使う）
- `income = 160` にすると、(40.0, 80.0) と、**どちらも 2 倍**になります
- `a = 2` にすると、(26.67, 26.67) になります。x の効用への寄与が大きいので、
  x に使う所得の割合が増えます（a ÷ (a + b) = 2/3）
- `b = 3` にすると、(10.0, 60.0) になります。y に使う割合が 3/4 に増えるからです
"""
        ),
    ]


def ch03_demand_curve_and_elasticity() -> list[NotebookNode]:
    return [
        _title(3, "需要曲線と弾力性", "03-demand-curve-and-elasticity"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
income = 80                # 消費者の所得
incomes = [80, 160]        # 市場需要・需要曲線の図で足し合わせる、消費者の所得
px = 2                     # 財 x の価格
py = 1                     # 財 y の価格
demand_intercept = 100     # 直線の需要 Q = a + s·P の切片 a
demand_slope = -1          # 直線の需要の傾き s（負）
linear_price = 50          # 弾力性を調べる価格
price_min = 0.25           # 図の価格の範囲（最小）
price_step = 0.125         # 価格の刻み
price_points = 30          # 価格の点の数
income_path = [20, 40, 80, 120, 160]  # 所得消費曲線の図の所得
""",
            parameters=True,
        ),
        markdown("## 需要量と弾力性"),
        code(
            """
from lib.chapter03.demand import (
    classify_by_income_elasticity,
    demand_x,
    elasticity_type,
    income_elasticity,
    market_demand,
    price_elasticity,
    price_elasticity_linear,
)

print(f"Px = {px} の需要量: {demand_x(income, px, py):.2f}")
print(f"市場需要（所得 {incomes}）: {market_demand(incomes, px, py):.2f}")
e = price_elasticity_linear(demand_intercept, demand_slope, linear_price)
print(f"直線の需要の価格弾力性（P = {linear_price}）: {e:.4f}、{elasticity_type(e)}")
e = price_elasticity(lambda p: demand_x(income, p, py), px)
print(f"U = x·y の需要の価格弾力性: {e:.4f}")
e = income_elasticity(lambda m: demand_x(m, px, py), income)
print(f"U = x·y の所得弾力性: {e:.4f}、{classify_by_income_elasticity(e)}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter03.plot import plot_demand_curve

prices = [price_min + price_step * i for i in range(price_points)]
plot_demand_curve(incomes, prices, py)
"""
        ),
        code(
            """
from lib.chapter03.plot import plot_income_consumption

plot_income_consumption(income_path, px, py)
"""
        ),
        markdown(
            """
## 試してみよう

- `px = 4` にすると、需要量は 10.0 です（`px = 2` の 20 の半分）
- `incomes = [40, 120, 80]` にすると、市場需要は 60.0 です。消費者が増えると、
  需要曲線は、**横に足されて**右へ動きます
- `linear_price` を 10 にすると、弾力性は約 0.11（非弾力的）、90 にすると 9.0
  （弾力的）です。同じ直線でも、**高い価格ほど弾力的**です
- `demand_slope = -2`、`linear_price = 25` にすると、弾力性は 1.0（単位弾力的）です。
  傾きが違うと、単位弾力的になる価格も変わります
"""
        ),
    ]


def ch04_slutsky_decomposition_and_goods() -> list[NotebookNode]:
    return [
        _title(4, "スルツキー分解と財の分類", "04-slutsky-decomposition-and-goods"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
income = 80      # 所得
px_old = 2       # 財 x の元の価格
px_new = 0.5     # 財 x の新しい価格（値下げ。px_old より小さくする）
py = 1           # 財 y の価格
x_max = 100      # 図の x の範囲
py_values = [0.5, 1, 1.5, 2, 2.5, 3, 4]  # 交差価格の図で動かす、財 y の価格
""",
            parameters=True,
        ),
        markdown("## 代替効果と所得効果"),
        code(
            """
from lib.chapter04.slutsky import classify_by_effects, slutsky_decomposition

r = slutsky_decomposition(income, px_old, px_new, py)
print(f"元の点 A: ({r.original[0]:.2f}, {r.original[1]:.2f})")
print(f"代替効果のあとの点 B: ({r.substitution[0]:.2f}, {r.substitution[1]:.2f})")
print(f"最終の点 C: ({r.final[0]:.2f}, {r.final[1]:.2f})")
print(f"代替効果 {r.substitution_effect:.4f}、所得効果 {r.income_effect:.4f}、"
      f"価格効果 {r.price_effect:.4f}")
kind = classify_by_effects(r.substitution_effect, r.income_effect)
print(f"財の種類: {kind}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter04.plot import plot_slutsky

plot_slutsky(income, px_old, px_new, py, x_max)
"""
        ),
        code(
            """
from lib.chapter04.plot import plot_cross_price

plot_cross_price(income, px_old, py_values)
"""
        ),
        markdown(
            """
## 試してみよう

- `px_new = 1` にすると、代替効果は約 8.28、所得効果は約 11.72、価格効果は 20.0 です。
  値下げが小さいと、どちらの効果も小さくなります
- `px_new = 0.25` にすると、価格効果は 140.0（代替効果 約 36.57 と、所得効果 約 103.43）
  です。値下げが大きいほど、所得効果が、大きく効きます
- `income = 160` にすると、代替効果は 40.0、所得効果は 80.0 で、どちらも 2 倍です
- `px_new` を `px_old` より大きくする（値上げ）と、エラーになります。この関数は、
  値下げを前提にしています
"""
        ),
    ]


def ch05_cost_curves() -> list[NotebookNode]:
    return [
        _title(5, "費用曲線", "05-cost-curves"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
cubic = 1        # 可変費用 VC = cubic·q³ + quadratic·q² + linear·q の、q³ の係数
quadratic = -6   # q² の係数
linear = 15      # q の係数
fixed = 32       # 固定費用
q = 4            # 調べる生産量
q_max = 8        # 図の q の範囲
y_max = 40       # 図の y の範囲
""",
            parameters=True,
        ),
        markdown("## 費用と最低点"),
        code(
            """
from lib.chapter05.cost import (
    CostCurve,
    average_cost,
    average_variable_cost,
    cost_minima,
    marginal_cost,
    total_cost,
)

curve = CostCurve(cubic=cubic, quadratic=quadratic, linear=linear, fixed=fixed)
print(f"q = {q}: 総費用 {total_cost(curve, q):.2f}、限界費用 "
      f"{marginal_cost(curve, q):.2f}")
print(f"q = {q}: 平均費用 {average_cost(curve, q):.2f}、平均可変費用 "
      f"{average_variable_cost(curve, q):.2f}")
for name, (q_min, value) in cost_minima(curve).items():
    print(f"{name} の最低点: q = {q_min:.3f}、値 {value:.3f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter05.plot import plot_cost_curves

plot_cost_curves(curve, q_max, y_max)
"""
        ),
        code(
            """
from lib.chapter05.plot import plot_total_cost

plot_total_cost(curve, q_max)
"""
        ),
        markdown(
            """
## 試してみよう

- `fixed = 0` にすると、平均費用の最低点が、平均可変費用の最低点（q = 3、値 6）と
  重なります。平均費用と平均可変費用の差は、**固定費用 ÷ q** だからです
- `fixed = 64` にすると、平均費用の最低点は、q ≈ 4.547、値 ≈ 22.468 に動きます。
  限界費用（q = 2、値 3）と平均可変費用（q = 3、値 6）の最低点は、変わりません
  （固定費用は、これらに入らない）
- `linear = 21` にすると、3 つの最低点の値が 9・12・21 に上がり、位置（q = 2・3・4）は
  変わりません
"""
        ),
    ]


def ch06_production_function_and_cost_minimization() -> list[NotebookNode]:
    return [
        _title(
            6,
            "生産関数と費用最小化",
            "06-production-function-and-cost-minimization",
        ),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
quantity = 10    # 生産量（これを作る、最小の費用を求める）
w = 1            # 労働の賃金
r = 4            # 資本の価格
alpha = 0.5      # 生産関数 Q = L^α · K^β の、労働のべき指数
beta = 0.5       # 資本のべき指数
labor = 20       # 限界生産性を調べる点の労働
capital = 5      # 限界生産性を調べる点の資本
levels = [5, 10, 15]  # 図に描く等量曲線の生産量
l_max = 80       # 限界生産性の図の、労働の範囲
""",
            parameters=True,
        ),
        markdown("## 費用最小の投入"),
        code(
            """
from lib.chapter06.production import (
    cost_minimizing_inputs,
    marginal_product_capital,
    marginal_product_labor,
    minimum_cost,
    mrts,
    production,
)

print(f"(L, K) = ({labor}, {capital}) の生産量: "
      f"{production(labor, capital, alpha, beta):.4f}")
print(f"労働の限界生産性: {marginal_product_labor(labor, capital, alpha, beta):.4f}、"
      f"資本の限界生産性: {marginal_product_capital(labor, capital, alpha, beta):.4f}")
best_l, best_k = cost_minimizing_inputs(quantity, w, r, alpha, beta)
print(f"費用最小の投入: L = {best_l:.4f}、K = {best_k:.4f}")
print(f"最小費用: {minimum_cost(quantity, w, r, alpha, beta):.4f}")
print(f"技術的限界代替率: {mrts(best_l, best_k, alpha, beta):.4f}、"
      f"価格比 w ÷ r: {w / r:.4f}")
"""
        ),
        markdown(
            "## 図\n\n等量曲線と等費用線の図は、Q = √(L·K)（α = β = 0.5）で描きます。"
            "α・β は、上の計算にだけ効きます。"
        ),
        code(
            """
from lib.chapter06.plot import plot_cost_minimization

plot_cost_minimization(levels, quantity, w, r)
"""
        ),
        code(
            """
from lib.chapter06.plot import plot_marginal_product

plot_marginal_product(capital, l_max)
"""
        ),
        markdown(
            """
## 試してみよう

- `w = 4`、`r = 1` にすると、投入は (L, K) = (5, 20) に逆転します。高い投入を減らし、
  安い投入を増やすからです
- `quantity = 20` にすると、最小費用は 80.0 で、10 のとき（40.0）の 2 倍です。
  `quantity = 40` なら 160.0 で、費用は、生産量に比例します
- `alpha = 0.3`、`beta = 0.5`（べき指数の和が 1 未満）にすると、最小費用は、
  `quantity = 10` で約 81.96、`quantity = 20` で約 194.93 です。生産量を 2 倍に
  すると、費用は **2 倍より多く**増えます（規模に関して収穫逓減）
- `alpha = 0.7`、`beta = 0.7`（和が 1 より大きい）にすると、`quantity = 10` で
  約 20.72、`quantity = 20` で約 33.99 です。費用は **2 倍より少なく**しか増えません
  （規模に関して収穫逓増）
"""
        ),
    ]


def ch07_profit_maximization_and_supply() -> list[NotebookNode]:
    return [
        _title(7, "利潤最大化と供給曲線", "07-profit-maximization-and-supply"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
cubic = 1        # 可変費用 VC = cubic·q³ + quadratic·q² + linear·q の、q³ の係数
quadratic = -6   # q² の係数
linear = 15      # q の係数
fixed = 32       # 固定費用
price = 30       # 市場の価格
firms = 2        # 同じ費用の企業の数
tax = 6          # 従量税（1 単位あたり）
rate = 0.2       # 従価税の税率
q_max = 8        # 供給曲線の図の、q の範囲
y_max = 40       # 供給曲線の図の、y の範囲
tax_q_min = 3    # 課税の図の、q の範囲
tax_q_max = 6
""",
            parameters=True,
        ),
        markdown("## 利潤最大の生産量と供給"),
        code(
            """
from lib.chapter05.cost import CostCurve
from lib.chapter07.supply import (
    break_even_price,
    free_entry_price,
    market_supply,
    profit,
    profit_maximizing_output,
    shutdown_price,
    supply_price_ad_valorem,
    supply_price_unit_tax,
)

curve = CostCurve(cubic=cubic, quadratic=quadratic, linear=linear, fixed=fixed)
q = profit_maximizing_output(curve, price)
print(f"P = {price}: 利潤最大の生産量 {q:.4f}、利潤 {profit(curve, price, q):.4f}")
print(f"損益分岐点 {break_even_price(curve):.4f}、操業停止点 "
      f"{shutdown_price(curve):.4f}")
print(f"市場供給（{firms} 社）: {market_supply([curve] * firms, price):.4f}")
print(f"従量税 {tax}: q = 5 を供給する価格 "
      f"{supply_price_unit_tax(curve, 5, tax):.4f}")
print(f"従価税 {rate:.0%}: q = 5 を供給する価格 "
      f"{supply_price_ad_valorem(curve, 5, rate):.4f}")
print(f"自由参入の長期の価格: {free_entry_price(curve):.4f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter07.plot import plot_supply

plot_supply(curve, price, q_max, y_max)
"""
        ),
        code(
            """
from lib.chapter07.plot import plot_tax_supply

plot_tax_supply(curve, tax, rate, tax_q_min, tax_q_max)
"""
        ),
        markdown(
            """
## 試してみよう

- `price = 10` にすると、生産量は約 3.53、利潤は約 −18.87（赤字）です。固定費用 32 の
  損失（作らない場合）より小さいので、作ります。`price = 5` なら、生産量は 0.0 です
  （作らない。図は、生産量が正のときだけ描けるので、図のセルは、エラーになります）
- `fixed = 0` にすると、損益分岐点が操業停止点（6.0）と同じになります。固定費用がない
  ので、赤字になる価格は、そのまま、作らない価格です
- `fixed = 64` にすると、損益分岐点は約 22.47、操業停止点は 6.0 のままです。`price = 30`
  での利潤は 36.0 に減ります
- `firms = 3` にすると、`price = 30` の市場供給は 15.0 です（5 × 3）
- `tax = 12` にすると、q = 5 を供給する価格は 42 です（30 + 12）
"""
        ),
    ]


def ch08_market_equilibrium_and_adjustment() -> list[NotebookNode]:
    return [
        _title(8, "市場均衡と調整過程", "08-market-equilibrium-and-adjustment"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
demand_intercept = 100  # 需要 Q = a + s_d·P の切片 a
demand_slope = -1       # 需要の傾き s_d（負）
supply_intercept = -10  # 供給 Q = c + s_s·P の切片 c
supply_slope = 1        # 供給の傾き s_s（正）
price0 = 80             # 調整の出発点の価格
quantity0 = 0           # 調整の出発点の数量
speed = 0.25            # 調整の速さ
steps = 12              # 調整の回数
delta = 20              # 需要・供給の動き（右へ + 、左へ −）
q_max = 100             # 図の数量の範囲
p_max = 100             # 図の価格の範囲
""",
            parameters=True,
        ),
        markdown("## 均衡と調整"),
        code(
            """
from lib.chapter08.market import (
    LinearMarket,
    equilibrium,
    excess_demand,
    marshall_adjustment,
    price_state,
    shift_demand,
    shift_supply,
    walras_adjustment,
)

market = LinearMarket(demand_intercept, demand_slope, supply_intercept, supply_slope)
price, quantity = equilibrium(market)
print(f"均衡: 価格 {price:.2f}、数量 {quantity:.2f}")
print(f"P = {price0} の超過需要 {excess_demand(market, price0):.2f}、"
      f"{price_state(market, price0)}")
path = walras_adjustment(market, price0, speed, 6)
print("ワルラス的調整（価格）:", [round(p, 3) for p in path])
path = marshall_adjustment(market, quantity0, speed, 6)
print("マーシャル的調整（数量）:", [round(q, 3) for q in path])
print(f"需要が {delta} 動く: {equilibrium(shift_demand(market, delta))}")
print(f"供給が {delta} 動く: {equilibrium(shift_supply(market, delta))}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter08.plot import plot_market

plot_market(market, q_max, p_max)
"""
        ),
        code(
            """
from lib.chapter08.plot import plot_shift

plot_shift(market, delta, q_max, p_max)
"""
        ),
        code(
            """
from lib.chapter08.plot import plot_adjustment

plot_adjustment(market, price0, quantity0, speed, steps)
"""
        ),
        markdown(
            """
## 試してみよう

- `speed = 0.5` にすると、価格は 80 から、1 回で 55.0（均衡）に着きます
- `speed = 1.0` にすると、価格は 80 → 30 → 80 → 30 と、**行ったり来たり**して、
  均衡に近づきません
- `speed = 2.0` にすると、価格は 80 → −20 → 220 → −200 と、**発散**します。調整が
  速すぎると、均衡は、安定しません
- `supply_slope = 0.5`（供給が急）にすると、均衡は、価格 約 73.33、数量 約 26.67 です。
  `demand_slope = -0.5` でも、価格は約 73.33 ですが、数量は約 63.33 です
"""
        ),
    ]


def ch10_trade_and_comparative_advantage() -> list[NotebookNode]:
    return [
        _title(10, "国際貿易と比較優位", "10-trade-and-comparative-advantage"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
demand_intercept = 100  # 国内市場の需要 Q = a + s_d·P の切片 a
demand_slope = -1       # 需要の傾き s_d（負）
supply_intercept = -10  # 国内市場の供給 Q = c + s_s·P の切片 c
supply_slope = 1        # 供給の傾き s_s（正）
world_price = 40        # 世界価格
tariff = 10             # 関税（1 単位あたり）
q_max = 100             # 図の数量の範囲
p_max = 100             # 図の価格の範囲
# 比較優位: 1 単位を作るのに要る労働（工業・農業）と、国の労働の総量
large_industry, large_agriculture, large_labor = 4, 8, 80
small_industry, small_agriculture, small_labor = 20, 10, 40
""",
            parameters=True,
        ),
        markdown("## 貿易と関税"),
        code(
            """
from lib.chapter08.market import LinearMarket
from lib.chapter10.trade import (
    free_trade_result,
    gains_from_trade,
    tariff_deadweight_loss,
    tariff_result,
)

market = LinearMarket(demand_intercept, demand_slope, supply_intercept, supply_slope)
r = free_trade_result(market, world_price)
print(f"自由貿易（世界価格 {world_price}）: 需要 {r.quantity_demanded:.2f}、"
      f"供給 {r.quantity_supplied:.2f}、輸入 {r.net_imports:.2f}")
print(f"消費者余剰 {r.consumer_surplus:.2f}、生産者余剰 {r.producer_surplus:.2f}、"
      f"貿易の利益 {gains_from_trade(market, world_price):.2f}")
t = tariff_result(market, world_price, tariff)
print(f"関税 {tariff}: 国内価格 {t.domestic_price:.2f}、輸入 {t.net_imports:.2f}、"
      f"関税収入 {t.tariff_revenue:.2f}")
print(f"関税の死荷重: {tariff_deadweight_loss(market, world_price, tariff):.2f}")
"""
        ),
        markdown("## 比較優位"),
        code(
            """
from lib.chapter10.comparative import (
    Country,
    comparative_advantage,
    mutually_beneficial_terms,
    opportunity_cost_of_industry,
    ppf_endpoints,
)

large = Country("Large", large_industry, large_agriculture)
small = Country("Small", small_industry, small_agriculture)
print(f"工業の機会費用: 大国 {opportunity_cost_of_industry(large):.2f}、"
      f"小国 {opportunity_cost_of_industry(small):.2f}")
print(f"比較優位: 工業は {comparative_advantage(large, small, 'industry')}、"
      f"農業は {comparative_advantage(large, small, 'agriculture')}")
print(f"フロンティアの両端: 大国 {ppf_endpoints(large, large_labor)}、"
      f"小国 {ppf_endpoints(small, small_labor)}")
low, high = mutually_beneficial_terms(large, small)
print(f"両国が得をする交換比率: {low:.2f} から {high:.2f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter10.plot import plot_tariff

plot_tariff(market, world_price, tariff, q_max, p_max)
"""
        ),
        code(
            """
from lib.chapter10.plot import plot_ppf

plot_ppf(large, large_labor, small, small_labor)
"""
        ),
        markdown(
            """
## 試してみよう

- `tariff = 0` にすると、国内価格は 40（世界価格）、輸入は 30 で、関税収入も死荷重も
  0 です。`tariff = 5` なら、国内価格 45、輸入 20、関税収入 100、死荷重 25.0 です
- `tariff = 15` にすると、国内価格は 55（関税なしの均衡価格）で、輸入は 0 です。
  関税収入は 0、死荷重は 225.0（貿易の利益 225 を、すべて失う）。**禁止的な関税**です。
  これ以上上げても、変わりません
- `world_price = 30` にすると、輸入は 50、貿易の利益は 625.0 です。世界価格が、
  国内の均衡価格（55）から離れるほど、貿易の利益は大きくなります
- `small_industry = 6`、`small_agriculture = 10` にすると、小国の工業の機会費用は
  0.6 で、両国が得をする交換比率は、0.5 から 0.6 の**狭い範囲**になります
- `small_industry = 8`、`small_agriculture = 16`（大国と同じ比率）にすると、
  比較優位は、どちらにもなく（None）、貿易の利益の余地が、なくなります。大国は、
  どちらの財でも、絶対優位です
"""
        ),
    ]


def ch11_monopoly_and_monopolistic_competition() -> list[NotebookNode]:
    return [
        _title(
            11,
            "独占と独占的競争",
            "11-monopoly-and-monopolistic-competition",
        ),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
demand_intercept = 100  # 逆需要 P = a − b·Q の切片 a
demand_slope = 1        # 逆需要の傾き b（正）
marginal_cost = 10      # 限界費用（一定）
fixed_cost = 1000       # 固定費用（独占的競争の短期・長期）
q_max = 100             # 図の数量の範囲
p_max = 100             # 図の価格の範囲
""",
            parameters=True,
        ),
        markdown("## 独占と完全競争"),
        code(
            """
from lib.chapter11.monopoly import (
    Monopoly,
    competitive_outcome,
    deadweight_loss,
    demand_elasticity,
    lerner_index,
    long_run_monopolistic_competition,
    monopolistic_competition_profit,
    monopoly_outcome,
)

monopoly = Monopoly(demand_intercept, demand_slope, marginal_cost)
m = monopoly_outcome(monopoly)
c = competitive_outcome(monopoly)
print(f"独占: 数量 {m.quantity:.2f}、価格 {m.price:.2f}、利潤 {m.profit:.2f}")
print(f"完全競争: 数量 {c.quantity:.2f}、価格 {c.price:.2f}")
print(f"総余剰 独占 {m.total_surplus:.2f}、完全競争 {c.total_surplus:.2f}、"
      f"死荷重 {deadweight_loss(monopoly):.2f}")
e = demand_elasticity(monopoly, m.quantity)
print(f"独占点の弾力性 {e:.4f}、ラーナー指数 {lerner_index(monopoly, m.price):.4f}、"
      f"弾力性の逆数 {1 / e:.4f}")
print(f"短期の利潤（固定費用 {fixed_cost}）: "
      f"{monopolistic_competition_profit(monopoly, fixed_cost):.2f}")
long_run = long_run_monopolistic_competition(marginal_cost, demand_slope, fixed_cost)
print(f"長期: 数量 {long_run.quantity:.4f}、価格 {long_run.price:.4f}、"
      f"需要の切片 {long_run.demand_intercept:.4f}、利潤 {long_run.profit:.6f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter11.plot import plot_monopoly

plot_monopoly(monopoly, q_max, p_max)
"""
        ),
        code(
            """
from lib.chapter11.plot import plot_long_run

plot_long_run(monopoly, fixed_cost, q_max, p_max)
"""
        ),
        markdown(
            """
## 試してみよう

- `marginal_cost = 40` にすると、独占の数量は 30、価格は 70、利潤は 900、死荷重は
  450 です。費用が上がると、数量は減り、価格は上がります
- `demand_slope = 2`（需要が急）にすると、独占の価格は 55 のまま、数量は 22.5 に
  減ります。死荷重は 506.25 です
- `fixed_cost = 2000` にすると、短期の利潤は 25 まで減り、長期は、数量 約 44.72、
  価格 約 54.72 になります。長期の利潤は、どの固定費用でも 0 です
- `fixed_cost = 500` にすると、長期は、数量 約 22.36、価格 約 32.36 です。
  固定費用が小さいほど、長期の価格は、限界費用（10）に近づきます
"""
        ),
    ]


def ch12_oligopoly_and_game_theory() -> list[NotebookNode]:
    return [
        _title(12, "利得表とナッシュ均衡", "12-oligopoly-and-game-theory"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
# 囚人のジレンマの利得（T > R > P > S にする。戦略 0 = 協調、1 = 裏切り）
temptation = 5   # T: 自分だけ裏切る
reward = 3       # R: 2 人とも協調する
punishment = 1   # P: 2 人とも裏切る
sucker = 0       # S: 自分だけ協調する
# 協調ゲームの利得（2 人が同じ戦略をそろえると、得をする）
payoff_cooperate = 2   # 2 人とも、戦略 0 をとる
payoff_defect = 1      # 2 人とも、戦略 1 をとる
""",
            parameters=True,
        ),
        markdown("## 囚人のジレンマ"),
        code(
            """
from lib.chapter12.game import (
    best_responses_for_column,
    best_responses_for_row,
    dominant_strategy_for_row,
    is_pareto_dominated,
    is_prisoners_dilemma,
    prisoners_dilemma,
    pure_nash_equilibria,
)

game = prisoners_dilemma(temptation, reward, punishment, sucker)
print("利得表（行の戦略 → 列の戦略: (行の利得, 列の利得)）")
for i, row in enumerate(game.payoffs):
    print(f"  行 {i}:", row)
print("囚人のジレンマか:", is_prisoners_dilemma(game))
print("行の最適反応（列が協調・裏切り）:", best_responses_for_row(game, 0),
      best_responses_for_row(game, 1))
print("列の最適反応（行が協調・裏切り）:", best_responses_for_column(game, 0),
      best_responses_for_column(game, 1))
print("行の支配戦略:", dominant_strategy_for_row(game))
print("ナッシュ均衡:", pure_nash_equilibria(game))
print("（裏切り, 裏切り）はパレート劣位か:", is_pareto_dominated(game, (1, 1)))
"""
        ),
        markdown("## 協調ゲーム"),
        code(
            """
from lib.chapter12.game import Game

coordination = Game(
    (
        ((payoff_cooperate, payoff_cooperate), (0, 0)),
        ((0, 0), (payoff_defect, payoff_defect)),
    )
)
print("協調ゲームのナッシュ均衡:", pure_nash_equilibria(coordination))
print("支配戦略:", dominant_strategy_for_row(coordination))
print("（戦略 1, 戦略 1）はパレート劣位か:", is_pareto_dominated(coordination, (1, 1)))
"""
        ),
        markdown(
            """
## 試してみよう

利得の数字を変えても、T > R > P > S が成り立つ限り、結果は変わりません。

- `temptation = 6`、`reward = 4`、`punishment = 2` など、数字を変えて試してください。
  ナッシュ均衡は、いつも（裏切り、裏切り）の 1 つだけで、パレート劣位です。
  **各自が合理的に選ぶと、全員が、悪い結果になる**構造は、利得の大きさに、よりません
- `reward = 6` のように、T > R > P > S を崩すと、エラーになります
  （囚人のジレンマではなくなる）
- 協調ゲームでは、`payoff_cooperate = 3`、`payoff_defect = 3` にしても、ナッシュ均衡は
  2 つ（(0, 0) と (1, 1)）のままです。`payoff_cooperate = 2`、`payoff_defect = 1`
  では、(1, 1) が、パレート劣位です。均衡が複数あると、**どちらに落ち着くか**を、
  ナッシュ均衡だけでは、決められません
"""
        ),
    ]


def ch13_repeated_games_and_kinked_demand() -> list[NotebookNode]:
    return [
        _title(
            13,
            "繰り返しゲームと屈折需要曲線",
            "13-repeated-games-and-kinked-demand",
        ),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
temptation = 5    # T: 自分だけ裏切る（T > R > P > S）
reward = 3        # R: 2 人とも協調する
punishment = 1    # P: 2 人とも裏切る
sucker = 0        # S: 自分だけ協調する
delta = 0.6       # 割引因子（将来を、どれだけ大切にするか）
rounds = 4        # 繰り返す回数
kink_quantity = 40   # 屈折需要: 屈折点の数量
kink_price = 50      # 屈折点の価格
upper_slope = 0.5    # 屈折点より上（価格が高い側）の傾き
lower_slope = 2      # 屈折点より下の傾き
marginal_cost = 30   # 限界費用（価格が動くか、確かめる）
cost_low = 10        # 図に描く、低い限界費用
cost_high = 25       # 図に描く、高い限界費用
q_max = 100          # 屈折需要の図の数量の範囲
p_max = 80           # 屈折需要の図の価格の範囲
""",
            parameters=True,
        ),
        markdown("## 繰り返しゲーム"),
        code(
            """
from lib.chapter12.game import prisoners_dilemma
from lib.chapter13.repeated import (
    always_defect,
    cooperation_threshold,
    cooperation_value,
    deviation_value,
    play,
    tit_for_tat,
    total_payoffs,
    trigger_sustains_cooperation,
)

game = prisoners_dilemma(temptation, reward, punishment, sucker)
threshold = cooperation_threshold(temptation, reward, punishment)
print(f"協調が続く、割引因子の閾値: {threshold:.4f}")
sustains = trigger_sustains_cooperation(temptation, reward, punishment, delta)
print(f"δ = {delta}: 協調 {cooperation_value(reward, delta):.4f}、"
      f"裏切り {deviation_value(temptation, punishment, delta):.4f}、"
      f"協調が続くか {sustains}")
history = play(game, tit_for_tat, always_defect, rounds)
print("しっぺ返し対いつも裏切り:", total_payoffs(game, history))
history = play(game, tit_for_tat, tit_for_tat, rounds)
print("しっぺ返し同士:", total_payoffs(game, history))
"""
        ),
        markdown("## 屈折需要曲線"),
        code(
            """
from lib.chapter13.kinked import (
    KinkedDemand,
    marginal_revenue_above,
    marginal_revenue_below,
    marginal_revenue_gap,
    price_stays,
)

kinked = KinkedDemand(kink_quantity, kink_price, upper_slope, lower_slope)
print(f"限界収入: 上 {marginal_revenue_above(kinked):.2f}、"
      f"下 {marginal_revenue_below(kinked):.2f}、"
      f"途切れ {marginal_revenue_gap(kinked):.2f}")
print(f"限界費用 {marginal_cost} で、価格は動かないか: "
      f"{price_stays(kinked, marginal_cost)}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter13.plot import plot_trigger

plot_trigger(temptation, reward, punishment, 0.95, 100, 60)
"""
        ),
        code(
            """
from lib.chapter13.plot import plot_kinked

plot_kinked(kinked, q_max, p_max, cost_low, cost_high)
"""
        ),
        markdown(
            """
## 試してみよう

- `temptation = 6` にすると、閾値は 0.6 に上がります。`delta = 0.5` では、協調は
  続かず（False）、`delta = 0.6` なら続きます（True）。裏切りの誘惑が大きいほど、
  将来を、より大切にしないと、協調は続きません
- `punishment = 2` にすると、閾値は約 0.667 に上がります。罰（P）が軽いと、
  裏切っても失うものが小さいので、協調が続きにくくなります
- `rounds = 10` にすると、しっぺ返し対いつも裏切りは (9, 14)、しっぺ返し同士は
  (30, 30) です。最初の 1 回の搾取は、そのままで、回数が増えるほど、協調の差が開きます
- `lower_slope = 1` にすると、途切れは 20.0 に縮みます（2 のときは 60.0、4 では
  140.0）。屈折が弱いほど、価格が動かない範囲も、狭くなります
- `upper_slope = 1` にすると、`marginal_cost = 30` では、価格は動きます（False）。
  途切れの範囲が、10 から −30 の間に、変わるためです
"""
        ),
    ]


def ch14_externality_and_coase() -> list[NotebookNode]:
    return [
        _title(14, "外部効果とコースの定理", "14-externality-and-coase"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
demand_intercept = 100  # 逆需要 P = a − b·Q の切片 a
demand_slope = 1        # 逆需要の傾き b
cost_intercept = 10     # 私的な限界費用 MC = c + d·Q の切片 c
cost_slope = 1          # 私的な限界費用の傾き d
external_cost = 20      # 1 単位あたりの外部費用（負なら外部便益）
q_max = 100             # 図の数量の範囲
p_max = 100             # 図の価格の範囲
# コースの定理: 加害者の利益と、被害者の被害
gain = 100              # 汚染する加害者の利益
damage = 60             # 被害者の被害
victim_has_right = True  # 権利が、被害者にあるか（False なら加害者）
# 排出権取引: 企業ごとの、削減費用の傾き（大きいほど、削減が苦しい）
slopes = [1, 2, 4]
total_reduction = 14    # 全体で削減する量
""",
            parameters=True,
        ),
        markdown("## 外部効果とピグー税"),
        code(
            """
from lib.chapter14.externality import (
    ExternalityMarket,
    externality_deadweight_loss,
    market_quantity,
    pigou_tax,
    quantity_with_tax,
    socially_optimal_quantity,
)

market = ExternalityMarket(
    demand_intercept, demand_slope, cost_intercept, cost_slope, external_cost
)
tax = pigou_tax(market)
print(f"市場の数量: {market_quantity(market):.2f}、"
      f"社会的に最適な数量: {socially_optimal_quantity(market):.2f}")
print(f"ピグー税: {tax:.2f}、税のもとの数量: {quantity_with_tax(market, tax):.2f}")
print(f"死荷重: {externality_deadweight_loss(market):.2f}")
"""
        ),
        markdown("## コースの定理と排出権取引"),
        code(
            """
from lib.chapter14.externality import (
    abatement_cost,
    coase_outcome,
    emissions_trading,
    uniform_reduction,
)

result = coase_outcome(gain, damage, victim_has_right)
print(f"コース（利益 {gain}、被害 {damage}）: 汚染する {result.pollution}、"
      f"払う金額の範囲 {result.payment_range}")
price, reductions = emissions_trading(slopes, total_reduction)
print(f"排出権の価格 {price:.2f}、削減量 {[round(r, 4) for r in reductions]}、"
      f"費用 {abatement_cost(slopes, reductions):.4f}")
uniform = uniform_reduction(slopes, total_reduction)
print(f"一律規制の削減量 {[round(r, 4) for r in uniform]}、"
      f"費用 {abatement_cost(slopes, uniform):.4f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter14.plot import plot_externality

plot_externality(market, q_max, p_max)
"""
        ),
        markdown(
            """
## 試してみよう

- `external_cost = 40` にすると、最適な数量は 25、ピグー税は 40、死荷重は 400.0 です。
  外部費用が 2 倍になると、死荷重は **4 倍**になります（2 乗に比例）
- `external_cost = 0` にすると、市場の数量と最適な数量が一致して（45）、
  死荷重は 0 です。`external_cost = -10`（外部便益）にすると、最適な数量は 50、
  税は −10（補助金）、死荷重は 25.0 です
- `gain = 40` にすると、権利が被害者にあっても、加害者にあっても、汚染しません。
  `gain = 100` なら、どちらでも、汚染します。権利の持ち主が違っても、**汚染するかは
  同じ**で、お金の流れだけが変わります
- `slopes = [1, 1, 1]` にすると、排出権取引も一律規制も、費用は約 32.67 で同じです。
  `slopes = [1, 1, 4]` にすると、約 43.56 と約 65.33 で、費用の差が開きます。
  企業の費用の差が大きいほど、取引の利益が大きくなります
"""
        ),
    ]


def ch15_public_goods_and_natural_monopoly() -> list[NotebookNode]:
    return [
        _title(
            15,
            "公共財と自然独占",
            "15-public-goods-and-natural-monopoly",
        ),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
# 自然独占（逆需要 P = a − b·Q、限界費用一定、固定費用が大きい）
demand_intercept = 100  # 逆需要の切片 a
demand_slope = 1        # 逆需要の傾き b
marginal_cost = 10      # 限界費用
fixed_cost = 800        # 固定費用（正にする）
q_max = 100             # 図の数量の範囲
p_max = 100             # 図の価格の範囲
# 公共財: 人ごとの限界便益 MB = a_i − b_i·q
benefit_intercepts = (40, 20)  # 人ごとの切片
benefit_slopes = (2, 1)        # 人ごとの傾き
public_marginal_cost = 30      # 公共財の限界費用
# 財の分類
rival = True        # 競合性があるか
excludable = False  # 排除性があるか
""",
            parameters=True,
        ),
        markdown("## 自然独占の価格規制"),
        code(
            """
from lib.chapter11.monopoly import Monopoly
from lib.chapter15.natural import (
    average_cost_pricing,
    marginal_cost_pricing,
    required_subsidy,
    unregulated_outcome,
)

demand = Monopoly(demand_intercept, demand_slope, marginal_cost)
outcomes = (
    ("限界費用価格", marginal_cost_pricing(demand, fixed_cost)),
    ("平均費用価格", average_cost_pricing(demand, fixed_cost)),
    ("規制なし", unregulated_outcome(demand, fixed_cost)),
)
for name, o in outcomes:
    print(f"{name}: 価格 {o.price:.2f}、数量 {o.quantity:.2f}、"
          f"利潤 {o.profit:.2f}、総余剰 {o.total_surplus:.2f}")
print(f"限界費用価格に必要な補助金: {required_subsidy(demand, fixed_cost):.2f}")
"""
        ),
        markdown("## 公共財"),
        code(
            """
from lib.chapter15.public import (
    PublicGood,
    classify_good,
    public_good_optimal_quantity,
    under_provision,
    voluntary_quantity,
)

good = PublicGood(benefit_intercepts, benefit_slopes, public_marginal_cost)
print(f"最適な供給量: {public_good_optimal_quantity(good):.4f}")
print(f"自発的な供給量: {voluntary_quantity(good):.4f}")
print(f"過少供給: {under_provision(good):.4f}")
print(f"財の分類（競合 {rival}、排除 {excludable}）: "
      f"{classify_good(rival, excludable)}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter15.plot import plot_natural_monopoly

plot_natural_monopoly(demand, fixed_cost, q_max, p_max)
"""
        ),
        markdown(
            """
## 試してみよう

- `fixed_cost = 1600` にすると、平均費用価格は、価格 約 34.38、数量 約 65.62 になり、
  規制なしの利潤は 425.0 に減ります。固定費用が大きいほど、平均費用価格は、
  独占の価格に近づきます
- `fixed_cost = 2000` にすると、平均費用価格は、価格 50.0、数量 50.0 です。規制なしの
  利潤は 25.0 まで減ります。限界費用価格の補助金は 2000.0 です
- `public_marginal_cost = 10` にすると、最適な供給量は約 16.67、自発的な供給量は 15.0、
  過少供給は約 1.67 です。費用が低いと、**過少供給は小さく**なります
- `benefit_intercepts = (40, 20, 30)`、`benefit_slopes = (2, 1, 1)`（3 人）にすると、
  最適な供給量は 15.0 に増えますが、自発的な供給量は 5.0 のままで、
  過少供給は 10.0 です。
  **人が増えるほど、フリーライダーの問題は、大きく**なります
- `rival = False`、`excludable = False` にすると、`public`（公共財）に分類されます
"""
        ),
    ]


def ch16_information_asymmetry() -> list[NotebookNode]:
    return [
        _title(16, "情報の非対称性", "16-information-asymmetry"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
# 逆選択（レモンの市場）
good_share = 0.5          # 良い品の割合
value_good = 100          # 良い品の、買い手にとっての価値
value_bad = 40            # 悪い品の、買い手にとっての価値
seller_reservation = 60   # 良い品の売り手の、最低価格
qualities = [20, 40, 60, 80, 100]  # 品質のリスト
premium = 1.5             # 買い手の評価の倍率（質 × 倍率 まで払う）
# シグナリング（教育）
wage_high = 100           # 高い能力の人の賃金
wage_low = 60             # 低い能力の人の賃金
cost_high = 10            # 教育 1 年あたりの費用（高い能力）
cost_low = 20             # 教育 1 年あたりの費用（低い能力。cost_high より大きく）
education = 3             # 調べる教育年数
e_max = 6                 # 図の教育年数の範囲
# モラルハザード（成果報酬）
value = 100               # 成功したときの、依頼人の価値
p_high = 0.8              # 努力したときの、成功の確率
p_low = 0.4               # 努力しないときの、成功の確率
effort_cost = 10          # 努力の費用
bonus = 25                # 成功したときの報酬
b_max = 60                # 図の報酬の範囲
""",
            parameters=True,
        ),
        markdown("## 逆選択"),
        code(
            """
from lib.chapter16.information import (
    expected_value_of_unknown_quality,
    good_quality_sells,
    unraveling,
)

willingness = expected_value_of_unknown_quality(good_share, value_good, value_bad)
print(f"質が分からない買い手の支払意思額: {willingness:.2f}")
sells = good_quality_sells(good_share, value_good, value_bad, seller_reservation)
print(f"良い品は売られるか（最低価格 {seller_reservation}）: {sells}")
print(f"評価の倍率 {premium} のとき、市場に残る質: {unraveling(qualities, premium)}")
"""
        ),
        markdown("## シグナリング"),
        code(
            """
from lib.chapter16.information import separating_education_range, signal_separates

low, high = separating_education_range(wage_high, wage_low, cost_high, cost_low)
print(f"区別できる教育年数の範囲: {low:.2f} 年から {high:.2f} 年")
separates = signal_separates(education, wage_high, wage_low, cost_high, cost_low)
print(f"教育 {education} 年で区別できるか: {separates}")
"""
        ),
        markdown("## モラルハザード"),
        code(
            """
from lib.chapter16.information import (
    agent_works,
    minimum_bonus,
    principal_profit_with_bonus,
    worth_paying_bonus,
)

print(f"努力させる、最低の成果報酬: {minimum_bonus(p_high, p_low, effort_cost):.2f}")
print(f"報酬 {bonus} で努力するか: {agent_works(bonus, p_high, p_low, effort_cost)}")
profit_effort = principal_profit_with_bonus(value, p_high, p_low, effort_cost)
print(f"依頼人の期待利潤（努力させる）: {profit_effort:.2f}、"
      f"努力なし: {p_low * value:.2f}")
worth = worth_paying_bonus(value, p_high, p_low, effort_cost)
print(f"努力させる価値があるか: {worth}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter16.plot import plot_signal

plot_signal(wage_high, wage_low, cost_high, cost_low, e_max)
"""
        ),
        code(
            """
from lib.chapter16.plot import plot_bonus

plot_bonus(p_high, p_low, effort_cost, b_max)
"""
        ),
        markdown(
            """
## 試してみよう

- `good_share = 0.8` にすると、支払意思額は 88.0 で、`seller_reservation = 80` でも、
  良い品は売られます。`good_share = 0.2` では、支払意思額は 52.0 で、最低価格 60 の
  良い品も、売られません。**悪い品が多いほど、良い品が消えやすい**です
- `premium = 1.2` にすると、残るのは [20] だけ、`premium = 2.0` なら、全部が残ります。
  買い手の評価が高いほど、市場は崩れにくくなります
- `cost_low = 40` にすると、区別できる教育年数は 1.0 年から 4.0 年に広がります。
  `wage_high = 80` では、1.0 年から 2.0 年に狭まります。`cost_high = 15` では、
  2.0 年から約 2.67 年です
- `cost_low = 10`（`cost_high` と同じ）にすると、エラーになります。低い能力の人の
  ほうが、教育が苦しい、という前提が崩れるためです
- `effort_cost = 20` にすると、最低の報酬は 50.0 に上がり、依頼人の期待利潤は 40.0 で、
  努力させない場合と同じです（努力させる価値は、ありません）。`p_high = 0.9` にすると、
  最低の報酬は 20.0 に下がり、期待利潤は 72.0 に増えます
"""
        ),
    ]


NOTEBOOKS: dict[str, Callable[[], list[NotebookNode]]] = {
    "ch01_utility_and_indifference_curves": ch01_utility_and_indifference_curves,
    "ch02_budget_and_optimal_choice": ch02_budget_and_optimal_choice,
    "ch03_demand_curve_and_elasticity": ch03_demand_curve_and_elasticity,
    "ch04_slutsky_decomposition_and_goods": ch04_slutsky_decomposition_and_goods,
    "ch05_cost_curves": ch05_cost_curves,
    "ch06_production_function_and_cost_minimization": (
        ch06_production_function_and_cost_minimization
    ),
    "ch07_profit_maximization_and_supply": ch07_profit_maximization_and_supply,
    "ch08_market_equilibrium_and_adjustment": ch08_market_equilibrium_and_adjustment,
    "ch09_surplus_and_tax": ch09_surplus_and_tax,
    "ch10_trade_and_comparative_advantage": ch10_trade_and_comparative_advantage,
    "ch11_monopoly_and_monopolistic_competition": (
        ch11_monopoly_and_monopolistic_competition
    ),
    "ch12_oligopoly_and_game_theory": ch12_oligopoly_and_game_theory,
    "ch13_repeated_games_and_kinked_demand": ch13_repeated_games_and_kinked_demand,
    "ch14_externality_and_coase": ch14_externality_and_coase,
    "ch15_public_goods_and_natural_monopoly": ch15_public_goods_and_natural_monopoly,
    "ch16_information_asymmetry": ch16_information_asymmetry,
}


def main() -> None:
    for name, build in sorted(NOTEBOOKS.items()):
        path = NOTEBOOKS_DIR / f"{name}.ipynb"
        write(path, build())
        print(f"生成: {path.name}")


if __name__ == "__main__":
    main()
