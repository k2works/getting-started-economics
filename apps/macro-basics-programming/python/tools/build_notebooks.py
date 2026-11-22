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
ARTICLES = "docs/article/macro-basics-programming"
HOW_TO_RUN = (
    "**使い方**: 「Parameters」のセルの数字を書き換えて、上から順に実行します"
    "（メニューの Run → Run All Cells）。数字を変えるたびに、結果と図が変わります。\n\n"
    "起動: アプリのディレクトリで `uv run --with jupyterlab jupyter lab notebooks/` "
    "を実行します。"
)


def _intro(title: str, article: str) -> NotebookNode:
    """先頭の説明のセル。章のタイトル、使い方、記事のパス。"""
    return markdown(
        f"# {title}: 数字を変えて確かめる\n\n{HOW_TO_RUN}\n\n"
        f"記事: `{ARTICLES}/{article}`"
    )


def ch01_gdp_and_value_added() -> list[NotebookNode]:
    return [
        _intro("第 1 章 GDP と付加価値", "01-gdp-and-value-added.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
stages = ["Wheat", "Flour", "Bread"]  # 生産の段階（小麦・小麦粉・パン）
output = [300, 700, 1000]             # 各段階の産出額
intermediate = [0, 300, 700]          # 各段階の中間投入
growth = 6.0            # 実質成長率（%）
labor_growth = 7.0      # 労働の増加率（%）
labor_share = 0.4       # 労働分配率
capital_growth = 4.0    # 資本の増加率（%）
capital_share = 0.6     # 資本分配率（労働分配率との合計を 1 にする）
""",
            parameters=True,
        ),
        markdown("## 付加価値と GDP"),
        code(
            """
from lib.chapter01.gdp import gdp_from_stages, growth_accounting, value_added

print("各段階の付加価値:", value_added(output, intermediate))
print("GDP（付加価値の合計）:", gdp_from_stages(output, intermediate))

result = growth_accounting(
    growth, labor_growth, labor_share, capital_growth, capital_share
)
print(f"成長率 {result.growth:.2f}% の内訳: 労働 {result.labor:.2f}、"
      f"資本 {result.capital:.2f}、技術進歩 {result.technology:.2f}")
"""
        ),
        markdown("## 図: 付加価値"),
        code(
            """
from lib.chapter01.plot import plot_value_added

plot_value_added(stages, output, intermediate)
"""
        ),
        markdown("## 図: 成長会計"),
        code(
            """
from lib.chapter01.plot import plot_growth_accounting

plot_growth_accounting(result)
"""
        ),
        markdown(
            """
## 試してみよう

- `growth = 8.0` にすると、技術進歩（残差）は 2.8 になります（6.0 のときは 0.8）。
  労働と資本で説明できない分が、技術進歩として残ります
- `labor_share = 0.5`、`capital_share = 0.5` にすると、労働 3.5、資本 2.0、技術進歩 0.5
  になります。分配率の合計が 1 でないと、エラーになります
- `output = [300, 700, 1200]` にすると、GDP は 1200 になります（1000 のときは 1000）。
  最終生産物の産出額が 200 増えると、GDP も 200 増えます
"""
        ),
    ]


def ch02_three_way_equivalence() -> list[NotebookNode]:
    return [
        _intro("第 2 章 三面等価と産業連関表", "02-three-way-equivalence.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
output = [100, 300, 500]        # 各産業の産出額
intermediate = [0, 100, 300]    # 各産業の中間投入
compensation = 280              # 雇用者報酬
operating_surplus = 120         # 営業余剰
depreciation = 80               # 固定資本減耗
indirect_taxes = 20             # 間接税（補助金は 0 とする）
consumption = 290               # 民間消費
government = 80                 # 政府消費
investment = 100                # 総固定資本形成
inventory = 10                  # 在庫品増加
net_exports = 20                # 純輸出
coefficients = [[0.2, 0.3], [0.4, 0.1]]  # 投入係数 A（行: 売り手、列: 買い手）
final_demand = [100, 200]       # 最終需要
""",
            parameters=True,
        ),
        markdown("## 三面等価"),
        code(
            """
from lib.chapter02.three_way import (
    gdp_distribution,
    gdp_expenditure,
    gdp_production,
    is_three_way_equal,
)

production = gdp_production(output, intermediate)
distribution = gdp_distribution(
    compensation, operating_surplus, depreciation, indirect_taxes, 0
)
expenditure = gdp_expenditure(
    consumption, government, investment, inventory, net_exports
)
print(f"生産面 {production}、分配面 {distribution}、支出面 {expenditure}")
equal = is_three_way_equal(production, distribution, expenditure)
print("三面等価が成り立つか:", equal)
"""
        ),
        markdown("## 図: 三面等価"),
        code(
            """
from lib.chapter02.plot import plot_three_way

plot_three_way(
    {
        "Production": {
            f"Industry {i + 1}": o - m
            for i, (o, m) in enumerate(zip(output, intermediate, strict=True))
        },
        "Distribution": {
            "Compensation": compensation,
            "Operating surplus": operating_surplus,
            "Depreciation": depreciation,
            "Taxes less subsidies": indirect_taxes,
        },
        "Expenditure": {
            "Consumption": consumption,
            "Government": government,
            "Investment": investment,
            "Inventory": inventory,
            "Net exports": net_exports,
        },
    }
)
"""
        ),
        markdown("## 産業連関表: 最終需要を満たす生産量"),
        code(
            """
from lib.chapter02.input_output import leontief_inverse, output_for_demand

print("レオンチェフ逆行列:")
print(leontief_inverse(coefficients).round(3))
print("必要な生産量:", output_for_demand(coefficients, final_demand).round(1))
"""
        ),
        code(
            """
from lib.chapter02.plot import plot_io_output

plot_io_output(coefficients, final_demand, ["Manufacturing", "Services"])
"""
        ),
        markdown(
            """
## 試してみよう

- `inventory = 30` にすると、支出面は 520 になり、生産面・分配面（500）と
  ずれて、「三面等価が成り立つか」は `False` になります。売れ残り（在庫）は、
  支出に数えるので、帳尻は在庫で合います
- `final_demand = [200, 200]` にすると、必要な生産量は [400.0, 400.0] になります
  （[100, 200] のときは [250.0, 333.3]）。最終需要の増加は、中間投入を通じて、
  それ以上の生産を呼びます
- `coefficients = [[0.4, 0.3], [0.4, 0.1]]` にすると、必要な生産量は
  [357.1, 381.0] に増えます。投入係数が大きい（原材料を多く使う）ほど、生産が膨らみます
"""
        ),
    ]


