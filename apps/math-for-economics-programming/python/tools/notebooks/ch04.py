"""第 4 章のノートブック（セルの並び）。"""

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import code, markdown
from tools.notebooks.common import title

NAME = "ch04_sequences_and_saving"


def cells() -> list[NotebookNode]:
    """ノートブックのセルの並び。"""
    return [
        title(4, "数列と貯蓄", "04-sequences-and-saving"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
first = 1          # 等比数列の初項 a
ratio = 0.5        # 公比 r（無限級数は、-1 < r < 1 のときだけ）
terms = 10         # 足す項数 n（1 以上）
tolerance = 0.01   # 無限級数との差の許容誤差（正）
payment = 5        # 毎年の受け取り・クーポン C
rate = 0.05        # 利子率 r（正。5% は 0.05）
years = 10         # 年金・債券の年数（0 以上）
face = 100         # 債券の額面
""",
            parameters=True,
        ),
        markdown("## 等比数列の和と、無限級数"),
        code(
            """
from lib.chapter04.sequence import (
    geometric_partial_sum,
    geometric_series_limit,
    terms_until_within,
)

total = geometric_partial_sum(first, ratio, terms)
limit = geometric_series_limit(first, ratio)
print(f"{terms} 項の和: {total:.6f}、無限級数: {limit:.6f}、差: {limit - total:.6f}")
needed = terms_until_within(first, ratio, tolerance)
print(f"差が {tolerance} より小さくなる項数: {needed}")
"""
        ),
        markdown("## 年金・永久債・利付債・積立"),
        code(
            """
from lib.chapter04.sequence import (
    annuity_present_value,
    coupon_bond_price,
    perpetuity_present_value,
    savings_future_value,
)

annuity = annuity_present_value(payment, rate, years)
perpetuity = perpetuity_present_value(payment, rate)
share = annuity / perpetuity
bond = coupon_bond_price(face, payment, rate, years)
print(f"{years} 年の年金の現在価値: {annuity:.2f}（永久債の {share:.1%}）")
print(f"永久債の現在価値: {perpetuity:.2f}")
print(f"利付債の価格（額面 {face}）: {bond:.2f}")
print(f"{years} 年の積立の将来価値: {savings_future_value(payment, rate, years):.2f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter04.plot import plot_bond_prices, plot_partial_sums

plot_partial_sums(first, ratio, terms)
"""
        ),
        code(
            """
rates = [k / 1000 for k in range(5, 101, 5)]  # 0.5% から 10% まで
plot_bond_prices(face, payment, years, rates)
"""
        ),
        markdown(
            """
## 試してみよう

- `ratio` を 0.9 にすると、10 項の和は 6.513216 で、無限級数 10 との差は 3.49 も
  残ります。差が 0.01 より小さくなるのは、66 項目です（0.5 なら 8 項目）
- `ratio = -0.5` にすると、部分和は、無限級数 0.666667 の上下を行き来しながら、
  近づきます（図の点が、ジグザグになります）
- `rate` を 0.1 に上げると、永久債は 50.00、利付債の価格は 69.28 に下がります。
  `rate` を 0.05（クーポンの利回りと同じ）に戻すと、利付債の価格は、ちょうど 100.00 です
- `years` を 50 にすると、年金の現在価値は 91.28 で、永久債の 91.3% に近づきます
"""
        ),
    ]
