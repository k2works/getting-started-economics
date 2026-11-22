"""Jupyter Notebook（notebooks/）を、書き出す。

    uv run python -m tools.build_notebooks

各ノートブックは、(1) 説明、(2) 数字を書き換えるセル（Parameters）、(3) 各章の関数を
呼んで、結果を表示するセル、(4) 図、(5) 「試してみよう」の順にそろえる。
`試してみよう` に書く数値は、実際に実行して確かめた値だけにする（乱数は、種を固定）。
データは、すべて乱数で作る（ネットワークには接続しない）。
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


def _title(chapter: str, name: str, article: str) -> NotebookNode:
    return markdown(
        f"# 第 {chapter} 章 {name}: 数字を変えて確かめる\n\n"
        + HOW_TO_RUN
        + f"\n\n記事: `docs/article/econometrics-programming/{article}`"
    )


def ch01_statistics_review() -> list[NotebookNode]:
    return [
        _title("1", "統計学の復習", "01-statistics-review.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0             # 乱数の種（変えると、標本が変わる）
n = 10               # 標本の大きさ
mean = 5.0           # 母集団の平均
sd = 2.0             # 母集団の標準偏差
repetitions = 2000   # 標本を取り直す回数
probability = 0.975  # 臨界値を求める下側確率
degrees_of_freedom = (2, 5, 30)  # 図に描く t 分布の自由度
""",
            parameters=True,
        ),
        markdown("## 標本の特徴と、標本平均のばらつき"),
        code(
            """
import numpy as np

from lib.chapter01.statistics import (
    critical_value,
    sample_variance,
    sampling_distribution_of_mean,
    standard_error_of_mean,
)

rng = np.random.default_rng(seed)
x = rng.normal(mean, sd, n)
print(f"標本平均 {x.mean():.3f}、不偏分散 {sample_variance(x):.3f}、"
      f"標準誤差 {standard_error_of_mean(x):.3f}")
print(f"t({n - 1}) の臨界値 {critical_value('t', probability, n - 1):.3f}、"
      f"正規分布の臨界値 {critical_value('normal', probability):.3f}")

means = sampling_distribution_of_mean(n, repetitions, rng)
print(f"標準正規分布から n={n} 個の平均を {repetitions} 回: "
      f"標準偏差 {means.std(ddof=1):.3f}（理論値 1/√n = {1 / np.sqrt(n):.3f}）")
"""
        ),
        markdown("## 図: 正規分布と t 分布"),
        code(
            """
from lib.chapter01.plot import plot_densities

plot_densities(degrees_of_freedom)
"""
        ),
        markdown(
            """
## 試してみよう

- `n` を 30 にすると、標準誤差は 0.301、t の臨界値は 2.045 になり、正規分布の 1.960
  に近づきます。`n` を 3 にすると、t の臨界値は 4.303 に広がります（標本が小さいほど、
  t 分布の裾は厚い）
- 標本平均のばらつき（計算のセルの 3 行目）は、`n` が 10 のとき 0.313、30 のとき
  0.189、3 のとき 0.576 で、どれも理論値 1/√n（0.316・0.183・0.577）に近い値です
- `seed` を 1 にすると、標本が変わり、標本平均は 5.450、標準誤差は 0.420 になります。
  標本が変わると、推定値も変わります
"""
        ),
    ]