def ch03_price_indexes_and_indicators() -> list[NotebookNode]:
    return [
        _intro(
            "第 3 章 物価指数と景気・雇用の指標", "03-price-indexes-and-indicators.md"
        ),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
periods = ["2020", "2021", "2022"]
bread_prices = [100, 110, 121]      # パンの価格
milk_prices = [200, 180, 170]       # 牛乳の価格
bread_quantities = [10, 12, 14]     # パンの数量
milk_quantities = [5, 4, 3]         # 牛乳の数量
base_period = "2020"                # 物価指数の基準時
nominal_gdp = 550                   # 名目 GDP
deflator = 110                      # GDP デフレータ（基準時 = 100）
employed = 6700                     # 就業者
unemployed = 200                    # 完全失業者
base_month = "2025-01"              # 景気動向指数 CI の基準の月（= 100）
""",
            parameters=True,
        ),
        markdown("## 物価指数・実質 GDP・失業率"),
        code(
            """
import pandas as pd

from lib.chapter03.indicators import unemployment_rate
from lib.chapter03.price_index import price_indexes, real_gdp

prices = pd.DataFrame({"bread": bread_prices, "milk": milk_prices}, index=periods)
quantities = pd.DataFrame(
    {"bread": bread_quantities, "milk": milk_quantities}, index=periods
)
table = price_indexes(prices, quantities, base=base_period)
print(table)
print("実質 GDP:", real_gdp(nominal_gdp, deflator))
print(f"完全失業率: {unemployment_rate(employed, unemployed):.2f}%")
"""
        ),
        markdown("## 図: 物価指数"),
        code(
            """
from lib.chapter03.plot import plot_price_indexes

plot_price_indexes(table)
"""
        ),
        markdown("## 景気動向指数（DI・CI）"),
        code(
            """
from pathlib import Path

from lib.chapter03.indicators import composite_index, diffusion_index, load_indicators

# アプリのディレクトリからでも、notebooks/ からでも、data/ を見つける
data_dir = Path("data") if Path("data").exists() else Path("../data")
indicators = load_indicators(data_dir / "ch03_indicators.csv")
di = diffusion_index(indicators)
ci = composite_index(indicators, base=base_month)
print(f"最後の月の CI（{base_month} = 100）: {ci.iloc[-1]:.2f}")
"""
        ),
        code(
            """
from lib.chapter03.plot import plot_business_indexes

plot_business_indexes(di, ci)
"""
        ),
        markdown(
            """
## 試してみよう

- 数量を一定にする（`bread_quantities = [10, 10, 10]`、
  `milk_quantities = [5, 5, 5]`）と、
  ラスパイレス指数とパーシェ指数は、2022 年にどちらも 1.03 で一致します
  （もとは 1.03 と 1.102）。**2 つの指数が食い違うのは、数量が変わるから**です
- `nominal_gdp = 550`、`deflator = 110` のとき、実質 GDP は 500.0 です
  （デフレータを 100 にすると、名目と実質が同じ 550 になります）
- `base_month = "2025-06"` にすると、最後の月の CI は 97.49 になります
  （`2025-01` のときは 104.82）。基準の月を変えると、100 の位置が動きます
"""
        ),
    ]


def ch04_45_degree_line_and_multiplier() -> list[NotebookNode]:
    return [
        _intro("第 4 章 45 度線分析と乗数", "04-45-degree-line-and-multiplier.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
mpc = 0.6                    # 限界消費性向 c（0 以上 1 未満）
autonomous_consumption = 40  # 基礎消費 C0
investment = 30              # 投資 I
government = 30              # 政府支出 G
net_exports = 0              # 純輸出 X
tax = 0                      # 租税 T（定額）
delta_government = 10        # 政府支出の変化 ΔG
delta_tax = 0                # 租税の変化 ΔT
mpc_high = 0.8               # 比べる、もう 1 つの限界消費性向
""",
            parameters=True,
        ),
        markdown("## 均衡国民所得と乗数"),
        code(
            """
from lib.chapter04.multiplier import (
    balanced_budget_multiplier,
    equilibrium_income,
    income_change,
    spending_multiplier,
    tax_multiplier,
)

y = equilibrium_income(
    mpc, autonomous_consumption, investment, government, net_exports, tax
)
print(f"均衡国民所得: {y:.2f}")
print(f"政府支出乗数 {spending_multiplier(mpc):.2f}、"
      f"租税乗数 {tax_multiplier(mpc):.2f}、"
      f"均衡予算乗数 {balanced_budget_multiplier(mpc):.2f}")
print(f"所得の変化: {income_change(mpc, delta_government, delta_tax):.2f}")
"""
        ),
        markdown("## 図: 45 度線"),
        code(
            """
from lib.chapter04.plot import plot_keynesian_cross

plot_keynesian_cross(
    mpc=mpc,
    autonomous_consumption=autonomous_consumption,
    investment=investment,
    government=government,
    net_exports=net_exports,
    income_max=400,
    tax=tax,
)
"""
        ),
        markdown("## 図: 限界消費性向と総需要の傾き"),
        code(
            """
from lib.chapter04.plot import plot_multiplier_slopes

plot_multiplier_slopes([mpc, mpc_high], autonomous=100, income_max=500)
"""
        ),
        markdown(
            """
## 試してみよう

- `mpc = 0.8` にすると、均衡国民所得は 500.00 になります（0.6 のときは 250.00）。
  乗数が 2.5 から 5 に大きくなるからです
- `tax = 10` にすると、均衡国民所得は 235.00 に下がります（租税は消費を減らします）
- `government = 40` にすると、均衡国民所得は 275.00 になります（`+10` で `+25`）
- `delta_tax = 10` にして、`delta_government = 10` のままにすると、
  所得の変化は 10.00 です。
  同じ額だけ増税して使う（**均衡予算乗数は 1**）と、所得は、その額だけ増えます
"""
        ),
    ]


