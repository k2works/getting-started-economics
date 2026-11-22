"""第 3 章のノートブック（セルの並び）。"""

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import code, markdown
from tools.notebooks.common import title

NAME = "ch03_exponents_logarithms_and_interest"


def cells() -> list[NotebookNode]:
    """ノートブックのセルの並び。"""
    return [
        title(3, "指数・対数と金利", "03-exponents-logarithms-and-interest"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
principal = 100      # 元本（正）
rate = 0.05          # 年利（小数。5% なら 0.05。倍になる年数は、正のときだけ）
years = 10           # 年数（1 以上の整数。図の横軸の長さにもなる）
times_per_year = 12  # 年あたりの複利の回数（1 以上の整数）
future = 1000        # 割引現在価値を求める、years 年後の額
""",
            parameters=True,
        ),
        markdown("## 複利・割引・倍になる年数"),
        code(
            """
from fractions import Fraction

from lib.chapter03.interest import (
    compound_amount,
    continuous_compound_amount,
    discount_to_present,
    effective_annual_rate,
    exact_compound_amount,
    rule_of_72_years,
    years_to_multiply,
)

print(f"複利（年 1 回）: {compound_amount(principal, rate, years):.4f}")
exact = exact_compound_amount(principal, Fraction(str(rate)), years)
print(f"  分数で厳密に: {exact}（小数では {float(exact):.10f}）")
print(f"単利: {principal * (1 + rate * years):.4f}")
print(f"連続複利: {continuous_compound_amount(principal, rate, years):.4f}")
print(f"{years} 年後の {future} の割引現在価値: "
      f"{discount_to_present(future, rate, years):.4f}")
print(f"年 {times_per_year} 回の複利の実効年利: "
      f"{effective_annual_rate(rate, times_per_year):.4%}")
print(f"倍になる年数: {years_to_multiply(rate, 2):.2f} 年"
      f"（72 の法則: {rule_of_72_years(rate):.2f} 年）")
"""
        ),
        markdown("## 図（左は線形目盛、右は対数目盛）"),
        code(
            """
from lib.chapter03.plot import plot_compound_growth

plot_compound_growth(principal, rate, years)
"""
        ),
        markdown(
            """
## 試してみよう

- `rate = 0.08` にすると、倍になる年数は 9.01 年、72 の法則は 9.00 年で、
  ほぼ一致します。`rate = 0.01` では 69.66 年と 72.00 年で、2 年以上ずれます
- `years = 30` にすると、複利は 432.1942、単利は 250.0000 です。年数が長いほど、
  「利子についた利子」の差が開きます（図の右の対数目盛では、複利だけが直線です）
- `times_per_year` を 1 → 365 に変えると、実効年利は 5.0000% → 5.1267% です。
  連続複利の 5.1271% に近づきますが、超えません
- `rate = 0.1`、`years = 2` にすると、分数では、ちょうど 121 です
  （小数の複利の表示は 121.0000 ですが、`compound_amount` の値は 121.00000000000001）
"""
        ),
    ]