def ch02_simple_regression() -> list[NotebookNode]:
    return [
        _title("2", "単回帰", "02-simple-regression.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0             # 乱数の種
n = 50               # 標本の大きさ
intercept = 1.0      # 真の切片
slope = 0.5          # 真の傾き
sigma = 1.0          # 誤差の標準偏差
repetitions = 1000   # 標本を取り直す回数
""",
            parameters=True,
        ),
        markdown("## 1 つの標本で、直線を当てはめる"),
        code(
            """
import numpy as np

from lib.chapter02.simple import (
    draw_sample,
    fit_simple,
    r_squared,
    sampling_distribution,
    slope_standard_error,
)

rng = np.random.default_rng(seed)
x, y = draw_sample(n, intercept, slope, sigma, rng)
fit = fit_simple(x, y)
print(f"切片 {fit.intercept:.3f}、傾き {fit.slope:.3f}（真の値 {slope}）")
print(f"R² {r_squared(fit, x, y):.3f}、傾きの標準誤差 "
      f"{slope_standard_error(fit, x, y):.3f}")

table = sampling_distribution(n, repetitions, intercept, slope, sigma, rng)
print(f"標本を {repetitions} 回取り直した傾き: 平均 {table['slope'].mean():.3f}、"
      f"標準偏差 {table['slope'].std(ddof=1):.3f}")
"""
        ),
        markdown("## 図: 回帰直線と残差"),
        code(
            """
from lib.chapter02.plot import plot_regression_line

plot_regression_line(x, y, fit)
"""
        ),
        markdown("## 図: 傾きの推定値の分布"),
        code(
            """
from lib.chapter02.plot import plot_slope_distribution

plot_slope_distribution(table["slope"].tolist(), slope)
"""
        ),
        markdown(
            """
## 試してみよう

- `n` を 200 にすると、傾きの標準誤差は 0.159 から 0.076 に下がり、
  取り直した傾きのばらつきも 0.151 から 0.070 になります（標本が大きいほど、
  推定は安定します）
- `sigma` を 3.0 にすると、R² は 0.002、標準誤差は 0.476 になります。誤差が大きいと、
  傾きは、ほとんど分かりません
- `slope` を 0.0 にしても、1 つの標本の傾きは −0.119 と、0 にはなりません。
  標本を取り直した傾きの平均は −0.003 で、0 の近くに集まります
"""
        ),
    ]


def ch03_multiple_regression() -> list[NotebookNode]:
    return [
        _title("3", "重回帰", "03-multiple-regression.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0             # 乱数の種
n = 50               # 標本の大きさ
correlation = 0.9    # x1 と x2 の相関（強い場合）
repetitions = 1000   # 標本を取り直す回数
""",
            parameters=True,
        ),
        markdown("## 説明変数の相関と、係数のばらつき"),
        code(
            """
import numpy as np

from lib.chapter03.multiple import multicollinearity_experiment

low = multicollinearity_experiment(0.0, n, repetitions, np.random.default_rng(seed))
high = multicollinearity_experiment(
    correlation, n, repetitions, np.random.default_rng(seed)
)
print(f"相関 0.0: x1 の係数の平均 {low['x1'].mean():.3f}、"
      f"標準偏差 {low['x1'].std(ddof=1):.3f}")
print(f"相関 {correlation}: x1 の係数の平均 {high['x1'].mean():.3f}、"
      f"標準偏差 {high['x1'].std(ddof=1):.3f}")
"""
        ),
        markdown("## 図: 係数の推定値の分布"),
        code(
            """
from lib.chapter03.plot import plot_collinearity_distributions

plot_collinearity_distributions(low["x1"].tolist(), high["x1"].tolist())
"""
        ),
        markdown(
            """
## 試してみよう

- `correlation` を 0.99 にすると、x1 の係数のばらつきは 0.148 から 1.003 へ、約 7
  倍に広がります。平均は 0.991 で、真の値（1）のままです（多重共線性は、偏りでなく、
  ばらつきを広げます）
- `n` を 200 にすると、相関 0.9 でも、ばらつきは 0.162 まで下がります（相関 0.0 は
  0.070）。標本を大きくすると、共線性の影響は小さくなります
"""
        ),
    ]


def ch04_residual_diagnostics() -> list[NotebookNode]:
    return [
        _title("4", "残差の診断", "04-residual-diagnostics.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0                # 乱数の種
n = 100                 # 標本の大きさ
heteroskedastic = True  # True: x が大きいほど誤差が大きい（扇形）
""",
            parameters=True,
        ),
        markdown("## てこ比・スチューデント化残差・クックの距離"),
        code(
            """
import numpy as np

from lib.chapter03.multiple import fit_ols, leverage
from lib.chapter04.diagnostics import cooks_distance, studentized_residuals
from lib.chapter08.hetero import draw_fan_sample

x, y = draw_fan_sample(n, np.random.default_rng(seed), heteroskedastic)
result = fit_ols(y, x)
h = leverage(x)
print(f"傾き {result.coefficients.iloc[1]:.3f}、R² {result.r_squared:.3f}")
print(f"てこ比の最大 {h.max():.3f}")
print(f"スチューデント化残差の絶対値の最大 "
      f"{np.abs(studentized_residuals(result, h)).max():.3f}")
print(f"クックの距離の最大 {cooks_distance(result, h).max():.3f}")
"""
        ),
        markdown("## 図: 回帰の診断図"),
        code(
            """
from lib.chapter04.plot import plot_diagnostics

plot_diagnostics(y, x)
"""
        ),
        markdown("## 図: 要約統計量が同じで、形が違う 4 組のデータ"),
        code(
            """
from lib.chapter04.diagnostics import same_summary_datasets
from lib.chapter04.plot import plot_same_summary

plot_same_summary(same_summary_datasets())
"""
        ),
        markdown(
            """
## 試してみよう

- `heteroskedastic` を `False` にすると、誤差が均一な標本になり、R² は 0.596 から
  0.858、クックの距離の最大は 0.189 から 0.087 になります。診断図の残差の扇形も、
  消えます
- `n` を 400 にすると、てこ比の最大は 0.042 から 0.011
  に下がります（観測値が増えると、1 点が回帰に及ぼす力は、小さくなります）
- 4 組のデータの図は、数字を変えられません。平均・標準偏差・相関・回帰直線が同じでも、
  形が違うことを、確かめてください
"""
        ),
    ]


def ch05_inference() -> list[NotebookNode]:
    return [
        _title("5", "推測", "05-inference.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0             # 乱数の種
n = 30               # 標本の大きさ
level = 0.95         # 信頼水準
repetitions = 100    # 標本を取り直す回数（区間の本数）
null_slope = 0.0     # 検定する帰無仮説の傾き（真の傾きは 0.5）
""",
            parameters=True,
        ),
        markdown("## 1 つの標本の t 値と信頼区間、被覆率と棄却率"),
        code(
            """
import numpy as np

from lib.chapter02.simple import draw_sample
from lib.chapter03.multiple import fit_ols
from lib.chapter05.inference import (
    confidence_interval,
    coverage_rate,
    rejection_rate,
    slope_intervals,
    t_statistics,
)

rng = np.random.default_rng(seed)
x, y = draw_sample(n, 1.0, 0.5, 1.0, rng)
result = fit_ols(y, x)
t = t_statistics(result, null_slope).iloc[1]
print(f"傾き {result.coefficients.iloc[1]:.3f}、t 値（帰無仮説 {null_slope}） {t:.3f}")
print(confidence_interval(result, level).round(3))

intervals = slope_intervals(n, repetitions, level, np.random.default_rng(seed))
contains = ((intervals["lower"] <= 0.5) & (0.5 <= intervals["upper"])).mean()
print(f"{repetitions} 本のうち、真の傾きを含む割合 {contains:.2f}")
print(f"被覆率（2000 回） "
      f"{coverage_rate(n, 2000, level, np.random.default_rng(seed)):.3f}")
rate = rejection_rate(n, 1000, 0.5, null_slope, 0.05, np.random.default_rng(seed))
print(f"棄却率（真の傾き 0.5、帰無仮説 {null_slope}、有意水準 5%） {rate:.3f}")
"""
        ),
        markdown("## 図: 標本ごとの信頼区間"),
        code(
            """
from lib.chapter05.plot import plot_confidence_intervals

plot_confidence_intervals(intervals, 0.5)
"""
        ),
        markdown(
            """
## 試してみよう

- `level` を 0.8 にすると、区間は狭くなり、真の傾きを含む割合も、0.97 から 0.78
  に下がります（被覆率は 0.812。水準に近い値です）
- `n` を 200 にすると、1 つの標本の t 値は 0.561 から 5.694 になり、棄却率は 0.703
  から 1.000 になります（標本が大きいほど、真の傾き 0.5 が、0 と違うと見抜けます）
- `null_slope` を 0.5（真の値）にすると、棄却率は 0.047 になり、有意水準 5%
  に近づきます。正しい帰無仮説を、誤って棄却する割合です
"""
        ),
    ]