def ch05_gaps_and_stabilization() -> list[NotebookNode]:
    return [
        _intro("第 5 章 ギャップと安定化政策", "05-gaps-and-stabilization.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
mpc = 0.6                    # 限界消費性向 c
autonomous = 100             # 独立支出 A（均衡所得 = A ÷ (1 − c)）
full_employment_income = 300 # 完全雇用所得
tax_rate = 0.2               # 比例税の税率 t（ビルトイン・スタビライザー）
shock = 10                   # 独立支出の変動
""",
            parameters=True,
        ),
        markdown("## ギャップと、必要な政策"),
        code(
            """
from lib.chapter05.stabilization import (
    classify_gap,
    income_swing,
    output_gap,
    required_spending_change,
    required_tax_change,
    stabilizer_multiplier,
    swing_reduction,
)

equilibrium = autonomous / (1 - mpc)
gap = output_gap(full_employment_income, equilibrium)
print(f"均衡所得 {equilibrium:.1f}、ギャップ {gap:.1f}（{classify_gap(gap)}）")
print(f"必要な政府支出の変化 {required_spending_change(gap, mpc):.2f}、"
      f"必要な租税の変化 {required_tax_change(gap, mpc):.2f}")
print(f"乗数 {stabilizer_multiplier(mpc, tax_rate):.3f}、"
      f"所得の振れ幅 {income_swing(mpc, tax_rate, shock):.2f}、"
      f"振れ幅の縮小 {swing_reduction(mpc, tax_rate):.1%}")
"""
        ),
        markdown("## 図: ギャップ"),
        code(
            """
from lib.chapter05.plot import plot_gap

plot_gap(mpc, autonomous, full_employment_income, income_max=400)
"""
        ),
        markdown("## 図: ビルトイン・スタビライザー"),
        code(
            """
from lib.chapter05.plot import plot_income_swing

plot_income_swing(mpc, tax_rate, shock)
"""
        ),
        markdown(
            """
## 試してみよう

- `full_employment_income = 200` にすると、ギャップは −50.0 で、**インフレギャップ**に
  なります（300 のときは、50.0 のデフレギャップ）
- `tax_rate = 0` にすると、所得の振れ幅は 25.00 です（0.2 のときは 19.23 で、
  23.1% 縮みます）。比例税が、景気の振れを小さくします
- `mpc = 0.8` にすると、均衡所得は 500、ギャップは −200 で、振れ幅は 27.78 に
  なります（`tax_rate = 0.2` のまま）。消費性向が高いほど、振れが大きくなります
"""
        ),
    ]


def ch06_money_supply() -> list[NotebookNode]:
    return [
        _intro("第 6 章 貨幣供給と貨幣乗数", "06-money-supply.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
base = 110              # ハイパワードマネー H
cash_ratio = 0.1        # 現金預金比率 C/D
reserve_ratio = 0.01    # 準備預金比率 R/D
operation_amount = 10   # 公開市場操作の額
rounds = 40             # 信用創造のラウンド数
reserve_ratios = [0.01, 0.05, 0.1]  # 図で比べる準備預金比率
""",
            parameters=True,
        ),
        markdown("## 貨幣乗数とマネーストック"),
        code(
            """
from lib.chapter06.money_supply import (
    credit_creation_path,
    money_multiplier,
    money_stock,
    open_market_operation,
)

print(f"貨幣乗数: {money_multiplier(cash_ratio, reserve_ratio):.3f}")
print(f"マネーストック: {money_stock(cash_ratio, reserve_ratio, base):.1f}")
bought = open_market_operation(base, operation_amount, "買いオペ")
after = money_stock(cash_ratio, reserve_ratio, bought)
print(f"買いオペ後のマネーストック: {after:.1f}")
path = credit_creation_path(base, cash_ratio, reserve_ratio, rounds)
print(f"信用創造 {rounds} ラウンド後: {path[-1]:.1f}")
"""
        ),
        markdown("## 図: 貨幣乗数"),
        code(
            """
from lib.chapter06.plot import plot_money_multiplier

plot_money_multiplier([i / 100 for i in range(0, 51)], reserve_ratios)
"""
        ),
        markdown("## 図: 信用創造"),
        code(
            """
from lib.chapter06.plot import plot_credit_creation

plot_credit_creation(base, cash_ratio, reserve_ratio, rounds)
"""
        ),
        markdown(
            """
## 試してみよう

- `reserve_ratio = 0.05` にすると、マネーストックは 806.7 になります
  （0.01 のときは 1100.0）。準備率を上げると、信用創造が縮みます
- `cash_ratio = 0.2` にすると、貨幣乗数は 5.714、マネーストックは 628.6 になります。
  現金で持つ割合が増えると、銀行に預金が戻らず、乗数が下がります
- `operation_amount = 10` の買いオペで、ハイパワードマネーは 120 になり、
  マネーストックは 1200.0 になります（乗数 10 × 120）
- `rounds = 10` にすると、信用創造は 716.5 で止まります（40 ラウンドでは 1083.7。
  ラウンドを重ねるほど、`貨幣乗数 × H` = 1100 に近づきます）
"""
        ),
    ]


