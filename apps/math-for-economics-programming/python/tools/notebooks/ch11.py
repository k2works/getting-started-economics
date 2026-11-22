"""第 11 章のノートブック（セルの並び）。"""

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import code, markdown
from tools.notebooks.common import title

NAME = "ch11_integrals_and_auctions"


def cells() -> list[NotebookNode]:
    """ノートブックのセルの並び。"""
    return [
        title(11, "積分とオークション", "11-integrals-and-auctions"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
power = 2               # 積分する関数 y = x^power の次数（2 以上の整数）
low = 0.0               # 積分の下端
high = 1.0              # 積分の上端（low より大きく）
pieces = 4              # 中点法・台形法の分割数（1 以上の整数）
demand_intercept = 120  # 需要 q = a − b·p の a（正）
demand_slope = 2        # 需要の傾き b（正）
price = 40              # 消費者余剰を求める価格（0 以上、a ÷ b 以下）
bidders = 2             # オークションの参加者の数（2 以上の整数）
rounds = 20_000         # シミュレーションの回数（1 以上。多いほど公式に近い）
seed = 1                # 乱数の種（同じ種なら、同じ結果になる）
""",
            parameters=True,
        ),
        markdown("## 積分: 公式と、中点法・台形法"),
        code(
            """
from lib.chapter05.derivative import Polynomial
from lib.chapter11.integral import (
    midpoint_rule_integral,
    polynomial_definite_integral,
    trapezoid_rule_integral,
)

curve = Polynomial((0,) * power + (1,))
exact = polynomial_definite_integral(curve, low, high)
print(f"x^{power} の {low:g} から {high:g} までの積分（公式）: {exact:.6f}")
rules = [("中点法", midpoint_rule_integral), ("台形法", trapezoid_rule_integral)]
for name, rule in rules:
    for n in (pieces, pieces * 10):
        value = rule(curve, low, high, n)
        print(f"{name}（{n} 等分）: {value:.6f}、誤差 {abs(value - exact):.2e}")
"""
        ),
        markdown("## 消費者余剰: 積分と、第 1 章の三角形"),
        code(
            """
import functools

from lib.chapter01.market import consumer_surplus, demand_quantity
from lib.chapter11.applications import area_under_demand

demand = functools.partial(demand_quantity, a=demand_intercept, b=demand_slope)
choke = demand_intercept / demand_slope
print(f"積分: {area_under_demand(demand, price, choke):.4f}")
triangle = consumer_surplus(price, demand_intercept, demand_slope)
print(f"三角形（第 1 章）: {triangle:.4f}")
"""
        ),
        markdown("## オークション: 公式・積分・シミュレーション"),
        code(
            """
import statistics

from lib.chapter11.auction import (
    expected_auction_revenue_formula,
    first_price_expected_revenue,
    second_price_expected_revenue,
    simulate_auction_revenues,
)

formula = expected_auction_revenue_formula(bidders)
print(f"公式 (n − 1) ÷ (n + 1): {formula}（{float(formula):.4f}）")
print(f"積分: セカンド {second_price_expected_revenue(bidders):.4f}、"
      f"ファースト {first_price_expected_revenue(bidders):.4f}")
for rule in ("second", "first"):
    revenues = simulate_auction_revenues(bidders, rounds, seed, rule=rule)
    print(f"シミュレーション（{rule}）: 平均 {statistics.fmean(revenues):.4f}、"
          f"分散 {statistics.pvariance(revenues):.4f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter11.plot import plot_auction_revenues, plot_integration_errors

plot_integration_errors(curve, exact, low, high, [pieces * 2**k for k in range(8)])
"""
        ),
        code(
            """
plot_auction_revenues(bidders, rounds, seed)
"""
        ),
        markdown(
            """
## 試してみよう

- `pieces` を 4 から 40 にすると、中点法の誤差は 5.21e-03 → 5.21e-05、台形法は
  1.04e-02 → 1.04e-04 です。分割数を 10 倍にすると、誤差は **100 分の 1**
  （誤差の次数 2）。同じ分割数なら、中点法の誤差は台形法の約半分です
- `power = 3`・`high = 2.0` にすると、公式の値は 4 です。4 等分の中点法は
  3.875（小さい）、台形法は 4.25（大きい）で、正しい値を挟みます
- `bidders` を 5 にすると、期待収入は公式・積分とも 2/3（0.6667）に上がります。
  シミュレーションの平均は、セカンド 0.6663・ファースト 0.6658 で、2 つの方式は
  ほぼ同じです（収入同値）。分散は、セカンド 0.0323・ファースト 0.0129 です
- `rounds` を 200 に減らすと、種 1 では、平均はセカンド 0.3180・ファースト 0.3276 で、
  公式の 1/3 から離れます。**多くの種で**、回数が少ないと、平均が 1/3 から離れやすく
  なります（種によっては、たまたま近くなります）。`seed` だけを 2 に変えると
  （2 万回のまま）、0.3332・0.3336 です
"""
        ),
    ]