def ch06_asymptotics() -> list[NotebookNode]:
    return [
        _title("6", "漸近理論", "06-asymptotics.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0                         # 乱数の種
sample_sizes = [30, 100, 250, 500]  # 標本の大きさ（比べる）
repetitions = 1000               # 標本を取り直す回数
skewed = True                    # True: 誤差が歪んだ分布（歪度 2）
test_n = 50                      # 検定の標本の大きさ
""",
            parameters=True,
        ),
        markdown("## 標本が大きいと、推定値は真の値（0.5）に集まる"),
        code(
            """
import numpy as np

from lib.chapter06.asymptotics import (
    consistency_experiment,
    jarque_bera_rejection_rate,
)

estimates = consistency_experiment(
    sample_sizes, repetitions, np.random.default_rng(seed)
)
for size, values in estimates.items():
    print(f"n={size}: 平均 {values.mean():.3f}、標準偏差 {values.std(ddof=1):.3f}")

rate = jarque_bera_rejection_rate(
    test_n, 500, skewed, np.random.default_rng(seed)
)
print(f"Jarque-Bera 検定の棄却率（n={test_n}、歪んだ誤差 {skewed}） {rate:.3f}")
"""
        ),
        markdown("## 図: 標本の大きさごとの推定値の分布"),
        code(
            """
from lib.chapter06.plot import plot_estimate_distributions

plot_estimate_distributions(estimates, 0.5)
"""
        ),
        markdown(
            """
## 試してみよう

- 標本の大きさ 30・100・250・500 で、推定値の標準偏差は 0.197・0.101・0.062・0.045
  と縮み、どれも平均は 0.5 のまわりです（一致性）
- `skewed` を `False` にすると、Jarque-Bera 検定の棄却率は 0.928 から 0.034
  に下がります（正規分布の誤差を、ほとんど棄却しません）
- `test_n` を 500 にすると、歪んだ誤差の棄却率は 1.000 です。標本が大きいほど、
  正規でないことを、見抜けます
"""
        ),
    ]


def ch07_dummy_variables() -> list[NotebookNode]:
    return [
        _title("7", "ダミー変数", "07-dummy-variables.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0             # 乱数の種
n = 80               # 標本の大きさ
interaction = True   # True: 女性ダミーと教育年数の交差項を入れる
""",
            parameters=True,
        ),
        markdown("## 男女の平均と、ダミー変数・交差項の回帰"),
        code(
            """
import numpy as np
import pandas as pd

from lib.chapter03.multiple import fit_ols
from lib.chapter07.dummies import draw_wage_sample, group_means, with_interaction

df = draw_wage_sample(n, np.random.default_rng(seed))
print("女性（1）と男性（0）の、対数賃金の平均")
print(group_means(df["lwage"], df["female"]).round(3).to_string())

x = df[["educ", "female"]].astype(float)
if interaction:
    x = x.join(with_interaction(x["educ"], x["female"]))
result = fit_ols(df["lwage"], x)
print(
    pd.DataFrame(
        {"係数": result.coefficients, "標準誤差": result.standard_errors}
    ).round(3)
)
print(f"R² {result.r_squared:.3f}")
"""
        ),
        markdown("## 図: 2 群のデータと回帰直線"),
        code(
            """
from lib.chapter07.plot import plot_group_lines

plot_group_lines(
    df["educ"].to_numpy(dtype=float),
    df["lwage"].to_numpy(),
    df["female"].to_numpy(dtype=float),
    interaction,
)
"""
        ),
        markdown(
            """
## 試してみよう

- `interaction` を `False` にすると、女性ダミーの係数は −0.010 になり、
  交差項を入れたときの −0.479 と大きく違います（交差項があると、女性ダミーは、
  教育年数が 0 のときの差を表します）
- `n` を 400 にすると、交差項の係数は 0.027（標準誤差 0.010）で、真の値（0.02）
  に近づきます。標本が大きいと、標準誤差が小さくなります
"""
        ),
    ]