def ch07_money_demand_and_lm() -> list[NotebookNode]:
    return [
        _intro("第 7 章 貨幣需要と LM 曲線", "07-money-demand-and-lm.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
income = 1000          # 所得 Y
income_after = 1200    # 所得が増えたあとの Y
real_money = 250       # 実質貨幣供給 M/P
real_money_after = 300 # 増やしたあとの実質貨幣供給
k = 0.5                # 貨幣需要の所得感応度 k（L = kY − hr）
h = 100                # 貨幣需要の利子感応度 h
floor = 2.0            # 流動性のわなの、利子率の下限
interest_max = 5       # 図の、利子率の上限
""",
            parameters=True,
        ),
        markdown("## 貨幣需要と LM 曲線"),
        code(
            """
from lib.chapter07.liquidity import lm_shift, money_demand_shift, trap_income
from lib.chapter07.money_market import lm_interest, lm_slope, money_demand

print(f"貨幣需要 L（r = 2.5）: {money_demand(income, 2.5, k, h):.1f}")
print(f"均衡の利子率（LM 曲線上）: {lm_interest(income, real_money, k, h):.2f}")
print(f"LM 曲線の傾き: {lm_slope(k, h):.4f}")
print(f"所得の増加による、貨幣需要曲線のシフト幅: "
      f"{money_demand_shift(income, income_after, k):.1f}")
print(f"実質貨幣供給の増加による、LM 曲線のシフト幅: "
      f"{lm_shift(real_money, real_money_after, k):.1f}")
print(f"流動性のわなの、所得の上限: {trap_income(real_money, k, h, floor):.1f}")
"""
        ),
        markdown("## 図: 貨幣市場"),
        code(
            """
from lib.chapter07.plot import plot_money_market

plot_money_market(income, income_after, real_money, k, h, interest_max)
"""
        ),
        markdown("## 図: LM 曲線"),
        code(
            """
from lib.chapter07.plot import plot_lm_curves

plot_lm_curves(
    incomes=list(range(600, 1501, 100)),
    real_money=real_money,
    real_money_after=real_money_after,
    k=k,
    h=h,
    floor=floor,
)
"""
        ),
        markdown(
            """
## 試してみよう

- `real_money = 300` にすると、均衡の利子率は 2.00 に下がります（250 のときは 2.50）。
  貨幣供給が増えると、利子率が下がります
- `h = 200` にすると、LM 曲線の傾きは 0.0025 になります（100 のときは 0.0050）。
  利子感応度が大きいほど、LM 曲線は緩やかです
- `income = 1200` にすると、均衡の利子率は 3.50 に上がります。所得が増えると、
  取引のための貨幣需要が増えるからです
- `floor = 2.0` のとき、流動性のわなの所得の上限は 900.0 です
"""
        ),
    ]


def ch08_is_curve_and_is_lm() -> list[NotebookNode]:
    return [
        _intro("第 8 章 IS 曲線と IS-LM の均衡", "08-is-curve-and-is-lm.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
mpc = 0.6          # 限界消費性向 c
b = 20             # 投資の利子感応度 b
b_high = 40        # 図で比べる、もう 1 つの b
intercept = 450    # IS 曲線の A（C0 − cT + I0 + G）
k = 0.5            # 貨幣需要の所得感応度 k
h = 100            # 貨幣需要の利子感応度 h
real_money = 250   # 実質貨幣供給 M/P
""",
            parameters=True,
        ),
        markdown("## IS-LM の均衡"),
        code(
            """
from lib.chapter08.is_lm import is_lm_residuals, is_slope, solve_is_lm

income, interest = solve_is_lm(mpc, b, intercept, k, h, real_money)
print(f"均衡: 所得 {income:.1f}、利子率 {interest:.2f}")
print(f"IS 曲線の傾き: {is_slope(mpc, b):.3f}")
residuals = is_lm_residuals(income, interest, mpc, b, intercept, k, h, real_money)
print("IS・LM の式の残差（均衡では 0）:", [round(r, 9) for r in residuals])
"""
        ),
        markdown("## 図: IS 曲線"),
        code(
            """
from lib.chapter08.plot import plot_is_curves

plot_is_curves(mpc, intercept, [b, b_high], interest_max=10)
"""
        ),
        markdown("## 図: IS-LM の均衡"),
        code(
            """
from lib.chapter08.plot import plot_is_lm_equilibrium

plot_is_lm_equilibrium(
    mpc, b, intercept, k, h, real_money, income_min=600, income_max=1200
)
"""
        ),
        markdown(
            """
## 試してみよう

- `b = 40` にすると、均衡は 所得 916.7、利子率 2.08 になります
  （`b = 20` のときは 1000.0 と 2.50）。投資が利子率に敏感だと、IS 曲線が緩やかで、
  LM 曲線との交点が、左下に動きます
- `real_money = 300` にすると、均衡は 所得 1020.0、利子率 2.10 になります
  （LM 曲線が右へ動きます）
- `intercept = 460`（政府支出を 10 増やす）にすると、均衡は 所得 1020.0、利子率 2.60
  になります（IS 曲線が右へ動きます）。所得は、同じ 1020 でも、利子率が違います
- `mpc = 0.8` にすると、均衡は 所得 1666.7、利子率 5.83 です。IS 曲線が、ぐっと
  右へ寄ります（図の範囲（1200 まで）を超えるので、図のセルの `income_max` も
  大きくしてください）
"""
        ),
    ]


