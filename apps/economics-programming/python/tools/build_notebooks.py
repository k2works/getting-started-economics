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
ARTICLES = "docs/article/economics-programming"
HOW_TO_RUN = (
    "**使い方**: 「Parameters」のセルの数字を書き換えて、上から順に実行します"
    "（メニューの Run → Run All Cells）。数字を変えるたびに、結果と図が変わります。\n\n"
    "起動: アプリのディレクトリで `uv run --with jupyterlab jupyter lab notebooks/` "
    "を実行します。"
)


def intro(title: str, article: str) -> NotebookNode:
    """章のタイトル・使い方・記事のパスを書いた、先頭の説明のセル。"""
    return markdown(
        f"# {title}: 数字を変えて確かめる\n\n{HOW_TO_RUN}\n\n"
        f"記事: `{ARTICLES}/{article}.md`"
    )


def ch01_preparation_and_first_test() -> list[NotebookNode]:
    return [
        intro("第 1 章 準備とはじめてのテスト", "01-preparation-and-first-test"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
intercept = 100  # 需要曲線 Q = a - bP の切片 a（価格 0 のときの需要量）
slope = 2        # 需要曲線の傾き b（正。価格が 1 上がると、需要量が b 減る）
price = 10       # 需要量を知りたい価格 P
""",
            parameters=True,
        ),
        markdown("## 需要量とチョーク価格"),
        code(
            """
from lib.chapter01.demand import choke_price, quantity_demanded

quantity = quantity_demanded(price, intercept, slope)
print(f"価格 {price} のときの需要量: {quantity}")
print(f"需要量が 0 になる価格（チョーク価格）: {choke_price(intercept, slope)}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter01.plot import plot_demand_curve

plot_demand_curve(intercept, slope)
"""
        ),
        markdown(
            """
## 試してみよう

- `slope` を 4 にすると、チョーク価格は 50 から 25 に下がります（傾きが急になる）
- `intercept` を 200 にすると、チョーク価格は 100 になります
- `price` を 60 にすると、需要量は 0 になります（計算上は負になりますが、需要量は
  負にならないので、0 で止まります）
"""
        ),
    ]


def ch02_data_types_and_variables() -> list[NotebookNode]:
    return [
        intro("第 2 章 データ型と変数", "02-data-types-and-variables"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
price_before = 10      # 値上げ前の価格
price_after = 12       # 値上げ後の価格
quantity_before = 80   # 値上げ前の需要量
quantity_after = 72    # 値上げ後の需要量
income_before = 300    # 所得が増える前
income_after = 330     # 所得が増えたあと
income_quantity_before = 50  # 所得が増える前の需要量
income_quantity_after = 60   # 所得が増えたあとの需要量
demand_intercept = 100  # 図: 需要曲線 Q = a - bP の切片 a
demand_slope = 2        # 図: 需要曲線の傾き b
""",
            parameters=True,
        ),
        markdown("## 価格弾力性と所得弾力性"),
        code(
            """
from lib.chapter02.elasticity import (
    classify_income_elasticity,
    income_elasticity,
    is_price_elastic,
    price_elasticity,
)

e = price_elasticity(price_before, price_after, quantity_before, quantity_after)
print(f"価格弾力性: {e:.2f}（弾力的か: {is_price_elastic(e)}）")
ie = income_elasticity(
    income_before, income_after, income_quantity_before, income_quantity_after
)
print(f"所得弾力性: {ie:.2f}（{classify_income_elasticity(ie)}）")
"""
        ),
        markdown("## 図: 弾力的な部分と非弾力的な部分"),
        code(
            """
from lib.chapter02.plot import plot_elasticity_regions

plot_elasticity_regions(demand_intercept, demand_slope)
"""
        ),
        markdown(
            """
## 試してみよう

- `quantity_after` を 60 にすると、価格弾力性は 0.5 から 1.25 になり、弾力的
  （1 より大きい）になります
- `income_quantity_after` を 52 にすると、所得弾力性は 0.4 になり、必需品です。
  48 にすると、負になり、下級財です（60 のときは 2.0 で、奢侈品）
- `demand_slope` を 4 にすると、弾力性がちょうど 1 になる価格が、25 から 12.5 に
  下がります（図の黒い点が下へ動きます）
"""
        ),
    ]


def ch03_containers_and_data_operations() -> list[NotebookNode]:
    return [
        intro("第 3 章 コンテナとデータの操作", "03-containers-and-data-operations"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
prices = [10, 15, 20, 25, 30]  # 需要表・供給表に並べる価格のリスト
demand_intercept = 100  # 需要 Q = a - bP の切片 a
demand_slope = 2        # 需要の傾き b
supply_intercept = 0    # 供給 Q = c + dP の切片 c
supply_slope = 3        # 供給の傾き d
""",
            parameters=True,
        ),
        markdown("## 需要表・供給表と、市場均衡"),
        code(
            """
from lib.chapter03.schedule import (
    demand_schedule,
    excess_demand,
    market_clearing_prices,
    supply_schedule,
)

demand = demand_schedule(prices, demand_intercept, demand_slope)
supply = supply_schedule(prices, supply_intercept, supply_slope)
print("需要表:", demand)
print("供給表:", supply)
print("超過需要:", excess_demand(demand, supply))
print("市場均衡の価格:", market_clearing_prices(demand, supply))
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter03.plot import plot_schedules

plot_schedules(demand, supply)
"""
        ),
        markdown(
            """
## 試してみよう

- `supply_intercept` を -10 にすると、均衡価格は 22 になり、リストの価格には 22 が
  ないので、「市場均衡の価格」は空のリスト `[]` になります（表の上では、均衡が
  見つかりません）
- `prices` を `[10, 20, 30]` にしても、均衡の価格 20 は 1 つ見つかります
  （表が粗くても、20 が含まれていれば見つかります）
"""
        ),
    ]


def ch04_functions_and_methods() -> list[NotebookNode]:
    return [
        intro("第 4 章 関数とメソッド", "04-functions-and-methods"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
quantity = 3        # 生産量 q
fixed_cost = 10     # 固定費用
good_x = 4          # 財 x の消費量
good_y = 9          # 財 y の消費量
alpha = 0.5         # 効用 U = x^a · y^(1-a) の指数 a
max_quantity = 6    # 図に描く生産量の上限
""",
            parameters=True,
        ),
        markdown("## 費用関数と効用関数"),
        code(
            """
from lib.chapter04.cost import (
    average_cost,
    average_variable_cost,
    marginal_cost,
    total_cost,
)
from lib.chapter04.utility import cobb_douglas_utility, marginal_rate_of_substitution

print(f"総費用 {total_cost(quantity, fixed_cost):.2f}")
print(f"限界費用 {marginal_cost(quantity):.2f}")
print(f"平均費用 {average_cost(quantity, fixed_cost):.2f}")
print(f"平均可変費用 {average_variable_cost(quantity):.2f}")
utility = cobb_douglas_utility(good_x, good_y, alpha)
print(f"効用 {utility:.2f}")
mrs = marginal_rate_of_substitution(good_x, good_y, alpha)
print(f"限界代替率 {mrs:.3f}")
"""
        ),
        markdown("## 図: 費用曲線"),
        code(
            """
from lib.chapter04.plot import plot_cost_curves

plot_cost_curves(max_quantity)
"""
        ),
        markdown(
            """
## 試してみよう

- `fixed_cost` を 20 にすると、総費用は 28 から 38 に、平均費用は 9.33 から 12.67 に
  なります（限界費用と平均可変費用は、固定費用に関係なく 6 のまま）
- `alpha` を 0.3 にすると、効用は 6.00 から 7.06 に、限界代替率は 2.25 から 0.964 に
  なります
- `good_x` を 8 にすると、限界代替率は 2.25 から 1.125 に半分になります
  （x が増えるほど、x の価値が下がります）
"""
        ),
    ]


def ch05_control_flow() -> list[NotebookNode]:
    return [
        intro("第 5 章 制御フロー", "05-control-flow"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
demand_intercept = 100  # 需要 Q = a - bP の切片 a
demand_slope = 2        # 需要の傾き b
supply_intercept = 0    # 供給 Q = c + dP の切片 c
supply_slope = 3        # 供給の傾き d
initial_price = 0       # ワルラス調整の、最初の価格
walras_step = 0.1       # ワルラス調整の速さ（大きすぎると収束しない）
initial_quantity = 0    # マーシャル調整の、最初の数量
marshall_step = 0.1     # マーシャル調整の速さ
""",
            parameters=True,
        ),
        markdown("## 価格調整（ワルラス）と、数量調整（マーシャル）"),
        code(
            """
from lib.chapter01.demand import quantity_demanded
from lib.chapter03.schedule import quantity_supplied
from lib.chapter05.adjustment import marshall_path, walras_path
from lib.chapter07.surplus import equilibrium, inverse_demand

eq_price, eq_quantity = equilibrium(
    demand_intercept, demand_slope, supply_intercept, supply_slope
)
print(f"均衡: 価格 {eq_price:.2f}、数量 {eq_quantity:.2f}")

price_path = walras_path(
    lambda p: quantity_demanded(p, demand_intercept, demand_slope),
    lambda p: quantity_supplied(p, supply_intercept, supply_slope),
    initial_price,
    walras_step,
)
print(f"ワルラス調整: {len(price_path) - 1} 回で、価格 {price_path[-1]:.3f}")

quantity_path = marshall_path(
    lambda q: inverse_demand(q, demand_intercept, demand_slope),
    lambda q: (q - supply_intercept) / supply_slope,
    initial_quantity,
    marshall_step,
)
print(f"マーシャル調整: {len(quantity_path) - 1} 回で、数量 {quantity_path[-1]:.3f}")
"""
        ),
        markdown("## 図: 価格の調整経路"),
        code(
            """
from lib.chapter05.plot import plot_price_paths

plot_price_paths({"Walras": price_path}, eq_price)
"""
        ),
        markdown(
            """
## 試してみよう

- `walras_step` を 0.05 にすると、収束までの回数が 27 回から 65 回に増えます
  （ゆっくり動くので、回数が増えます）
- `walras_step` を 0.5 にすると、価格が収束せず、`RuntimeError` で止まります
  （速すぎると、均衡を行きすぎて、振動が大きくなります）
- `marshall_step` を 0.5 にすると、収束までの回数が 204 回から 33 回に減ります
  （数量は、60 に収束します）
"""
        ),
    ]


def ch06_modules_errors_and_algorithms() -> list[NotebookNode]:
    return [
        intro(
            "第 6 章 モジュール・エラー・アルゴリズム",
            "06-modules-errors-and-algorithms",
        ),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
demand_intercept = 100  # 需要 Q = a - bP の切片 a
demand_slope = 2        # 需要の傾き b
supply_intercept = 0    # 供給 Q = c + dP の切片 c
supply_slope = 3        # 供給の傾き d
low = 0                 # 二分法で探す区間の下限（価格）
high = 100              # 二分法で探す区間の上限（価格）
tolerance = 1e-9        # 区間の幅が、これより小さくなったら、止める
steps = 6               # 図に描く、二分法の中点の数
""",
            parameters=True,
        ),
        markdown("## 二分法で、均衡価格を求める"),
        code(
            """
from lib.chapter06.bisection import find_equilibrium_price, make_excess_demand

excess_demand = make_excess_demand(
    demand_intercept, demand_slope, supply_intercept, supply_slope
)
price = find_equilibrium_price(excess_demand, low, high, tolerance)
print(f"均衡価格: {price:.6f}")
"""
        ),
        markdown("## 図: 二分法の中点が、0 に近づく"),
        code(
            """
from lib.chapter06.plot import plot_bisection

plot_bisection(excess_demand, low, high, steps)
"""
        ),
        markdown(
            """
## 試してみよう

- `supply_intercept` を -10 にすると、均衡価格は 22 になります
- `low` を 30 にすると、区間 [30, 100] の両端で超過需要の符号が同じ（どちらも
  負）なので、`NoEquilibriumError` で止まります（均衡が区間の外にあるため）
- `tolerance` を大きくすると、反復が減ります（区間の幅を 100 から
  半分ずつに絞るとき、誤差 1e-9 では 37 回、1e-3 では 17 回、1 では 7 回です）
"""
        ),
    ]


def ch07_plotting_with_matplotlib() -> list[NotebookNode]:
    return [
        intro("第 7 章 Matplotlib による図示", "07-plotting-with-matplotlib"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
demand_intercept = 100  # 需要 Q = a - bP の切片 a
demand_slope = 2        # 需要の傾き b
supply_intercept = 0    # 供給 Q = c + dP の切片 c
supply_slope = 3        # 供給の傾き d
tax = 5                 # 従量税（売り手に、1 単位あたり課す）
""",
            parameters=True,
        ),
        markdown("## 均衡・余剰・課税"),
        code(
            """
from lib.chapter07.surplus import (
    consumer_surplus,
    equilibrium,
    equilibrium_with_tax,
    producer_surplus,
)

market = (demand_intercept, demand_slope, supply_intercept, supply_slope)
price, quantity = equilibrium(*market)
print(f"均衡: 価格 {price:.2f}、数量 {quantity:.2f}")
print(f"消費者余剰 {consumer_surplus(*market):.2f}")
print(f"生産者余剰 {producer_surplus(*market):.2f}")

result = equilibrium_with_tax(*market, tax)
print(f"課税後: 買い手の価格 {result.consumer_price:.2f}、"
      f"売り手の手取り {result.producer_price:.2f}、数量 {result.quantity:.2f}")
print(f"税収 {result.tax_revenue:.2f}、死荷重 {result.deadweight_loss:.2f}")
print(f"税の負担: 買い手 {result.consumer_price - price:.2f}、"
      f"売り手 {price - result.producer_price:.2f}")
"""
        ),
        markdown("## 図: 需要と供給"),
        code(
            """
from lib.chapter07.plot import draw_market

draw_market(*market)
"""
        ),
        markdown("## 図: 従量税"),
        code(
            """
from lib.chapter07.plot import draw_tax_wedge

draw_tax_wedge(*market, tax)
"""
        ),
        markdown(
            """
## 試してみよう

- `tax` を 10 にすると、死荷重は 15 から 60 になります（税額が 2 倍で、死荷重は
  **4 倍**。税額の 2 乗に比例します）。0 にすると、税収も死荷重も 0 です
- `demand_slope` を 4 にして、`tax` を 5 のままにすると、死荷重は 21.43 に増えます。
  買い手の負担は 2.14、売り手の負担は 2.86 で、売り手の負担のほうが大きくなります
  （価格に敏感な側ほど、負担が小さくなります）
- `supply_slope` を 6 にすると、死荷重は 18.75 になります
"""
        ),
    ]


def ch08_random_numbers_and_simulation() -> list[NotebookNode]:
    return [
        intro("第 8 章 乱数とシミュレーション", "08-random-numbers-and-simulation"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0           # 乱数の種（同じ値なら、同じ結果になる）
price = 10         # 需要を観測する価格
intercept = 100    # 需要 Q = a - bP の切片 a
slope = 2          # 需要の傾き b
sigma = 10         # 観測値のばらつき（標準偏差）
n = 1000           # 観測値の個数
sample_size = 5    # サイコロを振る回数（1 回の試行あたり）
trials = 1000      # 試行の回数
bins = 30          # ヒストグラムの棒の数
""",
            parameters=True,
        ),
        markdown("## 大数の法則: 観測値の累積平均"),
        code(
            """
import random
import statistics

from lib.chapter08.simulation import running_means, sample_means, simulate_demand

rng = random.Random(seed)
observations = simulate_demand(price, intercept, slope, sigma, n, rng)
means = running_means(observations)
print(f"累積平均: 1 個 {means[0]:.2f}、10 個 {means[min(9, n - 1)]:.2f}、"
      f"全部 {means[-1]:.2f}（真の値 {intercept - slope * price}）")
"""
        ),
        markdown("## 図: 観測値の分布"),
        code(
            """
from lib.chapter08.simulation import plot_histogram

plot_histogram(observations, bins)
"""
        ),
        markdown("## 中心極限定理: サイコロの平均"),
        code(
            """
averages = sample_means(sample_size, trials, random.Random(seed))
print(f"平均の平均 {statistics.mean(averages):.3f}、"
      f"標準偏差 {statistics.stdev(averages):.3f}")
"""
        ),
        code(
            """
plot_histogram(averages, bins)
"""
        ),
        markdown(
            """
## 試してみよう

- `sigma` を 0 にすると、観測値はすべて真の値 80 で、累積平均は最初から 80 です。
  30 にすると、観測値のばらつきが大きく、最小が約 -7、最大が約 187 になります
  （それでも、累積平均は、n = 1000 で約 80.5 に近づきます）
- `sample_size` を 1 にすると、平均の標準偏差は 1.74、5 で 0.77、30 で 0.31 に
  なります（平均は、どれも約 3.5 で、標準偏差は、回数の平方根に反比例して、
  小さくなります）
- 図の形は、`sample_size` が大きいほど、釣り鐘型（正規分布）に近づきます
"""
        ),
    ]


def ch09_numpy_arrays() -> list[NotebookNode]:
    return [
        intro("第 9 章 NumPy による配列計算", "09-numpy-arrays"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
autonomous_consumption = 100  # 基礎消費 C0
mpc = 0.8                     # 限界消費性向 c（0 以上 1 未満）
investment = 100              # 投資 I
new_investment = 150          # 図: 投資が変わったあとの値
initial_spending = 100        # 乗数効果: 最初の支出
rounds = 5                    # 乗数効果: 波及を見る回数
demand_intercept = 100        # 需要 Q = a - bP の切片 a
demand_slope = 2              # 需要の傾き b
supply_intercept = 0          # 供給 Q = c + dP の切片 c
supply_slope = 3              # 供給の傾き d
""",
            parameters=True,
        ),
        markdown("## 乗数効果と、国民所得の決定"),
        code(
            """
from lib.chapter09.linear import (
    equilibrium_by_linear_algebra,
    income_determination,
    multiplier,
    spending_rounds,
)

print(f"乗数: {multiplier(mpc):.2f}")
spread = spending_rounds(initial_spending, mpc, rounds)
print(f"波及する支出（{rounds} 回）: {spread.round(2).tolist()}")
print(f"波及の合計: {spread.sum():.2f}")
income, consumption = income_determination(autonomous_consumption, mpc, investment)
print(f"均衡所得 {income:.2f}、消費 {consumption:.2f}")
price, quantity = equilibrium_by_linear_algebra(
    demand_intercept, demand_slope, supply_intercept, supply_slope
)
print(f"市場均衡（連立方程式）: 価格 {price:.2f}、数量 {quantity:.2f}")
"""
        ),
        markdown("## 図: 45 度線分析"),
        code(
            """
from lib.chapter09.plot import plot_keynesian_cross

plot_keynesian_cross(autonomous_consumption, mpc, investment, new_investment)
"""
        ),
        markdown(
            """
## 試してみよう

- `investment` が 100 で `new_investment` が 150 のとき、均衡所得は 1000 から
  1250 に 250 増えます（投資の増加 50 × 乗数 5）。図で、2 つの均衡点を比べます
- `mpc` を 0.5 にすると、乗数は 2.0、均衡所得は 400 に下がります。0.9 にすると、
  乗数は 10.0 に上がります
- `rounds` を 50 にすると、波及の合計は約 500 になり、初期支出 × 乗数
  （100 × 5）に近づきます（5 回では 336.16）
"""
        ),
    ]


def ch10_optimization_with_scipy() -> list[NotebookNode]:
    return [
        intro("第 10 章 SciPy による最適化", "10-optimization-with-scipy"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
price_x = 2      # 財 x の価格
price_y = 1      # 財 y の価格
income = 100     # 所得（予算）
alpha = 0.5      # 効用 U = x^a · y^(1-a) の指数 a
goods_price = 6  # 利潤最大化: 財の価格 P
output = 10      # 費用最小化: 作りたい産出量
wage = 1         # 費用最小化: 賃金 w
rental = 1       # 費用最小化: 資本の賃貸料 r
""",
            parameters=True,
        ),
        markdown("## 効用最大化・利潤最大化・費用最小化"),
        code(
            """
from lib.chapter10.optimization import (
    maximize_utility,
    minimize_cost,
    profit_maximizing_quantity,
)

best_x, best_y = maximize_utility(price_x, price_y, income, alpha)
print(f"効用最大化: x = {best_x:.2f}、y = {best_y:.2f}")
print(f"利潤最大化: 価格 {goods_price} のとき生産量 "
      f"{profit_maximizing_quantity(goods_price):.2f}")
labor, capital, cost = minimize_cost(output, wage, rental)
print(f"費用最小化: 労働 {labor:.2f}、資本 {capital:.2f}、費用 {cost:.2f}")
"""
        ),
        markdown("## 図: 予算線と無差別曲線"),
        code(
            """
from lib.chapter10.plot import plot_utility_maximization

plot_utility_maximization(price_x, price_y, income, alpha)
"""
        ),
        markdown(
            """
## 試してみよう

- `price_x` を 1 にすると、x の購入量は 25 から 50 に増えます（y は 50 のまま。
  指数 0.5 のコブ・ダグラス型では、各財に所得の半分を使います）
- `alpha` を 0.3 にすると、x は約 15、y は約 70 になります（x への支出の割合が
  0.3 になります）
- `goods_price` を 3 にすると、生産量は 0（操業停止）です。6 で 3.00、10 で 3.53、
  30 で 5.00 と、価格が高いほど増えます
- `wage` を 4 にすると、労働は約 5、資本は約 20、費用は約 40 になり、安い資本へ
  切り替わります
"""
        ),
    ]


def ch11_data_analysis_with_pandas() -> list[NotebookNode]:
    return [
        intro("第 11 章 Pandas によるデータ分析", "11-data-analysis-with-pandas"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
year = 2020                         # 見る年（2011〜2021。2010 は成長率が出ない）
base_prices = [100, 200]            # 物価指数: 基準年の価格（財ごと）
base_quantities = [10, 5]           # 基準年の数量
current_prices = [110, 190]         # 比較年の価格
current_quantities = [8, 6]         # 比較年の数量
""",
            parameters=True,
        ),
        markdown("## 3 面の GDP・成長率・構成比"),
        code(
            """
from lib.chapter11.economy import (
    expenditure_gdp,
    expenditure_shares,
    growth_rates,
    income_gdp,
    load_economy,
    production_gdp,
    real_gdp,
    recession_years,
    statistical_discrepancy,
)

df = load_economy()
print(f"{year} 年の GDP: 生産 {production_gdp(df)[year]}、"
      f"分配 {income_gdp(df)[year]}、支出 {expenditure_gdp(df)[year]}")
print(f"統計上の不突合: {statistical_discrepancy(df)[year]}")
print(f"実質 GDP: {real_gdp(df)[year]:.1f}、"
      f"成長率: {growth_rates(real_gdp(df))[year]:.2f}%")
print(f"後退した年: {recession_years(df)}")
expenditure_shares(df, year).round(1)
"""
        ),
        markdown("## 物価指数"),
        code(
            """
from lib.chapter11.economy import laspeyres_index, paasche_index

print(f"ラスパイレス指数: "
      f"{laspeyres_index(base_prices, base_quantities, current_prices):.1f}")
print(f"パーシェ指数: "
      f"{paasche_index(base_prices, current_prices, current_quantities):.1f}")
"""
        ),
        markdown(
            """
## 試してみよう

- `year` を 2020 や 2021 にすると、GDP・成長率・構成比が、その年のものに変わります。
  実質成長率がマイナスの年は、2013 と 2020 です（`year` を 2020 にして確かめます）
- `current_prices` を `[130, 190]` にすると、ラスパイレス指数は 102.5 から 112.5 に
  なります。`[110, 150]` にすると、92.5 に下がります
- 基準年と比較年の数量が同じでない（`base_quantities` と `current_quantities` が
  違う）ので、ラスパイレス指数（102.5）とパーシェ指数（101.0）は、少し違います
"""
        ),
    ]


def ch12_plotting_with_pandas() -> list[NotebookNode]:
    return [
        intro("第 12 章 Pandas による図示", "12-plotting-with-pandas"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
first_year = 2010   # 図に描く、最初の年（2010〜2021）
window = 3          # 移動平均の窓の幅（年数）
""",
            parameters=True,
        ),
        markdown("## 移動平均と、景気動向指数"),
        code(
            """
from lib.chapter11.economy import load_economy, real_gdp
from lib.chapter12.charts import diffusion_index, moving_average

df = load_economy().loc[first_year:]
average = moving_average(real_gdp(df), window)
print(f"実質 GDP の移動平均（窓 {window}）の最後の 3 年:")
print(average.tail(3).round(1).to_string())
print(f"景気動向指数（DI）: {diffusion_index(df).round(1).tolist()}")
"""
        ),
        markdown("## 図: 名目 GDP と実質 GDP"),
        code(
            """
from lib.chapter12.charts import plot_gdp_chart

plot_gdp_chart(df)
"""
        ),
        markdown("## 図: 実質成長率"),
        code(
            """
from lib.chapter12.charts import plot_growth_chart

plot_growth_chart(df)
"""
        ),
        markdown(
            """
## 試してみよう

- `window` を 1 にすると、移動平均は実質 GDP そのもの（最後の 3 年は 580.4、563.1、
  577.0）になります。3 だと 573.5 まで、5 だと 569.5 までなめらかになります
  （いずれも、最後の年の値）
- `first_year` を 2015 にすると、図の横軸が 2015 年からになります
"""
        ),
    ]


def ch13_is_lm_analysis() -> list[NotebookNode]:
    return [
        intro("第 13 章 IS-LM 分析", "13-is-lm-analysis"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
autonomous_consumption = 100  # C0: 基礎消費
mpc = 0.8                     # c: 限界消費性向
tax = 50                      # T: 定額税
autonomous_investment = 140   # I0: 利子率が 0 のときの投資
investment_sensitivity = 10   # b: 投資の利子率感応度
government = 100              # G: 政府支出
money_supply = 525            # M: 名目貨幣供給
price_level = 1               # P: 物価水準
money_income_sensitivity = 0.5      # k: 貨幣需要の所得感応度
money_interest_sensitivity = 20     # h: 貨幣需要の利子率感応度
interest_floor = None         # 利子率の下限（流動性のわな）。例: 2
government_after = 100        # 政策後の政府支出（財政政策）
money_supply_after = 525      # 政策後の貨幣供給（金融政策）
""",
            parameters=True,
        ),
        markdown("## IS-LM の均衡と、政策の効果"),
        code(
            """
import dataclasses

from lib.chapter13.islm import IsLmModel, solve_equilibrium

model = IsLmModel(
    autonomous_consumption=autonomous_consumption,
    mpc=mpc,
    tax=tax,
    autonomous_investment=autonomous_investment,
    investment_sensitivity=investment_sensitivity,
    government=government,
    money_supply=money_supply,
    price_level=price_level,
    money_income_sensitivity=money_income_sensitivity,
    money_interest_sensitivity=money_interest_sensitivity,
    interest_floor=interest_floor,
)
after = dataclasses.replace(
    model, government=government_after, money_supply=money_supply_after
)
income, rate = solve_equilibrium(model)
income_after, rate_after = solve_equilibrium(after)
print(f"政策前: 所得 {income:.1f}、利子率 {rate:.2f}")
print(f"政策後: 所得 {income_after:.1f}、利子率 {rate_after:.2f}")
"""
        ),
        markdown("## 図: IS 曲線と LM 曲線"),
        code(
            """
from lib.chapter13.islm import plot_islm

plot_islm(model, after)
"""
        ),
        markdown(
            """
## 試してみよう

- `government_after` を 150 にすると、所得は 1250 から 1361.1 に、利子率は 5.00 から
  7.78 に上がります（クラウディングアウト: 利子率が上がって、投資が減ります）
- `money_supply_after` を 625 にすると、所得は 1361.1 に増え、利子率は 2.78 に
  下がります
- `interest_floor` を 2 にして、`money_supply_after` を 2000 にすると、利子率は
  下限の 2.00 に張り付き、所得は 1400 で止まります。3000 にしても、1400 のままです
  （流動性のわな: 金融政策が効きません）
- `interest_floor` を 2、`money_supply` と `money_supply_after` を 2000 にして、
  `government_after` を 120 にすると、所得は 100 増えます（クラウディングアウトが
  なく、乗数どおり）
"""
        ),
    ]


def ch14_ad_as_and_major_theories() -> list[NotebookNode]:
    return [
        intro("第 14 章 AD-AS 分析と主要理論", "14-ad-as-and-major-theories"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
government = 100               # IS-LM の政府支出 G
money_supply = 525             # IS-LM の名目貨幣供給 M
government_after = 100         # 図: 政策後の政府支出
full_employment_income = 1250  # 完全雇用所得（古典派の総供給は、ここで垂直）
natural_rate = 4               # フィリップス曲線: 自然失業率（%）
expected_inflation = 2         # 期待物価上昇率（%）
phillips_slope = 0.5           # フィリップス曲線の傾き
unemployment = 2               # 失業率（%）
actual_gdp = 980               # 需給ギャップ: 実際の GDP
potential_gdp = 1000           # 潜在 GDP
nominal_rate = 5               # フィッシャー方程式: 名目利子率（%）
inflation = 2                  # インフレ率（%）
nominal_money = 500            # 貨幣数量説: 貨幣供給 M
velocity = 2                   # 貨幣の流通速度 V
real_income = 1000             # 実質所得 Y
""",
            parameters=True,
        ),
        markdown("## AD-AS 分析"),
        code(
            """
import dataclasses

from lib.chapter13.islm import IsLmModel
from lib.chapter14.adas import classical_supply, equilibrium_price_and_income

model = IsLmModel(government=government, money_supply=money_supply)
after = dataclasses.replace(model, government=government_after)
price, income = equilibrium_price_and_income(
    model, lambda p: classical_supply(p, full_employment_income)
)
price_after, income_after = equilibrium_price_and_income(
    after, lambda p: classical_supply(p, full_employment_income)
)
print(f"均衡: 物価 {price:.3f}、所得 {income:.1f}")
print(f"政策後: 物価 {price_after:.3f}、所得 {income_after:.1f}")
"""
        ),
        code(
            """
from lib.chapter14.plot import plot_adas

plot_adas(model, full_employment_income, after)
"""
        ),
        markdown("## フィリップス曲線・需給ギャップ・オークンの法則・その他"),
        code(
            """
from lib.chapter14.indicators import (
    okun_unemployment,
    output_gap,
    phillips_inflation,
    price_level_by_quantity_theory,
    real_interest_rate,
)

inflation_rate = phillips_inflation(
    unemployment, natural_rate, expected_inflation, phillips_slope
)
print(f"物価上昇率（フィリップス曲線）: {inflation_rate:.2f}%")
gap = output_gap(actual_gdp, potential_gdp)
print(f"需給ギャップ: {gap:.2f}%")
print(f"失業率（オークンの法則）: {okun_unemployment(gap, natural_rate):.2f}%")
print(f"実質利子率: {real_interest_rate(nominal_rate, inflation):.2f}%")
print(f"物価水準（貨幣数量説）: "
      f"{price_level_by_quantity_theory(nominal_money, velocity, real_income):.2f}")
"""
        ),
        code(
            """
from lib.chapter14.plot import plot_phillips_curve

plot_phillips_curve(natural_rate, expected_inflation, phillips_slope)
"""
        ),
        markdown(
            """
## 試してみよう

- `government_after` を 150 にすると、古典派の総供給は垂直なので、所得は 1250 の
  まま、物価だけが 1.000 から 1.235 に上がります（財政政策は、物価を上げるだけ）
- `full_employment_income` を 1300 にすると、均衡の物価は 0.921 に下がり、所得は
  1300 になります
- `unemployment` を 6 にすると、物価上昇率は 1.00%、2 だと 3.00% です
  （失業率が低いほど、物価上昇率が高い）。`phillips_slope` を 1 にすると、2 のとき
  4.00% です
- `actual_gdp` を 1020 にすると、需給ギャップは 2.00%、失業率は 3.00% になります
- `nominal_money` を 1000 にすると、物価水準は 1.00 から 2.00 になります
  （貨幣供給が 2 倍で、物価も 2 倍）。`nominal_rate` が 5 で `inflation` が 6 なら、
  実質利子率は -1.00% です
"""
        ),
    ]


def ch15_imperfect_competition_and_game_theory() -> list[NotebookNode]:
    return [
        intro(
            "第 15 章 不完全競争とゲーム理論",
            "15-imperfect-competition-and-game-theory",
        ),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
demand_intercept = 100  # 需要 Q = a - bP の切片 a
demand_slope = 2        # 需要の傾き b
marginal_cost = 10      # 限界費用（一定）
firms = 2               # クールノー競争の企業数
supply_intercept = 0    # 外部不経済: 私的な供給 Q = c + dP の切片 c
supply_slope = 3        # 私的な供給の傾き d
external_cost = 5       # 外部費用（1 単位あたり）
both_cooperate = 3      # ゲーム: 2 人とも協力したときの、利得
temptation = 5          # 自分だけ裏切ったときの、利得
sucker = 0              # 自分だけ協力したときの、利得
both_defect = 1         # 2 人とも裏切ったときの、利得
""",
            parameters=True,
        ),
        markdown("## 独占"),
        code(
            """
from lib.chapter15.monopoly import competitive_quantity, lerner_index, monopoly_outcome

outcome = monopoly_outcome(demand_intercept, demand_slope, marginal_cost)
print(f"独占: 数量 {outcome.quantity:.2f}、価格 {outcome.price:.2f}、"
      f"利潤 {outcome.profit:.2f}")
print(f"消費者余剰 {outcome.consumer_surplus:.2f}、"
      f"死荷重 {outcome.deadweight_loss:.2f}")
print(f"競争の数量: "
      f"{competitive_quantity(demand_intercept, demand_slope, marginal_cost):.2f}")
print(f"ラーナー指数: {lerner_index(outcome.price, marginal_cost):.3f}")
"""
        ),
        code(
            """
from lib.chapter15.plot import plot_monopoly

plot_monopoly(demand_intercept, demand_slope, marginal_cost)
"""
        ),
        markdown("## 寡占（クールノー競争）"),
        code(
            """
from lib.chapter15.oligopoly import cournot_by_iteration, cournot_symmetric

q1, q2 = cournot_by_iteration(demand_intercept, demand_slope, marginal_cost)
print(f"2 社の反復で求めた均衡: {q1:.2f}、{q2:.2f}")
quantity, price, profit = cournot_symmetric(
    firms, demand_intercept, demand_slope, marginal_cost
)
print(f"{firms} 社: 各社の数量 {quantity:.2f}、価格 {price:.2f}、"
      f"各社の利潤 {profit:.2f}")
"""
        ),
        code(
            """
from lib.chapter15.plot import plot_cournot

plot_cournot(demand_intercept, demand_slope, marginal_cost)
"""
        ),
        markdown("## 外部不経済とピグー税"),
        code(
            """
from lib.chapter15.externality import (
    externality_deadweight_loss,
    social_optimum_quantity,
)

market = (demand_intercept, demand_slope, supply_intercept, supply_slope)
print(f"社会的に最適な数量: {social_optimum_quantity(*market, external_cost):.2f}")
print(f"死荷重: {externality_deadweight_loss(*market, external_cost):.2f}")
"""
        ),
        code(
            """
from lib.chapter15.plot import plot_externality

plot_externality(*market, external_cost)
"""
        ),
        markdown("## ゲーム理論"),
        code(
            """
from lib.chapter15.game import pure_nash_equilibria

payoffs = {
    ("協力", "協力"): (both_cooperate, both_cooperate),
    ("協力", "裏切り"): (sucker, temptation),
    ("裏切り", "協力"): (temptation, sucker),
    ("裏切り", "裏切り"): (both_defect, both_defect),
}
print("ナッシュ均衡:", pure_nash_equilibria(payoffs))
"""
        ),
        markdown(
            """
## 試してみよう

- `marginal_cost` を 20 にすると、独占の数量は 40 から 30 に、価格は 30 から 35 に、
  利潤は 800 から 450 になります。`demand_slope` を 4 にすると、数量は 30、価格は
  17.50 です（`marginal_cost` は 10 のまま）
- `firms` を 1 にすると、独占と同じ（数量 40、価格 30、利潤 800）です。10 にすると、
  各社の数量は 7.27、価格は 13.64、各社の利潤は 26.45 に下がり、競争に近づきます
  （2 社なら、26.67、23.33、355.56）
- `external_cost` を 10 にすると、最適な数量は 54 から 48 に、死荷重は 15 から 60 に
  なります。0 にすると、死荷重は 0 です
- `both_cooperate` を 6 にすると、ナッシュ均衡が 2 つ（協力・協力と、裏切り・裏切り）
  になります（3 のときは、裏切り・裏切りだけ）
"""
        ),
    ]


def appendix_a_bridge_to_regression() -> list[NotebookNode]:
    return [
        intro("付録 A 回帰分析への橋渡し", "appendix-a-bridge-to-regression"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
true_intercept = 100  # 真の需要曲線 Q = a - bP の切片 a
true_slope = 2        # 真の傾き b
sigma = 10            # 観測値のばらつき（標準偏差）
per_price = 50        # 価格ごとの観測値の個数
seed = 0              # 乱数の種
""",
            parameters=True,
        ),
        markdown("## シミュレーションで作ったデータから、需要曲線を推定する"),
        code(
            """
import random

from lib.appendix_a.regression import fit_line, r_squared
from lib.chapter08.simulation import simulate_demand

rng = random.Random(seed)
prices: list[float] = []
quantities: list[float] = []
for price in range(5, 21):
    observations = simulate_demand(
        price, true_intercept, true_slope, sigma, per_price, rng
    )
    prices.extend([float(price)] * len(observations))
    quantities.extend(observations)
intercept, slope = fit_line(prices, quantities)
print(f"観測値の数: {len(prices)}")
print(f"推定: 切片 {intercept:.3f}、傾き {slope:.3f}"
      f"（真の値 {true_intercept}、{-true_slope}）")
print(f"決定係数 R²: {r_squared(prices, quantities):.4f}")
"""
        ),
        markdown(
            """
## 試してみよう

- `sigma` を 0 にすると、推定は真の値そのもの（切片 100、傾き -2）で、決定係数は
  1 になります。5 では R² が 0.7751、10 では 0.4561、30 では 0.0768 と、ばらつきが
  大きいほど、決定係数は小さくなります
- `sigma` が 30 でも、傾きの推定値は -1.839 で、真の値 -2 の近くにあります
  （決定係数が小さくても、傾きは、おおよそ当たります）
- `seed` を 1 にする（`sigma` は 10）と、推定は、切片 101.430、傾き -2.107 に
  変わります（乱数が違えば、推定も少しずれます）
"""
        ),
    ]