def ch08_heteroskedasticity() -> list[NotebookNode]:
    return [
        _title("8", "不均一分散", "08-heteroskedasticity.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0                # 乱数の種
n = 100                 # 標本の大きさ
heteroskedastic = True  # True: x が大きいほど誤差が大きい
repetitions = 1000      # 標準誤差を比べる繰り返しの回数
""",
            parameters=True,
        ),
        markdown("## 検定と、頑健な標準誤差"),
        code(
            """
import numpy as np

from lib.chapter03.multiple import fit_ols
from lib.chapter08.hetero import (
    breusch_pagan,
    draw_fan_sample,
    reset_test,
    robust_standard_errors,
    standard_error_comparison,
    white_test,
)

x, y = draw_fan_sample(n, np.random.default_rng(seed), heteroskedastic)
result = fit_ols(y, x)
print(f"通常の標準誤差 {result.standard_errors.iloc[1]:.3f}、"
      f"頑健な標準誤差（HC1） {robust_standard_errors(y, x).iloc[1]:.3f}")
print(f"Breusch-Pagan の p 値 {breusch_pagan(y, x).p_value:.4f}、"
      f"White の p 値 {white_test(y, x).p_value:.4f}、"
      f"RESET の p 値 {reset_test(y, x).p_value:.4f}")

rng = np.random.default_rng(seed)
r = standard_error_comparison(n, repetitions, heteroskedastic, rng)
print(f"傾きの実際のばらつき {r['sd']:.3f}、通常 {r['classical']:.3f}、"
      f"頑健 {r['hc1']:.3f}")
"""
        ),
        markdown("## 図: 実際のばらつきと標準誤差"),
        code(
            """
from lib.chapter08.plot import plot_standard_errors

plot_standard_errors(
    {
        "Actual (SD of estimates)": r["sd"],
        "Classical": r["classical"],
        "Robust (HC1)": r["hc1"],
    }
)
"""
        ),
        markdown(
            """
## 試してみよう

- `heteroskedastic` を `False` にすると、通常の標準誤差（0.081）
  と頑健な標準誤差（0.082）は、ほぼ同じになり、Breusch-Pagan の p 値は 0.4135 で、
  均一分散を棄却しません
- `True` のとき、実際のばらつき 0.200 に対して、通常の標準誤差は 0.157 と小さすぎ、
  頑健な標準誤差は 0.193 で近くなります（図の 3 本の棒）
"""
        ),
    ]


def ch09_pooling_and_did() -> list[NotebookNode]:
    return [
        _title("9", "プーリングと差分の差分", "09-pooling-and-did.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0             # 乱数の種
n = 200              # 各群・各時点の標本の大きさ
effect = 1.5         # 処置の真の効果
entities = 100       # パネルの個人の数
periods = 5          # パネルの期間の数
correlation = 1.0    # 個人の効果 a と x の相関の強さ
repetitions = 200    # パネルを作り直す回数
""",
            parameters=True,
        ),
        markdown("## 差分の差分"),
        code(
            """
import numpy as np

from lib.chapter09.did import (
    did_estimate,
    did_regression,
    draw_did_sample,
    group_period_means,
    panel_estimators,
)

sample = draw_did_sample(n, effect, np.random.default_rng(seed))
means = group_period_means(sample)
print(means.round(3))
print(f"差分の差分 {did_estimate(sample):.3f}（真の効果 {effect}）")
print(f"回帰の交差項の係数 {did_regression(sample).coefficients.iloc[-1]:.3f}")
"""
        ),
        markdown("## 図: 処置群・対照群の平均と反事実"),
        code(
            """
from lib.chapter09.plot import plot_did

plot_did(means)
"""
        ),
        markdown("## パネル: プーリング OLS と 1 階差分（真の傾きは 1）"),
        code(
            """
estimates = panel_estimators(
    entities, periods, correlation, repetitions, np.random.default_rng(seed)
)
print(estimates.agg(["mean", "std"]).round(3))
"""
        ),
        markdown(
            """
## 試してみよう

- `effect` を 0.0 にすると、差分の差分は 0.062 で、0 の近くになります。
  処置の効果がなければ、差分の差分も、ほぼ 0 です
- `correlation` を 0.0 にすると、プーリング OLS の平均は 1.496 から 1.000 になります。
  個人の効果が x と無相関なら、プーリングでも偏りません。1 階差分は、どちらでも 1.000
  です
"""
        ),
    ]