def ch09_fiscal_and_monetary_policy() -> list[NotebookNode]:
    return [
        _intro("第 9 章 財政政策と金融政策の効果", "09-fiscal-and-monetary-policy.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
mpc = 0.6                # 限界消費性向 c
b = 20                   # 投資の利子感応度 b
intercept = 450          # IS 曲線の A
k = 0.5                  # 貨幣需要の所得感応度 k
h = 100                  # 貨幣需要の利子感応度 h
real_money = 250         # 実質貨幣供給 M/P
delta_government = 10    # 政府支出の増加 ΔG
delta_real_money = 10    # 実質貨幣供給の増加 Δ(M/P)
trap_interest = 2.5      # 流動性のわなの、利子率の下限
""",
            parameters=True,
        ),
        markdown("## 政策の効果"),
        code(
            """
from lib.chapter09.policy import (
    crowding_out,
    fiscal_effect,
    fiscal_effect_solved,
    monetary_effect,
    monetary_effect_solved,
)

fiscal = fiscal_effect(mpc, b, k, h, delta_government)
fiscal_solved = fiscal_effect_solved(
    mpc, b, intercept, k, h, real_money, delta_government
)
monetary = monetary_effect(mpc, b, k, h, delta_real_money)
monetary_solved = monetary_effect_solved(
    mpc, b, intercept, k, h, real_money, delta_real_money
)
print(f"財政政策の効果 ΔY: {fiscal:.2f}（連立方程式を解くと {fiscal_solved:.2f}）")
print(f"金融政策の効果 ΔY: {monetary:.2f}（連立方程式を解くと {monetary_solved:.2f}）")
print(f"クラウディングアウト: {crowding_out(mpc, b, k, h, delta_government):.2f}")
"""
        ),
        markdown("## 条件ごとの比較（h が無限大 = 流動性のわな）"),
        code(
            """
import math

from lib.chapter09.policy import policy_effectiveness

conditions = [(h, b), (10, b), (1000, b), (math.inf, b)]
rows = policy_effectiveness(mpc, k, conditions, delta_government, delta_real_money)
for row in rows:
    print(f"h={row.h}, b={row.b}: 財政 {row.fiscal:.2f}、金融 {row.monetary:.2f}、"
          f"クラウディングアウト {row.crowding_out:.2f}")
"""
        ),
        markdown("## 図: 政策による曲線のシフト"),
        code(
            """
from lib.chapter09.plot import plot_policy_shifts

plot_policy_shifts(
    mpc, b, intercept, k, h, real_money, delta_government, delta_real_money,
    income_min=600, income_max=1200,
)
"""
        ),
        markdown("## 図: 流動性のわな"),
        code(
            """
from lib.chapter09.plot import plot_liquidity_trap

plot_liquidity_trap(
    mpc, b, intercept, trap_interest, delta_government, income_min=600, income_max=1200
)
"""
        ),
        markdown(
            """
## 試してみよう

- 条件の表の `h = 10`（貨幣需要が利子に鈍い）では、財政 7.14、金融 14.29、
  クラウディングアウト 17.86 です（`h = 100` では、20.00、4.00、5.00）。
  LM 曲線が急だと、財政政策は効きにくく、金融政策が効きます
- `h = 1000` では、財政 24.39、金融 0.49 です。LM 曲線が水平に近いと、
  財政政策がほぼ単純な乗数どおりに効き、金融政策は効きません。
  `h = math.inf`（流動性のわな）では、財政 25.00（= 1 ÷ (1 − c) × 10）、金融 0.00 です
- `b = 40` にすると、財政政策の効果は 16.67 に小さくなります（`b = 20` では 20.00）。
  投資が利子に敏感だと、クラウディングアウトが大きくなります
- 「連立方程式を解くと」の値が、閉じた式の値と一致します（財政 20.00、金融 4.00）
"""
        ),
    ]


def ch10_labor_market_and_ad_as() -> list[NotebookNode]:
    return [
        _intro("第 10 章 労働市場と AD-AS 分析", "10-labor-market-and-ad-as.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
demand_intercept = 100  # 労働需要 Ld = a − b·w の切片 a
demand_slope = 10       # 労働需要の傾き b
supply_intercept = 20   # 労働供給 Ls = c + d·w の切片 c
supply_slope = 10       # 労働供給の傾き d
sticky_wage = 6         # 硬直的な実質賃金
subsistence = 1         # 効率賃金仮説の、生存水準の賃金
mpc = 0.6               # 限界消費性向 c
b = 20                  # 投資の利子感応度 b
intercept = 450         # IS 曲線の A
k = 0.5                 # 貨幣需要の所得感応度 k
h = 100                 # 貨幣需要の利子感応度 h
nominal_money = 250     # 名目貨幣供給 M
full_employment_income = 1000  # 完全雇用所得
base_income = 480       # ケインズの AS の、基準の所得
slope = 400             # ケインズの AS の傾き
delta_government = 10   # 政府支出の増加（ディマンドプル）
supply_loss = 50        # 供給の減少（コストプッシュ）
""",
            parameters=True,
        ),
        markdown("## 労働市場"),
        code(
            """
from lib.chapter10.labor import (
    LaborCurves,
    best_efficiency_wage,
    involuntary_unemployment,
    labor_equilibrium,
)

curves = LaborCurves(demand_intercept, demand_slope, supply_intercept, supply_slope)
wage, employment = labor_equilibrium(curves)
print(f"均衡: 実質賃金 {wage:.2f}、雇用 {employment:.1f}")
print(f"実質賃金が {sticky_wage} に硬直的なときの、非自発的失業: "
      f"{involuntary_unemployment(curves, sticky_wage):.1f}")
print("効率賃金（努力 ÷ 賃金が最大）:",
      best_efficiency_wage([2, 3, 4, 5, 6, 8, 10], subsistence))
"""
        ),
        markdown("## 図: 労働市場"),
        code(
            """
from lib.chapter10.plot import plot_labor_market

plot_labor_market(curves, sticky_wage, wage_max=10)
"""
        ),
        markdown("## AD と AS の交点"),
        code(
            """
from functools import partial

from lib.chapter10.ad_as import (
    AdEconomy,
    expand_demand,
    keynesian_supply,
    shift_supply,
    solve_ad_as,
)

economy = AdEconomy(mpc, b, intercept, k, h, nominal_money)
supply = partial(
    keynesian_supply,
    full_employment_income=full_employment_income,
    base_income=base_income,
    slope=slope,
)
price, income = solve_ad_as(economy, supply)
print(f"もとの均衡: 物価 {price:.3f}、所得 {income:.1f}")
price1, income1 = solve_ad_as(expand_demand(economy, delta_government), supply)
print(f"AD が右へ: 物価 {price1:.3f}、所得 {income1:.1f}")
full, base_after = shift_supply(full_employment_income, base_income, -supply_loss)
shifted = partial(
    keynesian_supply, full_employment_income=full, base_income=base_after, slope=slope
)
price2, income2 = solve_ad_as(economy, shifted)
print(f"AS が左へ: 物価 {price2:.3f}、所得 {income2:.1f}")
"""
        ),
        markdown("## 図: AD-AS"),
        code(
            """
from lib.chapter10.plot import plot_ad_as

plot_ad_as(
    economy, full_employment_income, base_income, slope, delta_government,
    price_min=0.8, price_max=1.6,
)
"""
        ),
        markdown(
            """
## 試してみよう

- `sticky_wage = 7` にすると、非自発的失業は 60.0 になります（6 のときは 40.0）。
  `sticky_wage = 4` にすると、均衡（4.0）なので、失業は 0.0 です
- `subsistence = 2` にすると、効率賃金は 4 になります（1 のときは 2）。
  生存水準が高いほど、企業は高い賃金を払うのが得になります
- もとの均衡は、物価 1.250、所得 980.0 です。`delta_government = 10`（AD が右へ）で、
  物価 1.293、所得 997.3 になります。**物価と所得が、ともに上がります**
- `supply_loss = 50`（AS が左へ）では、物価 2.000、所得 950.0 です。**物価が上がり、
  所得が下がります**（スタグフレーション）
"""
        ),
    ]