NOTEBOOKS: dict[str, Callable[[], list[NotebookNode]]] = {
    "ch01_preparation_and_first_test": ch01_preparation_and_first_test,
    "ch02_data_types_and_variables": ch02_data_types_and_variables,
    "ch03_containers_and_data_operations": ch03_containers_and_data_operations,
    "ch04_functions_and_methods": ch04_functions_and_methods,
    "ch05_control_flow": ch05_control_flow,
    "ch06_modules_errors_and_algorithms": ch06_modules_errors_and_algorithms,
    "ch07_plotting_with_matplotlib": ch07_plotting_with_matplotlib,
    "ch08_random_numbers_and_simulation": ch08_random_numbers_and_simulation,
    "ch09_numpy_arrays": ch09_numpy_arrays,
    "ch10_optimization_with_scipy": ch10_optimization_with_scipy,
    "ch11_data_analysis_with_pandas": ch11_data_analysis_with_pandas,
    "ch12_plotting_with_pandas": ch12_plotting_with_pandas,
    "ch13_is_lm_analysis": ch13_is_lm_analysis,
    "ch14_ad_as_and_major_theories": ch14_ad_as_and_major_theories,
    "ch15_imperfect_competition_and_game_theory": (
        ch15_imperfect_competition_and_game_theory
    ),
    "appendix_a_bridge_to_regression": appendix_a_bridge_to_regression,
}


def main() -> None:
    for name, build in sorted(NOTEBOOKS.items()):
        path = NOTEBOOKS_DIR / f"{name}.ipynb"
        write(path, build())
        print(f"生成: {path.name}")


if __name__ == "__main__":
    main()