def ch10_panel_data() -> list[NotebookNode]:
    return [
        _title("10", "パネルデータ", "10-panel-data.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0             # 乱数の種
entities = 100       # 個人の数
periods = 5          # 期間の数
correlation = 1.0    # 個人の効果 a と x の相関の強さ（0 なら無相関）
repetitions = 100    # パネルを作り直す回数
""",
            parameters=True,
        ),
        markdown("## 1 つのパネルを、固定効果とランダム効果で推定する"),
        code(
            """
import numpy as np

from lib.chapter09.did import draw_panel, pooled_estimate
from lib.chapter10.panel import fixed_effects, hausman_test, random_effects

panel = draw_panel(entities, periods, correlation, np.random.default_rng(seed))
fe = fixed_effects(panel, "y", ["x"])
re = random_effects(panel, "y", ["x"])
print(f"プーリング OLS {pooled_estimate(panel):.3f}、"
      f"固定効果 {fe.coefficients['x']:.3f}、ランダム効果 {re.coefficients['x']:.3f}"
      "（真の傾きは 1）")
test = hausman_test(fe, re, ["x"])
print(f"Hausman 検定: 統計量 {test.statistic:.3f}、p 値 {test.p_value:.4f}")
"""
        ),
        markdown("## 3 つの推定量の分布（パネルを作り直して繰り返す）"),
        code(
            """
from lib.chapter10.panel import estimator_comparison, hausman_rejection_rate

estimates = estimator_comparison(
    entities, periods, correlation, repetitions, np.random.default_rng(seed)
)
print(estimates.agg(["mean", "std"]).round(3))
rate = hausman_rejection_rate(
    entities, periods, correlation, repetitions, 0.05, np.random.default_rng(seed)
)
print(f"Hausman 検定の棄却率 {rate:.3f}")
"""
        ),
        markdown("## 図: 推定量ごとの分布"),
        code(
            """
from lib.chapter10.plot import plot_estimate_comparison

plot_estimate_comparison(estimates, 1.0)
"""
        ),
        markdown("## 図: 個人ごとの直線"),
        code(
            """
from lib.chapter10.plot import plot_entity_lines

plot_entity_lines(panel, 5)
"""
        ),
        markdown(
            """
## 試してみよう

- `correlation` を 0.0 にすると、プーリング OLS・固定効果・ランダム効果が、どれも 1
  の近く（0.970・0.989・0.988）になり、Hausman 検定の p 値は 0.6669 で、
  同じという帰無仮説を棄却しません
- `correlation` が 1.0 のときは、固定効果が 0.989、ランダム効果が 1.177 で、Hausman
  検定の p 値は 0.0000 です。個人の効果が x と相関すると、ランダム効果は偏ります
- 3 つの推定量を繰り返した結果（`repetitions` が 100）は、固定効果 0.998（標準偏差
  0.022）、ランダム効果 1.213、プーリング OLS 1.491 です
"""
        ),
    ]


def ch11_endogeneity() -> list[NotebookNode]:
    return [
        _title("11", "内生性", "11-endogeneity.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0             # 乱数の種
n = 200              # 標本の大きさ
correlation = 0.5    # x1 と欠落した x2 の相関
error_sd = 0.5       # x の測定誤差の標準偏差
sd_demand = 2.0      # 需要の誤差の標準偏差
sd_supply = 1.0      # 供給の誤差の標準偏差
repetitions = 500    # 標本を取り直す回数
""",
            parameters=True,
        ),
        markdown("## 欠落変数・測定誤差・同時性"),
        code(
            """
import numpy as np

from lib.chapter11.endogeneity import (
    attenuation_factor,
    draw_omitted,
    ovb_decomposition,
    simulate_measurement_error,
    simulate_omitted,
    simultaneity_slope,
)

y, x1, x2 = draw_omitted(n, correlation, np.random.default_rng(seed))
ovb = ovb_decomposition(y, x1, x2)
print(f"欠落変数: 短い回帰 {ovb.short:.3f}、長い回帰 {ovb.long:.3f}"
      f"（真の値 1）、補助回帰の傾き {ovb.delta:.3f}")

omitted = simulate_omitted(n, correlation, repetitions, np.random.default_rng(seed))
print(omitted.agg(["mean", "std"]).round(3))

noisy = simulate_measurement_error(
    n, error_sd, repetitions, np.random.default_rng(seed)
)
print(f"測定誤差: 傾きの平均 {noisy.mean():.3f}、"
      f"理論の減衰係数 {attenuation_factor(1.0, error_sd**2):.3f}")
print(f"同時性: 傾きの大標本での値 {simultaneity_slope(sd_demand, sd_supply):.3f}")
"""
        ),
        markdown("## 図: 欠落変数の偏り"),
        code(
            """
from lib.chapter10.plot import plot_estimate_comparison

plot_estimate_comparison(omitted, 1.0)
"""
        ),
        markdown("## 図: 市場（需要と供給の連立）"),
        code(
            """
from lib.chapter11.endogeneity import draw_market
from lib.chapter11.plot import plot_market

plot_market(draw_market(n, sd_demand, sd_supply, np.random.default_rng(seed)))
"""
        ),
        markdown(
            """
## 試してみよう

- `correlation` を 0.9 にすると、x2 を落とした回帰の係数は 1.943 から 2.803
  へ増えます（理論の偏り 2·相関 だけ、真の値 1 から離れます）。x2 を入れた回帰は
  0.944 で、真の値の近くです
- `error_sd` を 1.0 にすると、測定誤差のある回帰の傾きは 0.803 から 0.505 に縮み、
  理論の減衰係数 0.500 に近づきます
- `sd_demand` を 1.0、`sd_supply` を 2.0 にすると、傾きの大標本での値は 0.600 から
  −0.600 になります。需要と供給のどちらの誤差が大きいかで、OLS
  の傾きの符号まで変わります
"""
        ),
    ]