def ch11_phillips_curve_and_okun() -> list[NotebookNode]:
    return [
        _intro(
            "第 11 章 物価・失業とフィリップス曲線", "11-phillips-curve-and-okun.md"
        ),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
unemployment = 4.0        # 失業率 u（%）
natural_rate = 5.0        # 自然失業率 u_n（%）
expected_inflation = 2.0  # 期待インフレ率 π^e（%）
beta = 0.5                # 失業率への感応度 β
periods = 5               # 期待が追いつく経路の期間
growth = [3.2, 1.5, 4.1, 0.8, 2.9, 5.0, -0.5, 3.6, 2.2, 4.5, 1.0, 3.0]  # 成長率（%）
okun_slope = -0.4         # 架空のデータの、真の傾き
okun_intercept = 1.2      # 架空のデータの、真の切片
noise = 0.1               # 架空のデータの、雑音の大きさ
seed = 0                  # 雑音の種
nominal_rate = 1.0        # 名目利子率（%）
inflation = -2.0          # インフレ率（%）。負ならデフレ
debt = 1000               # 名目の借金
years = 10                # 借金の年数
mpc = 0.6                 # 限界消費性向 c
b = 20                    # 投資の利子感応度 b
intercept = 450           # IS 曲線の A
k = 0.5                   # 貨幣需要の所得感応度 k
h = 100                   # 貨幣需要の利子感応度 h
nominal_money = 250       # 名目貨幣供給 M
delta_government = 10     # 需要の増加（ディマンドプル）
supply_loss = 50          # 供給の減少（コストプッシュ）
""",
            parameters=True,
        ),
        markdown("## フィリップス曲線"),
        code(
            """
from lib.chapter11.phillips import (
    accelerating_inflation_path,
    implied_natural_rate,
    short_run_inflation,
)

pi = short_run_inflation(unemployment, natural_rate, expected_inflation, beta)
print(f"短期のインフレ率: {pi:.2f}%")
print("失業率を保ち続けたときのインフレ率の経路:",
      accelerating_inflation_path(
          unemployment, natural_rate, expected_inflation, beta, periods
      ))
print("観測から逆算した自然失業率:",
      implied_natural_rate(unemployment, pi, expected_inflation, beta))
"""
        ),
        code(
            """
from lib.chapter11.plot import plot_phillips

plot_phillips(
    natural_rate, [expected_inflation, expected_inflation + 2], beta, u_min=3, u_max=7
)
"""
        ),
        markdown("## オークンの法則"),
        code(
            """
from lib.chapter11.okun import (
    okun_breakeven_growth,
    okun_coefficients,
    synthetic_unemployment_change,
)

change = synthetic_unemployment_change(growth, okun_slope, okun_intercept, noise, seed)
fit = okun_coefficients(growth, change)
print(f"推定: 傾き {fit.slope:.3f}、切片 {fit.intercept:.3f}")
print(f"失業率が変わらない成長率: {okun_breakeven_growth(fit):.3f}%")
"""
        ),
        code(
            """
from lib.chapter11.plot import plot_okun

plot_okun(growth, change, fit)
"""
        ),
        markdown("## デフレと、物価ショック"),
        code(
            """
from lib.chapter10.ad_as import AdEconomy
from lib.chapter11.deflation import debt_burden, real_interest_rate
from lib.chapter11.price_shocks import cost_push_effect, demand_pull_effect

print(f"実質利子率: {real_interest_rate(nominal_rate, inflation):.1f}%")
burden = debt_burden(debt, inflation / 100, years)
print(f"借金の実質的な負担（{years} 年後）: {burden:.1f}")
economy = AdEconomy(mpc, b, intercept, k, h, nominal_money)
dp, dy = demand_pull_effect(economy, 1000, 480, 400, delta_government)
print(f"ディマンドプル: 物価 {dp:+.4f}、所得 {dy:+.2f}")
cp, cy = cost_push_effect(economy, 1000, 480, 400, supply_loss)
print(f"コストプッシュ: 物価 {cp:+.4f}、所得 {cy:+.2f}")
"""
        ),
        markdown(
            """
## 試してみよう

- `expected_inflation = 4.0` にすると、短期のインフレ率は 4.50% になります（2.0 のときは
  2.50%）。期待インフレ率が高いと、同じ失業率でも、インフレ率が高くなります
- `beta = 1.0` にすると、短期のインフレ率は 3.00% です。曲線が急になります
- `unemployment = 4.0`（自然失業率の 5.0 より低い）を保ち続けると、経路は
  [2, 2.5, 3.0, 3.5, 4.0, 4.5] と上がり続けます。`unemployment = 5.0` にすると、
  [2, 2.0, 2.0, 2.0, 2.0, 2.0] で、上がりません。**長期のトレードオフはありません**
- `noise = 0.5` にすると、推定の傾きは −0.442、切片は 1.320 になります
  （`noise = 0.1` では −0.408 と 1.224）。雑音が大きいと、推定が真の値（−0.4、1.2）
  から離れます
- `inflation = 2.0` にすると、実質利子率は −1.0%、借金の実質的な負担は 820.3 です
  （`inflation = -2.0` では 3.0% と 1223.9）。デフレは、実質利子率を高くし、
  借金の負担を重くします
- `delta_government = 5` にすると、ディマンドプルは、物価 +0.0216、所得 +8.64 です
  （10 では +0.0433 と +17.32）。`supply_loss = 50` のコストプッシュは、物価 +0.7500、
  所得 −30.00 で、**所得が減ります**
"""
        ),
    ]


def ch12_consumption_and_investment() -> list[NotebookNode]:
    return [
        _intro("第 12 章 消費と投資の理論", "12-consumption-and-investment.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
incomes = [100, 100, 100, 130, 100, 100]  # 所得の系列（4 期目だけ一時的に増える）
mpc = 0.8                  # 限界消費性向 c
adjust = 0.2               # 恒常所得の調整係数 λ
annual_income = 500        # 働いている間の年収
working_years = 40         # 働く年数
lifetime_years = 60        # 生涯の年数
capital_coefficient = 2    # 資本係数 V
accelerator_incomes = [100, 120, 140, 150, 155, 155]  # 加速度原理の所得の系列
market_value = 120         # 企業の市場価値
replacement_cost = 100     # 資本の再取得価格
""",
            parameters=True,
        ),
        markdown("## 消費の理論"),
        code(
            """
from lib.chapter12.consumption import (
    consumption_from_absolute_income,
    lifecycle_consumption,
    lifecycle_saving,
    permanent_consumption,
    ratchet_consumption,
)

print("絶対所得仮説:", [consumption_from_absolute_income(y, mpc) for y in incomes])
print("恒常所得仮説:",
      [round(c, 1) for c in permanent_consumption(incomes, mpc, adjust)])
print("相対所得仮説（ラチェット）:", ratchet_consumption(incomes, mpc))
print(f"ライフサイクル仮説: 毎年の消費 "
      f"{lifecycle_consumption(annual_income, working_years, lifetime_years):.1f}、"
      f"貯蓄 {lifecycle_saving(annual_income, working_years, lifetime_years):.1f}")
"""
        ),
        markdown("## 図: 消費の理論"),
        code(
            """
from lib.chapter12.plot import plot_consumption_theories

plot_consumption_theories(incomes, mpc, adjust)
"""
        ),
        markdown("## 投資の理論"),
        code(
            """
from lib.chapter12.investment import accelerator_path, should_invest, tobins_q

print("加速度原理の投資:", accelerator_path(capital_coefficient, accelerator_incomes))
q = tobins_q(market_value, replacement_cost)
print(f"トービンの q: {q:.2f}、投資するか: {should_invest(q)}")
"""
        ),
        markdown("## 図: 加速度原理"),
        code(
            """
from lib.chapter12.plot import plot_accelerator

plot_accelerator(capital_coefficient, accelerator_incomes)
"""
        ),
        markdown(
            """
## 試してみよう

- `adjust = 0.5` にすると、恒常所得仮説の消費は [80, 80, 80, 92, 86, 83] になります
  （0.2 のときは [80, 80, 80, 84.8, 83.8, 83.1]）。`adjust = 1.0` にすると、
  絶対所得仮説と
  同じ [80, 80, 80, 104, 80, 80] です。**一時的な所得の増加に、消費は敏感に動きません**
- ラチェット（相対所得仮説）の消費は、所得が戻っても、[80, 80, 80, 104, 104, 104] のまま
  下がりません。過去の最高所得が、消費を決めるからです
- `working_years = 45` にすると、毎年の消費は 375.0 になります（40 年では 333.3）。
  働く期間が長いほど、生涯所得が増えます
- `capital_coefficient = 3` にすると、投資は [60, 60, 30, 15, 0] になります
  （2 のときは [40, 40, 20, 10, 0]）。所得の増加が止まる（`accelerator_incomes` の最後を
  150 に揃える）と、投資は 0 になります
- `market_value = 80` にすると、q は 0.80 で、投資しません（q > 1 のときだけ投資します）
"""
        ),
    ]


