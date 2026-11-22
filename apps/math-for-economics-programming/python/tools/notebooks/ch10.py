"""第 10 章のノートブック（セルの並び）。"""

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import code, markdown
from tools.notebooks.common import title

NAME = "ch10_probability_and_risk"


def cells() -> list[NotebookNode]:
    """ノートブックのセルの並び。"""
    return [
        title(10, "確率とリスク", "10-probability-and-risk"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
from fractions import Fraction

prevalence = Fraction(1, 100)          # 有病率（事前確率。0 以上 1 以下）
sensitivity = Fraction(9, 10)          # 感度 P(陽性|病気)（0 以上 1 以下）
false_positive_rate = Fraction(5, 100) # 偽陽性率 P(陽性|健康)（0 以上 1 以下）
low_prize = 0                          # 賭けの小さいほうの賞金（0 以上の整数）
high_prize = 100                       # 賭けの大きいほうの賞金（low_prize より大きい）
high_probability = Fraction(1, 2)      # 大きいほうの確率（0 より大きく 1 未満）
trials = 60_000                        # サイコロ 2 個を投げる回数（1〜100 万）
seed = 1                               # 乱数の種（同じ種なら、同じ結果）
""",
            parameters=True,
        ),
        markdown("## ベイズの定理: 陽性のとき、病気である確率"),
        code(
            """
from lib.chapter10.bayes import (
    disease_probability_given_positive,
    positive_test_probability,
)
from lib.chapter10.plot import plot_bayes_update

positive = positive_test_probability(prevalence, sensitivity, false_positive_rate)
posterior = disease_probability_given_positive(
    prevalence, sensitivity, false_positive_rate
)
print(f"陽性になる確率: {float(positive):.4f}")
print(f"陽性のとき病気である確率: {posterior}（{float(posterior):.4f}）")
plot_bayes_update(
    {"Disease": prevalence, "Healthy": 1 - prevalence},
    {"Disease": sensitivity, "Healthy": false_positive_rate},
)
"""
        ),
        markdown("## 期待効用・確実性等価・危険プレミアム（効用 √x）"),
        code(
            """
import math

from lib.chapter10.expectation import discrete_expected_value
from lib.chapter10.plot import plot_certainty_equivalent
from lib.chapter10.risk import (
    certainty_equivalent_of_lottery,
    expected_utility_of_lottery,
    risk_premium_of_lottery,
)

lottery = {low_prize: 1 - high_probability, high_prize: high_probability}
print(f"期待値: {float(discrete_expected_value(lottery)):.4f}")
print(f"期待効用: {expected_utility_of_lottery(lottery, math.sqrt):.4f}")
ce = certainty_equivalent_of_lottery(lottery, math.sqrt)
print(f"確実性等価: {ce:.4f}")
print(f"危険プレミアム: {risk_premium_of_lottery(lottery, math.sqrt):.4f}")
plot_certainty_equivalent(lottery, math.sqrt)
"""
        ),
        markdown("## シミュレーション: 和が 7 の相対頻度"),
        code(
            """
from lib.chapter10.simulation import simulate_dice_sum_frequencies

frequencies = simulate_dice_sum_frequencies(trials, seed=seed)
print(f"{trials} 回のうち、和が 7: {round(frequencies[7] * trials)} 回")
print(f"相対頻度 {frequencies[7]:.4f}（確率 1/6 ≈ {1 / 6:.4f}）")
"""
        ),
        markdown(
            """
## 試してみよう

- 有病率を 10 倍の `Fraction(1, 10)` にすると、陽性のとき病気である確率は
  0.1538 から 2/3（0.6667）に上がります。同じ検査でも、**事前確率**で意味が変わります
- 偽陽性率を `Fraction(1, 100)` に下げると、有病率 1% のままでも、
  10/21（0.4762）に上がります。まれな病気の検査では、**偽陽性率**が効きます
- 賭けを `low_prize = 16` にすると、期待値 58・期待効用 7・確実性等価 49・
  危険プレミアム 9 になります（記事の 10.1 節の図）。`low_prize = 0` のときの
  危険プレミアム 25 より小さくなります。賞金の差（リスク）が小さいからです
- `trials = 600` にすると、和が 7 は 93 回（相対頻度 0.1550）で、1/6 からのずれが
  大きくなります。`seed = 2` に変えると 104 回（0.1733）です。`trials = 1_000_000`
  なら 166494 回（0.1665）で、1/6 ≈ 0.1667 に近づきます（大数の法則）
"""
        ),
    ]