def ch12_instrumental_variables() -> list[NotebookNode]:
    return [
        _title("12", "操作変数法", "12-instrumental-variables.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0             # 乱数の種
n = 200              # 標本の大きさ
strength = 1.0       # 操作変数の強さ（x = strength·z + v）
endogeneity = 0.5    # 誤差 u と v の相関（内生性）
repetitions = 500    # 標本を取り直す回数
""",
            parameters=True,
        ),
        markdown("## 1 つの標本の、OLS と IV"),
        code(
            """
import numpy as np
import pandas as pd

from lib.chapter03.multiple import fit_ols
from lib.chapter12.iv import (
    draw_iv_sample,
    first_stage_f,
    iv_estimate,
    two_stage_least_squares,
    weak_instrument_experiment,
)

sample = draw_iv_sample(n, strength, endogeneity, np.random.default_rng(seed))
y, x, z = sample["y"], sample["x"], sample["z"]
print(f"OLS の傾き {fit_ols(y, x).coefficients.iloc[1]:.3f}、"
      f"IV の傾き {iv_estimate(y, x, z).slope:.3f}（真の値 1）")
tsls = two_stage_least_squares(y, sample[["x"]], sample[["z"]])
print(f"2SLS の傾き {tsls.coefficients['x']:.3f}、"
      f"標準誤差 {tsls.standard_errors['x']:.3f}")
print(f"第 1 段階の F 値 {first_stage_f(x, sample[['z']]).statistic:.1f}"
      "（10 未満は弱操作変数の目安）")
"""
        ),
        markdown("## 強い操作変数と、指定した強さの比較（内生性は 0.5）"),
        code(
            """
strong = weak_instrument_experiment(n, 1.0, repetitions, np.random.default_rng(seed))
chosen = weak_instrument_experiment(
    n, strength, repetitions, np.random.default_rng(seed)
)
print(f"強さ 1.0: IV の平均 {strong['iv'].mean():.3f}、"
      f"中央値 {strong['iv'].median():.3f}、F の中央値 {strong['f'].median():.1f}")
print(f"強さ {strength}: IV の平均 {chosen['iv'].mean():.3f}、"
      f"中央値 {chosen['iv'].median():.3f}、F の中央値 {chosen['f'].median():.1f}")
"""
        ),
        markdown("## 図: IV の推定値の分布"),
        code(
            """
from lib.chapter10.plot import plot_estimate_comparison

plot_estimate_comparison(
    pd.DataFrame(
        {
            "strength 1.0": strong["iv"].clip(-1, 3),
            f"strength {strength}": chosen["iv"].clip(-1, 3),
        }
    ),
    1.0,
)
"""
        ),
        markdown(
            """
## 試してみよう

- `strength` を 0.1 にすると、第 1 段階の F 値は 0.2 まで下がり、1 つの標本の IV
  の傾きは 1.648（標準誤差 2.086）と、真の値（1）から大きく外れます。標本を取り直した
  IV の推定値は、平均が 1.378、F の中央値が 2.1 です
- `endogeneity` を 0.0 にすると、OLS の傾きは 1.063 で、IV の 1.068 とほぼ同じです。
  内生性がなければ、OLS で足ります
- `n` を 1000 にすると、IV の傾きの標準誤差は 0.081 から 0.031 に、F 値は 1029.4
  になります。OLS は 1.242 で、標本が大きくなっても、1 に近づきません
"""
        ),
    ]


def ch13_iv_tests() -> list[NotebookNode]:
    return [
        _title("13", "操作変数の検定", "13-iv-tests.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0                       # 乱数の種
n = 500                        # 標本の大きさ
invalid_levels = [0.0, 0.1, 0.3]  # 操作変数 z2 が誤差と相関する度合い
endogeneity = 0.5              # Wu-Hausman 検定で調べる内生性の強さ
significance = 0.05            # 有意水準
repetitions = 300              # 標本を取り直す回数
""",
            parameters=True,
        ),
        markdown("## Sargan 検定と Wu-Hausman 検定"),
        code(
            """
import numpy as np

from lib.chapter13.iv_tests import (
    draw_overid_sample,
    sargan_rejection_rate,
    sargan_test,
    wu_hausman_rejection_rate,
)

sample = draw_overid_sample(n, invalid_levels[-1], np.random.default_rng(seed))
test = sargan_test(sample["y"], sample[["x"]], sample[["z1", "z2"]])
print(f"1 つの標本の Sargan 検定（invalid={invalid_levels[-1]}）: "
      f"統計量 {test.statistic:.3f}、p 値 {test.p_value:.4f}")

rates = {
    f"Invalid {invalid}": sargan_rejection_rate(
        n, invalid, repetitions, significance, np.random.default_rng(seed)
    )
    for invalid in invalid_levels
}
for name, rate in rates.items():
    print(f"Sargan の棄却率 {name}: {rate:.3f}")
wu = wu_hausman_rejection_rate(
    n, endogeneity, repetitions, significance, np.random.default_rng(seed)
)
print(f"Wu-Hausman の棄却率（内生性 {endogeneity}）: {wu:.3f}")
"""
        ),
        markdown("## 図: Sargan 検定の棄却率"),
        code(
            """
from lib.chapter13.plot import plot_rejection_rates

plot_rejection_rates(rates, significance)
"""
        ),
        markdown(
            """
## 試してみよう

- `invalid_levels` の 0.0・0.1・0.3 で、Sargan 検定の棄却率は 0.053・0.390・1.000
  です。操作変数が外生（0.0）なら有意水準 5% に近く、誤差と相関するほど、見抜けます
- `n` を 2000 にすると、`invalid` が 0.1 の棄却率は 0.390 から 0.930
  に上がります（標本が大きいほど、小さな不備も、見抜けます）
- `endogeneity` を 0.0 にすると、Wu-Hausman 検定の棄却率は 0.027 に下がり、有意水準
  5% より小さくなります（内生性がなければ、棄却しません）
"""
        ),
    ]