def ch13_quantity_theory_and_exchange_rate() -> list[NotebookNode]:
    return [
        _intro(
            "第 13 章 貨幣数量説と為替・国際収支",
            "13-quantity-theory-and-exchange-rate.md",
        ),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
money = 200               # 貨幣量 M
velocity = 4              # 貨幣の流通速度 V
output = 200              # 実質生産量 Y
money_growth = 5          # 貨幣の増加率 μ（%）
real_growth = 2           # 実質成長率 g（%）
velocity_change = 0       # 流通速度の変化 Δv（%）
outputs = [200, 400]      # 図で比べる生産量
moneys = [0, 100, 200, 300]  # 図の、貨幣量
rates = [105, 115, 125, 135, 145]  # 為替レート（1 ドルあたりの円）
base_net_exports = 20     # 基準の純輸出
base_rate = 125           # 基準の為替レート
net_export_slope = 0.4    # 為替レートに対する純輸出の傾き
domestic_price = 1000     # 自国の価格
foreign_price = 10        # 外国の価格（ドル）
domestic_inflation = 0.1  # 自国の物価上昇率
""",
            parameters=True,
        ),
        markdown("## 貨幣数量説"),
        code(
            """
from lib.chapter13.quantity import (
    inflation_from_money_growth,
    marshall_k,
    price_level_from_quantity,
)

print(f"物価水準 P = MV ÷ Y: {price_level_from_quantity(money, velocity, output):.2f}")
print(f"マーシャルの k: {marshall_k(velocity):.3f}")
print(f"インフレ率の近似: "
      f"{inflation_from_money_growth(money_growth, real_growth, velocity_change)}%")
"""
        ),
        markdown("## 図: 貨幣量と物価"),
        code(
            """
from lib.chapter13.plot import plot_money_and_prices

plot_money_and_prices(velocity, outputs, moneys)
"""
        ),
        markdown("## 為替レートと純輸出"),
        code(
            """
from lib.chapter13.open_economy import (
    net_exports_from_exchange_rate,
    ppp_after_inflation,
    ppp_exchange_rate,
)

print("純輸出:", [
    net_exports_from_exchange_rate(e, base_net_exports, base_rate, net_export_slope)
    for e in rates
])
print(f"購買力平価: {ppp_exchange_rate(domestic_price, foreign_price):.1f}、"
      f"物価上昇後 "
      f"{ppp_after_inflation(domestic_price, foreign_price, domestic_inflation):.1f}")
"""
        ),
        markdown("## 図: 為替レートと純輸出"),
        code(
            """
from lib.chapter13.plot import plot_net_exports

plot_net_exports(rates, base_net_exports, base_rate, net_export_slope)
"""
        ),
        markdown(
            """
## 試してみよう

- `money = 400` にすると、物価水準は 8.00 になります（200 では 4.00）。貨幣量が 2 倍に
  なると、物価も 2 倍です。`output = 400` にすると、2.00 に下がります
- `velocity_change = 1` にすると、インフレ率の近似は 4% です（0 のときは 3%）。
  `velocity_change = -3` にすると、0% です。流通速度が下がると、貨幣を増やしても
  物価が上がりません
- `net_export_slope = 0.8` にすると、純輸出は、為替レート 105 で 4.0、145 で 36.0 です
  （0.4 では 12.0 と 28.0）。円安で純輸出が増える度合いが、大きくなります
- `domestic_inflation = 0.1` のとき、購買力平価は 100.0 から 110.0 に動きます。
  自国の物価が上がると、円安の方向へ動きます
"""
        ),
    ]


def ch14_mundell_fleming() -> list[NotebookNode]:
    return [
        _intro("第 14 章 マンデル・フレミング・モデル", "14-mundell-fleming.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
mpc = 0.6              # 限界消費性向 c
b = 20                 # 投資の利子感応度 b
intercept = 400        # 為替レートによらない支出 A
n = 50                 # 為替レートへの純輸出の感応度 n
k = 0.5                # 貨幣需要の所得感応度 k
h = 100                # 貨幣需要の利子感応度 h
real_money = 250       # 実質貨幣供給 M/P（変動相場で使う）
world_rate = 2.5       # 世界の利子率 r*
exchange_rate = 1      # 為替レート e（固定相場で使う。上がると円安）
delta_government = 10  # 政府支出の増加 ΔG
delta_real_money = 10  # 実質貨幣供給の増加 Δ(M/P)
delta_exchange_rate = 0.1  # 固定相場での、為替レートの切り下げ幅
""",
            parameters=True,
        ),
        markdown("## 均衡と、政策の効果"),
        code(
            """
from lib.chapter14.mundell_fleming import (
    SmallOpenEconomy,
    fixed_rate_devaluation_effect,
    fixed_rate_equilibrium,
    floating_rate_equilibrium,
    policy_effects_table,
)

economy = SmallOpenEconomy(
    mpc, b, intercept, n, k, h, real_money, world_rate, exchange_rate
)
print("固定相場の均衡:", fixed_rate_equilibrium(economy))
print("変動相場の均衡:", floating_rate_equilibrium(economy))
for row in policy_effects_table(economy, delta_government, delta_real_money):
    print(f"{row.regime}・{row.policy}: 所得 {row.income_change:+.2f}、"
          f"為替レート {row.exchange_rate_change:+.3f}、"
          f"実質貨幣供給 {row.real_money_change:+.2f}")
print(f"固定相場の切り下げ（{delta_exchange_rate}）の効果: "
      f"{fixed_rate_devaluation_effect(economy, delta_exchange_rate):+.2f}")
"""
        ),
        markdown("## 図: 為替制度ごとの財政政策"),
        code(
            """
from lib.chapter14.plot import plot_fiscal_policy_by_regime

plot_fiscal_policy_by_regime(
    economy, delta_government, income_min=600, income_max=1200
)
"""
        ),
        markdown("## 図: 4 通りの政策の効果"),
        code(
            """
from lib.chapter14.plot import plot_policy_effects

plot_policy_effects(economy, delta_government, delta_real_money)
"""
        ),
        markdown(
            """
## 試してみよう

- 初期設定では、固定・変動の、どちらの均衡も、所得 1000.0 です。政策の効果の表は、
  固定相場では、財政政策が +25.00（金融政策は 0.00）、変動相場では、財政政策が 0.00
  （金融政策は +20.00）です。**固定相場では財政政策、変動相場では金融政策が効きます**
- `world_rate = 3.5` にすると、固定相場の均衡の所得は 950.0、変動相場の均衡の所得は
  1200.0、為替レートは 3.0 になります。世界の利子率が上がると、固定相場では
  投資が減って所得が下がり、変動相場では、LM 曲線から所得が決まります
- `n = 100` にすると、変動相場の財政政策による為替レートの変化は −0.100 になります
  （`n = 50` では −0.200）。純輸出が為替に敏感なほど、為替レートの動きは小さくて
  すみます。所得の効果は、変わりません
- `delta_exchange_rate = 0.1` の切り下げは、固定相場で所得を +12.50 増やします
"""
        ),
    ]


NOTEBOOKS: dict[str, Callable[[], list[NotebookNode]]] = {
    "ch01_gdp_and_value_added": ch01_gdp_and_value_added,
    "ch02_three_way_equivalence": ch02_three_way_equivalence,
    "ch03_price_indexes_and_indicators": ch03_price_indexes_and_indicators,
    "ch04_45_degree_line_and_multiplier": ch04_45_degree_line_and_multiplier,
    "ch05_gaps_and_stabilization": ch05_gaps_and_stabilization,
    "ch06_money_supply": ch06_money_supply,
    "ch07_money_demand_and_lm": ch07_money_demand_and_lm,
    "ch08_is_curve_and_is_lm": ch08_is_curve_and_is_lm,
    "ch09_fiscal_and_monetary_policy": ch09_fiscal_and_monetary_policy,
    "ch10_labor_market_and_ad_as": ch10_labor_market_and_ad_as,
    "ch11_phillips_curve_and_okun": ch11_phillips_curve_and_okun,
    "ch12_consumption_and_investment": ch12_consumption_and_investment,
    "ch13_quantity_theory_and_exchange_rate": ch13_quantity_theory_and_exchange_rate,
    "ch14_mundell_fleming": ch14_mundell_fleming,
}


def main() -> None:
    for name, build in sorted(NOTEBOOKS.items()):
        path = NOTEBOOKS_DIR / f"{name}.ipynb"
        write(path, build())
        print(f"生成: {path.name}")


if __name__ == "__main__":
    main()