def ch14_logit_probit() -> list[NotebookNode]:
    return [
        _title("14", "ロジットとプロビット", "14-logit-probit.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0             # 乱数の種
n = 300              # 標本の大きさ
link = "logit"       # データを作る誤差の分布（"logit" か "probit"）
""",
            parameters=True,
        ),
        markdown(
            "## ロジット・プロビット・線形確率モデル"
            "（データを作った係数: 0.5・1・−0.8）"
        ),
        code(
            """
import numpy as np
import pandas as pd

from lib.chapter14.discrete import (
    average_marginal_effects,
    draw_binary_sample,
    fit_binary,
    linear_probability,
)

sample = draw_binary_sample(n, link, np.random.default_rng(seed))
x = sample[["x1", "x2"]]
logit = fit_binary(sample["y"], x, "logit")
probit = fit_binary(sample["y"], x, "probit")
coefficients = pd.DataFrame(
    {"logit": logit.coefficients, "probit": probit.coefficients}
)
print(coefficients.round(3))
print(f"対数尤度: logit {logit.log_likelihood:.2f}、probit {probit.log_likelihood:.2f}")
print("平均限界効果")
print(pd.DataFrame({
    "logit": average_marginal_effects(logit, x),
    "probit": average_marginal_effects(probit, x),
    "線形確率": linear_probability(sample["y"], x).drop("const"),
}).round(3))
"""
        ),
        markdown("## 図: 確率の曲線"),
        code(
            """
from lib.chapter14.plot import plot_probability_curves

plot_probability_curves(sample["x1"].to_numpy(), sample["y"].to_numpy())
"""
        ),
        markdown(
            """
## 試してみよう

- `link` を `"probit"` にしても、ロジットとプロビットの平均限界効果は、
  ほぼ同じです（x1 が 0.275 と 0.276）。係数の大きさは違っても（ロジットは、
  プロビットの 1.7 倍ほど）、限界効果は同じです
- `n` を 3000 にすると、係数が真の値に近づきます（ロジットの x1 は 1.043、x2 は
  −0.791。潜在変数の係数は 1 と −0.8）
- 線形確率モデルの平均限界効果（x1 が 0.186）も、ロジット（0.184）に近い値です
"""
        ),
    ]


def ch15_truncated_tobit() -> list[NotebookNode]:
    return [
        _title("15", "切断とトービット", "15-truncated-tobit.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0             # 乱数の種
n = 1000             # 標本の大きさ（潜在変数 y* = 1 + 2x + u、u の標準偏差は 2）
""",
            parameters=True,
        ),
        markdown("## 打ち切りと切断で、OLS は縮む（真の傾きは 2）"),
        code(
            """
import numpy as np

from lib.chapter03.multiple import fit_ols
from lib.chapter15.limited import (
    censor,
    draw_latent_sample,
    fit_tobit,
    fit_truncreg,
    truncate,
)

x, latent = draw_latent_sample(n, np.random.default_rng(seed))
observed = censor(latent)
print(f"打ち切られた割合 {(observed == 0).mean():.2f}")
print(f"潜在変数への OLS（本当は見えない） "
      f"{fit_ols(latent, x).coefficients.iloc[1]:.3f}")
print(f"打ち切りデータへの OLS {fit_ols(observed, x).coefficients.iloc[1]:.3f}")
tobit = fit_tobit(observed, x)
print(f"トービット {tobit.coefficients.iloc[1]:.3f}")

x_cut, y_cut = truncate(x, latent)
print(f"切断（残る観測値 {len(y_cut)}）への OLS "
      f"{fit_ols(y_cut, x_cut).coefficients.iloc[1]:.3f}")
print(f"切断回帰 {fit_truncreg(y_cut, x_cut).coefficients.iloc[1]:.3f}")
"""
        ),
        markdown("## 図: 打ち切られたデータと直線"),
        code(
            """
from lib.chapter15.plot import plot_censored_data

plot_censored_data(x, observed)
"""
        ),
        markdown(
            """
## 試してみよう

- 打ち切りデータへの OLS は 1.315 に縮み、トービットは 2.113 で、真の値（2）
  の近くです。`n` を 200 にしても、トービットは 2.048、OLS は 1.135 です
- 切断（観測値が消える）の OLS は 1.356 に縮み、切断回帰は 2.153 です。
  打ち切りと切断では、使う道具が違います
"""
        ),
    ]


def ch16_heckit() -> list[NotebookNode]:
    return [
        _title("16", "標本選択とヘックマン", "16-heckit.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
seed = 0             # 乱数の種
n = 3000             # 標本の大きさ
correlation = 0.7    # 選択の誤差と結果の誤差の相関 ρ
repetitions = 100    # 標本を取り直す回数
""",
            parameters=True,
        ),
        markdown(
            "## 選択された標本の OLS と、ヘックマンの 2 段階推定（x の真の傾きは 2）"
        ),
        code(
            """
import numpy as np

from lib.chapter03.multiple import fit_ols
from lib.chapter16.heckit import (
    draw_selection_sample,
    heckit_two_step,
    selection_bias_experiment,
)

df = draw_selection_sample(n, correlation, np.random.default_rng(seed))
chosen = df[df["selected"] == 1]
print(f"選択された割合 {df['selected'].mean():.2f}")
ols = fit_ols(chosen["y"], chosen[["x"]]).coefficients["x"]
print(f"選択された標本の OLS {ols:.3f}")
print(f"ヘックマン {heckit_two_step(df, ['x'], ['x', 'z']).coefficients['x']:.3f}")

estimates = selection_bias_experiment(
    1000, correlation, repetitions, np.random.default_rng(seed)
)
print(estimates.agg(["mean", "std"]).round(3))
"""
        ),
        markdown("## 図: 選択された標本と直線"),
        code(
            """
from lib.chapter16.plot import plot_selection

plot_selection(df)
"""
        ),
        markdown("## 図: 推定量の分布"),
        code(
            """
from lib.chapter10.plot import plot_estimate_comparison

plot_estimate_comparison(estimates, 2.0)
"""
        ),
        markdown(
            """
## 試してみよう

- `correlation` を 0.0 にすると、選択された標本の OLS も、2.025 と偏りません。
  選択の誤差と結果の誤差が相関して初めて、選択バイアスが生じます
- `correlation` を 0.9 にすると、OLS の平均は 1.828 から 1.781 へ、さらに偏ります。
  ヘックマンは 1.999 で、真の値（2）のままです
- 繰り返した推定のばらつきは、OLS が 0.040、ヘックマンが 0.056 です。
  偏りを取り除く代わりに、ばらつきは少し大きくなります
"""
        ),
    ]


NOTEBOOKS: dict[str, Callable[[], list[NotebookNode]]] = {
    "ch01_statistics_review": ch01_statistics_review,
    "ch02_simple_regression": ch02_simple_regression,
    "ch03_multiple_regression": ch03_multiple_regression,
    "ch04_residual_diagnostics": ch04_residual_diagnostics,
    "ch05_inference": ch05_inference,
    "ch06_asymptotics": ch06_asymptotics,
    "ch07_dummy_variables": ch07_dummy_variables,
    "ch08_heteroskedasticity": ch08_heteroskedasticity,
    "ch09_pooling_and_did": ch09_pooling_and_did,
    "ch10_panel_data": ch10_panel_data,
    "ch11_endogeneity": ch11_endogeneity,
    "ch12_instrumental_variables": ch12_instrumental_variables,
    "ch13_iv_tests": ch13_iv_tests,
    "ch14_logit_probit": ch14_logit_probit,
    "ch15_truncated_tobit": ch15_truncated_tobit,
    "ch16_heckit": ch16_heckit,
}


def main() -> None:
    for name, build in sorted(NOTEBOOKS.items()):
        path = NOTEBOOKS_DIR / f"{name}.ipynb"
        write(path, build())
        print(f"生成: {path.name}")


if __name__ == "__main__":
    main()
