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


def intro(title: str, article: str) -> NotebookNode:
    """章のタイトル、使い方、記事のパス。"""
    return markdown(
        f"# {title}: 数字を変えて確かめる\n\n{HOW_TO_RUN}\n\n"
        f"記事: `docs/article/macro-programming/{article}`"
    )


def ch01_development_accounting() -> list[NotebookNode]:
    return [
        intro("第 1 章 発展会計", "01-development-accounting.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
alpha = 1 / 3        # 資本分配率 α（物的資本の弾力性）
output_a = 2         # 国 A の 1 人当たり所得
capital_a = 8        # 国 A の 1 人当たり物的資本
human_capital_a = 1  # 国 A の人的資本
output_b = 0.5       # 国 B の 1 人当たり所得
capital_b = 1        # 国 B の 1 人当たり物的資本
human_capital_b = 1  # 国 B の人的資本
target = "C24"       # 所得の差を分解する国（データの C01〜C24）
reference = "C01"    # 比べる相手の国
""",
            parameters=True,
        ),
        markdown("## 2 か国の TFP と、所得の差の内訳"),
        code(
            """
import math

from lib.chapter01.accounting import tfp

a = tfp(output_a, capital_a, human_capital_a, alpha)
b = tfp(output_b, capital_b, human_capital_b, alpha)
gap = math.log(output_b / output_a)
capital_part = alpha * math.log(capital_b / capital_a)
human_part = (1 - alpha) * math.log(human_capital_b / human_capital_a)
tfp_part = math.log(b / a)
print(f"国 A の TFP: {a:.4f}、国 B の TFP: {b:.4f}")
print(f"所得の差（対数）: {gap:.4f}")
print(f"資本の寄与の割合: {capital_part / gap:.4f}")
print(f"人的資本の寄与の割合: {human_part / gap + 0.0:.4f}")
print(f"TFP の寄与の割合: {tfp_part / gap:.4f}")
"""
        ),
        markdown("## 24 か国のデータで、所得の差を分解する"),
        code(
            """
import pandas as pd

from lib.chapter01.accounting import income_gap, load_countries, variance_shares

df = load_countries()
row = pd.Series(income_gap(df, reference, alpha).loc[target])
print(row.round(3).to_string())
print(f"TFP の寄与の割合: {row['tfp'] / row['total']:.3f}")
print("所得の分散を説明する割合:")
print(variance_shares(df, alpha).round(3).to_string())
"""
        ),
        markdown("## 図: 所得の差の分解"),
        code(
            """
from lib.chapter01.plot import plot_gap_decomposition

plot_gap_decomposition(row)
"""
        ),
        markdown("## 図: 対数の TFP と対数の所得"),
        code(
            """
from lib.chapter01.plot import plot_income_and_tfp

plot_income_and_tfp(df, alpha)
"""
        ),
        markdown(
            """
## 試してみよう

- `alpha = 0.5` にすると、C24 の所得の差（−4.818）に占める TFP の割合は、
  0.596 から 0.500 に下がります。24 か国の所得の分散では、0.615 から 0.519 です。
  **α の置き方で、TFP の割合は変わります**
- `target = "C12"` にすると、所得の差は −1.988 に小さくなり、
  TFP の割合は 0.656 です（C24 は 0.596）
- `capital_b = 4`（国 B の資本を 1 から 4 に）にすると、
  国 B の TFP は 0.3150 になり、資本の寄与の割合は 0.1667、
  TFP の割合は 0.8333 です。資本の差が縮むと、所得の差の大半は TFP の差になります
"""
        ),
    ]


def ch02_growth_accounting() -> list[NotebookNode]:
    return [
        intro("第 2 章 成長会計", "02-growth-accounting.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
alpha = 1 / 3          # 資本分配率 α
capital_growth = 6     # 物的資本の成長率（% / 年）
human_growth = 3       # 人的資本の成長率（% / 年）
tfp_growth = 1         # TFP の成長率（% / 年）
start_year = 1990      # 期間の始まり（データは 1990 年から）
end_year = 2019        # 期間の終わり
""",
            parameters=True,
        ),
        markdown("## 成長率の内訳（資本・人的資本・TFP の寄与）"),
        code(
            """
capital = alpha * capital_growth
human_capital = (1 - alpha) * human_growth
income = capital + human_capital + tfp_growth
print(f"資本の寄与: {capital:.4f} %、人的資本の寄与: {human_capital:.4f} %")
print(f"TFP の寄与: {tfp_growth:.4f} %、所得の成長率: {income:.4f} %")
print(f"TFP の割合: {tfp_growth / income:.4f}")
"""
        ),
        markdown("## 24 か国のデータで、成長を分解する"),
        code(
            """
from lib.chapter02.growth import contribution_shares, growth_contribution, load_panel

table = growth_contribution(load_panel(), start_year, end_year, alpha)
print("国ごとの寄与（% / 年）の、24 か国の平均:")
print(table.mean().round(3).to_string())
print("平均の成長率に占める割合:")
print(contribution_shares(table.mean().to_frame().T).round(3).to_string(index=False))
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter02.plot import plot_growth_contributions

plot_growth_contributions(table)
"""
        ),
        code(
            """
from lib.chapter02.plot import plot_tfp_growth

plot_tfp_growth(table)
"""
        ),
        markdown(
            """
## 試してみよう

- `alpha = 0.5` にすると、24 か国の平均の成長率（2.781 % / 年）
  に占める TFP の割合は、0.463 から 0.339 に下がり、資本の寄与（0.959 から 1.438）
  が大きくなります。**α の置き方で、成長の内訳が変わります**
- `tfp_growth = 0` にすると、予想の答え合わせの TFP の割合は 0.0 です
- 予想の答え合わせは、`alpha = 0.5` でも変わります。TFP の割合は 0.1818（1 ÷ 5.5）
  に下がります（資本の寄与が 3、人的資本が 1.5、TFP が 1）
"""
        ),
    ]


def ch03_regression() -> list[NotebookNode]:
    return [
        intro("第 3 章 回帰分析", "03-regression.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
x_values = [1.0, 2.0, 3.0]  # 説明変数 x の 3 つの点
y_values = [2.0, 4.0, 5.0]  # 被説明変数 y の 3 つの点
""",
            parameters=True,
        ),
        markdown("## 直線の当てはめ（最小二乗法）"),
        code(
            """
import pandas as pd

from lib.chapter03.regression import fit_ols

x = pd.Series(x_values)
y = pd.Series(y_values)
result = fit_ols(y, pd.DataFrame({"x": x}))
print(f"傾き: {result.coefficients['x']:.4f}")
print(f"切片: {result.coefficients['const']:.4f}")
print(f"決定係数: {result.r_squared:.4f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter03.plot import plot_regression

plot_regression(x, y, xlabel="x", ylabel="y", label="Points")
"""
        ),
        markdown(
            """
## 試してみよう

- `y_values = [2.0, 4.0, 6.0]` にすると、3 点が一直線に並び、傾きは 2.0、
  決定係数は 1.0 です
- `y_values = [2.0, 5.0, 4.0]` にすると、傾きは 1.0、
  決定係数は 0.4286 に下がります（点が直線から離れます）
- `y_values = [5.0, 4.0, 2.0]` にすると、傾きは −1.5（右下がり）です。
  決定係数は 0.9643 で、右上がりのときと同じです
"""
        ),
    ]


def ch04_difference_equations() -> list[NotebookNode]:
    return [
        intro("第 4 章 差分方程式", "04-difference-equations.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
a = 0.5            # 差分方程式 x(t+1) = a·x(t) + b の係数 a（1 は不可）
b = 1.0            # 定数 b
initial = 0.0      # 初期値 x(0)
periods = 20       # 何期先まで計算するか
demand_intercept = 100  # 蜘蛛の巣: 需要 Q = 切片 − 傾き·P の切片
demand_slope = 3        # 需要の傾き
supply_intercept = 0    # 供給 Q = 切片 + 傾き·P(前期) の切片
supply_slope = 2        # 供給の傾き
initial_price = 10      # 最初の価格
cobweb_periods = 6      # 蜘蛛の巣を何期描くか
""",
            parameters=True,
        ),
        markdown("## 経路と定常状態"),
        code(
            """
from lib.chapter04.difference import is_stable, linear_path, steady_state

path = linear_path(a, b, initial, periods)
print("x(1) から x(5):", [round(v, 4) for v in path[1:6]])
print("定常状態 x*:", round(steady_state(a, b), 4))
print("安定か（|a| < 1）:", is_stable(a))
print(f"x({periods}):", round(path[periods], 4))
"""
        ),
        markdown("## 図: 差分方程式の経路"),
        code(
            """
from lib.chapter04.plot import plot_paths

plot_paths({f"a = {a}": path}, steady_state=steady_state(a, b))
"""
        ),
        markdown("## 蜘蛛の巣モデル"),
        code(
            """
from lib.chapter04.difference import cobweb_coefficients

a_cobweb, b_cobweb = cobweb_coefficients(
    demand_intercept, demand_slope, supply_intercept, supply_slope
)
print(f"価格の差分方程式の係数 a = {a_cobweb:.4f}、定数 b = {b_cobweb:.4f}")
print("安定か:", is_stable(a_cobweb))
"""
        ),
        code(
            """
from lib.chapter04.plot import plot_cobweb

plot_cobweb(
    demand_intercept,
    demand_slope,
    supply_intercept,
    supply_slope,
    initial_price,
    cobweb_periods,
)
"""
        ),
        markdown(
            """
## 試してみよう

- `a = -0.8` にすると、定常状態は 0.5556 で、x(t) は 1.0、0.2、0.84、0.328、
  0.7376 と、**定常状態の上下を往復しながら**近づきます
- `a = 1.1`、`b = -0.2` にすると、|a| > 1 なので、x(20) は −11.455 で、
  定常状態（2.0）から**遠ざかります**
- `supply_slope = 4`（供給の傾きが、需要の傾き 3 より大きい）にすると、
  蜘蛛の巣の係数は a = −1.3333 で、安定ではありません。`supply_slope = 3` なら、
  a = −1.0 で、これも安定ではありません
"""
        ),
    ]


def ch05_solow_model() -> list[NotebookNode]:
    return [
        intro("第 5 章 ソロー・モデル", "05-solow-model.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
saving_rate = 0.2    # 貯蓄率 s
depreciation = 0.05  # 減耗率 δ
alpha = 0.5          # 資本分配率 α
technology = 1.0     # 技術水準 A
capital_low = 4      # 資本が少ない国の、初期の資本
capital_high = 25    # 資本が多い国の、初期の資本
periods = 200        # 何期先まで計算するか
""",
            parameters=True,
        ),
        markdown("## 定常状態と、収束の速さ"),
        code(
            """
from lib.chapter05.solow import (
    convergence_speed,
    half_life,
    solow_path,
    steady_state_capital,
)

kstar = steady_state_capital(saving_rate, depreciation, alpha, technology)
print(f"定常状態の資本 k*: {kstar:.4f}")
speed = convergence_speed(alpha, depreciation)
print(f"収束の速さ λ: {speed:.4f}、半減期: {half_life(speed):.2f} 期")
for name, start in (("少ない国", capital_low), ("多い国", capital_high)):
    path = solow_path(start, saving_rate, depreciation, alpha, periods, technology)
    print(f"{name}: 初期 {start} → 1 期後 {path[1]:.4f} → {periods} 期後 "
          f"{path[periods]:.4f}")
"""
        ),
        markdown("## 図: ソロー・ダイアグラム（貯蓄と減耗）"),
        code(
            """
from lib.chapter05.plot import plot_solow_diagram

plot_solow_diagram(saving_rate, depreciation, alpha, technology)
"""
        ),
        markdown("## 図: 資本の経路"),
        code(
            """
from lib.chapter05.plot import plot_solow_convergence

plot_solow_convergence(
    [capital_low, capital_high], saving_rate, depreciation, alpha, periods, technology
)
"""
        ),
        markdown(
            """
## 試してみよう

- `saving_rate = 0.3` にすると、定常状態の資本 k* は、
  16 から 36 に増えます（(0.3 ÷ 0.05)^2 = 36）
- `depreciation = 0.1` にすると、k* は 4 に下がり、
  半減期は 27.38 期から 13.51 期に短くなります（収束が速くなります）
- `alpha = 0.3` にすると、k* は 7.2458、半減期は 19.46 期です
- `technology = 2.0` にすると、k* は 64 です
"""
        ),
    ]


def ch06_income_convergence() -> list[NotebookNode]:
    return [
        intro("第 6 章 所得の収束", "06-income-convergence.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
start_year = 1990  # 成長率を測る期間の始まり（データは 1990〜2019 年）
end_year = 2019    # 期間の終わり
use_controls = False  # True: 初期の資本・人的資本も説明変数に加える
""",
            parameters=True,
        ),
        markdown("## β 収斂の回帰"),
        code(
            """
from lib.chapter02.growth import load_panel
from lib.chapter06.convergence import (
    beta_convergence,
    half_life_years,
    implied_speed,
    income_growth,
)

panel = load_panel()
controls = ("k", "h") if use_controls else ()
result = beta_convergence(panel, start_year, end_year, controls)
beta = float(result.coefficients["ln_y0"])
years = end_year - start_year
print(f"傾き β: {beta:.4f}（初期の所得が高いほど、成長が遅いなら、負）")
print(result.coefficients.round(4).to_string())
print(f"決定係数: {result.r_squared:.3f}")
if beta < 0:
    speed = implied_speed(beta, years)
    print(f"収束の速さ λ: {speed:.4f}、半減期: {half_life_years(speed):.1f} 年")
"""
        ),
        markdown("## 図: 初期の所得と、その後の成長率"),
        code(
            """
import numpy as np

from lib.chapter03.plot import plot_regression

plot_regression(
    np.log(panel.xs(start_year, level="year")["y"]),
    income_growth(panel, start_year, end_year),
    xlabel=f"Initial income in {start_year} (log)",
    ylabel=f"Growth rate {start_year}-{end_year} (% per year)",
)
"""
        ),
        markdown(
            """
## 試してみよう

- `use_controls = True` にすると、初期の所得の係数 β は、−0.4846 から −0.2238 に、
  0 に近づきます。収束の速さから求めた半減期は、
  132.7 年から 299.6 年に伸びます（初期の資本・人的資本を一定にすると、
  収斂は遅く見えます）
- `start_year = 2000` にすると、β は −0.5323 です
"""
        ),
    ]


def ch07_purchasing_power_parity() -> list[NotebookNode]:
    return [
        intro("第 7 章 購買力平価", "07-purchasing-power-parity.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
local_price = 450      # 日本の商品の価格（円）
exchange_rate = 150    # 為替レート（円 / ドル）
us_price = 5.5         # 米国の同じ商品の価格（ドル）
""",
            parameters=True,
        ),
        markdown("## 価格のドル換算と、購買力平価"),
        code(
            """
from lib.chapter07.ppp import ppp_rate, price_in_dollars, relative_price_level

print("日本の価格（ドル）:", round(price_in_dollars(local_price, exchange_rate), 4))
print("PPP レート（円 / ドル）:", round(ppp_rate(local_price, us_price), 4))
level = relative_price_level(local_price, exchange_rate, us_price)
print("相対価格水準:", round(level, 4))
"""
        ),
        markdown("## 24 か国の相対価格水準とペン効果"),
        code(
            """
import numpy as np

from lib.chapter03.plot import plot_regression
from lib.chapter07.ppp import (
    load_prices,
    penn_effect_regression,
    relative_price_levels,
)

prices = load_prices()
levels = relative_price_levels(prices)
effect = penn_effect_regression(prices)
print(f"ペン効果の傾き（対数の所得 → 対数の相対価格水準）: "
      f"{float(effect.coefficients.iloc[1]):.3f}")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter07.plot import plot_relative_price_levels

plot_relative_price_levels(levels)
"""
        ),
        code(
            """
plot_regression(
    np.log(prices["income"]),
    np.log(levels),
    xlabel="Income per capita (log)",
    ylabel="Relative price level (log)",
)
"""
        ),
        markdown(
            """
## 試してみよう

- `exchange_rate = 81.8182` にすると、
  相対価格水準は 1.0 になります（為替レートが PPP レートと等しいとき）
- `us_price = 3.0` にすると、相対価格水準は 1.0 です（日本の価格が、ドルで 3.0 で、
  米国の価格と等しい）
- `exchange_rate = 100` にすると、日本の価格は 4.5 ドル、相対価格水準は 0.8182 です
"""
        ),
    ]


def ch08_random_variables() -> list[NotebookNode]:
    return [
        intro("第 8 章 確率変数と時系列", "08-random-variables.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
rho = 0.5         # AR(1) x(t) = ρ·x(t−1) + ε(t) の係数 ρ（0 は不可）
rho_other = 0.95  # 比べる相手の ρ（0 は不可）
sigma = 1.0       # ショック ε の標準偏差 σ
n = 100_000       # 系列の長さ（計算用）
n_plot = 100      # 図に描く系列の長さ
seed = 0          # 乱数の種（同じ種なら、同じ系列）
max_lag = 10      # 自己相関を、何ラグ先まで見るか
""",
            parameters=True,
        ),
        markdown("## 理論値と、標本の値"),
        code(
            """
import numpy as np

from lib.chapter08.stochastic import (
    ar1_autocorrelation,
    ar1_series,
    ar1_variance,
    sample_autocorrelation,
    shock_half_life,
)

print(f"理論の分散（ρ = {rho}）: {ar1_variance(rho, sigma):.4f}")
for r in (rho, rho_other):
    x = ar1_series(r, sigma, n, np.random.default_rng(seed))
    print(
        f"ρ = {r}: 標本の分散 {x.var():.3f}、"
        f"ラグ 1 の自己相関 {sample_autocorrelation(x, 1):.3f}、"
        f"範囲 {x.min():.1f} から {x.max():.1f}、半減期 {shock_half_life(r):.1f} 期"
    )
"""
        ),
        markdown("## 図: 2 つの ρ の系列"),
        code(
            """
from lib.chapter08.plot import plot_series

plot_series(
    {
        f"rho = {r}": ar1_series(r, sigma, n_plot, np.random.default_rng(seed))
        for r in (rho, rho_other)
    }
)
"""
        ),
        markdown("## 図: 自己相関（標本と理論）"),
        code(
            """
from lib.chapter08.plot import plot_acf
from lib.chapter08.stochastic import autocorrelation_function

series = ar1_series(rho, sigma, n, np.random.default_rng(seed))
plot_acf(
    autocorrelation_function(series, max_lag),
    [ar1_autocorrelation(rho, lag) for lag in range(max_lag + 1)],
)
"""
        ),
        markdown(
            """
## 試してみよう

- `sigma = 2.0` にすると、分散の理論値は 1.3333 から 5.3333 に、
  4 倍になります（分散は σ の 2 乗に比例します）
- `rho = 0.9`、`rho_other = -0.5` にすると、ρ = 0.9 の分散は 5.2632、
  半減期は 6.6 期です。ρ = −0.5 のラグ 1 の自己相関は **−0.504（負）** で、系列は、
  上下に交互に動きます
- `seed = 1` にすると、ρ = 0.5 の標本の分散は 1.311 です（種が違うと、
  標本は少し変わりますが、理論の 1.3333 に近いままです）
"""
        ),
    ]


def ch09_macro_data_features() -> list[NotebookNode]:
    return [
        intro("第 9 章 マクロ経済データの特徴", "09-macro-data-features.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
smoothing = 1600  # HP フィルターの平滑化の強さ λ（四半期データでは 1600）
series_name = "gdp"  # トレンドを描く系列（gdp・consumption・investment）
""",
            parameters=True,
        ),
        markdown("## 循環の統計"),
        code(
            """
import pandas as pd

from lib.chapter09.cycles import cycle_statistics, load_quarterly

df = load_quarterly()
stats = cycle_statistics(df, smoothing)
print("変動の大きさ（標準偏差）")
print(stats["volatility"].round(3).to_string())
print("GDP との相関")
print(stats["correlation_with_gdp"].round(3).to_string())
print("自己相関（ラグ 1）")
print(stats["autocorrelation"].round(3).to_string())
"""
        ),
        markdown("## 図: トレンドと循環"),
        code(
            """
from lib.chapter09.plot import plot_trend

plot_trend(pd.Series(df[series_name]), smoothing)
"""
        ),
        code(
            """
from lib.chapter09.cycles import log_cycle
from lib.chapter09.plot import plot_cycle

plot_cycle(
    pd.DataFrame(
        {
            name: log_cycle(pd.Series(df[name]), smoothing)
            for name in ("gdp", "consumption", "investment")
        }
    )
)
"""
        ),
        code(
            """
from lib.chapter09.plot import plot_volatility

plot_volatility(stats)
"""
        ),
        markdown(
            """
## 試してみよう

- `smoothing = 100` にすると、GDP の循環の標準偏差は 1.008 から 0.758 に、
  ラグ 1 の自己相関は 0.623 から 0.371 に下がります（トレンドが曲がりやすく、
  循環として残る部分が減ります）
- `smoothing = 100000` にすると、GDP の標準偏差は 1.200、
  自己相関は 0.722 に増えます（トレンドが直線に近づきます）
- どちらでも、投資が最も大きく動き、失業率は GDP と逆向き（相関 −0.94 から −0.97）
  に動く結果は、変わりません
"""
        ),
    ]


def ch10_okun_and_phillips() -> list[NotebookNode]:
    return [
        intro("第 10 章 オークンの法則とフィリップス曲線", "10-okun-and-phillips.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
smoothing = 1600   # HP フィルターの平滑化の強さ λ
split_year = 2000  # フィリップス曲線を、この年の前後で分ける
window = 40        # 傾きの推移を見る、窓の長さ（四半期）
""",
            parameters=True,
        ),
        markdown("## 回帰の傾き"),
        code(
            """
from lib.chapter09.cycles import load_quarterly
from lib.chapter10.okun_phillips import (
    okun_regression_from_data,
    phillips_by_period,
    phillips_regression_from_data,
)

df = load_quarterly()
okun = okun_regression_from_data(df, smoothing)
print("オークンの法則の傾き:", round(float(okun.coefficients["output_cycle"]), 3))
phillips = phillips_regression_from_data(df, smoothing)
print("フィリップス曲線の傾き（全期間）:",
      round(float(phillips.coefficients["unemployment_gap"]), 3))
parts = phillips_by_period(df, split_year, smoothing)
labels = {"before": f"{split_year} 年より前", "after": f"{split_year} 年以降"}
for name, label in labels.items():
    slope = float(parts[name].coefficients["unemployment_gap"])
    print(f"{label}の傾き: {slope:.3f}")
"""
        ),
        markdown("## 図: 傾きの推移（窓をずらして、回帰する）"),
        code(
            """
import pandas as pd

from lib.chapter09.cycles import cycle
from lib.chapter10.okun_phillips import rolling_slope
from lib.chapter10.plot import plot_rolling_slope

plot_rolling_slope(
    rolling_slope(
        cycle(pd.Series(df["unemployment"]), smoothing),
        pd.Series(df["inflation"]),
        window=window,
    )
)
"""
        ),
        markdown(
            """
## 試してみよう

- `split_year = 1995` にすると、フィリップス曲線の傾きは、1995 年より前が −0.504、
  1995 年以降が −0.241 です。分ける年を変えても、**あとのほうが平ら**になります
- `smoothing = 100` にすると、オークンの法則の傾きは −0.492、
  フィリップス曲線の傾き（全期間）は −0.351 です（HP フィルターの強さで、
  傾きは少し変わります）
"""
        ),
    ]


def ch11_inflation_and_money_stock() -> list[NotebookNode]:
    return [
        intro("第 11 章 インフレと貨幣量", "11-inflation-and-money-stock.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
money_growth = 5      # 貨幣の伸び率（% / 年）
real_growth = 1       # 実質成長率（% / 年）
velocity_growth = 0   # 流通速度の伸び率（% / 年）
max_inflation = 100   # 回帰に使う、物価上昇率（% / 年）の上限
""",
            parameters=True,
        ),
        markdown("## 貨幣数量説と、20 か国のパネル"),
        code(
            """
from lib.chapter11.money import (
    load_money_panel,
    money_inflation_regression,
    quantity_theory_inflation,
)

inflation = quantity_theory_inflation(money_growth, real_growth, velocity_growth)
print("物価上昇率:", inflation)
panel = load_money_panel()
whole = money_inflation_regression(panel)
print("回帰の傾き（全体）:", round(float(whole.coefficients["money_growth"]), 3))
moderate = money_inflation_regression(panel, max_inflation=max_inflation)
print("回帰の傾き（上限より下だけ）:",
      round(float(moderate.coefficients["money_growth"]), 3))
"""
        ),
        markdown("## 図: 貨幣の伸び率と物価上昇率"),
        code(
            """
import pandas as pd

from lib.chapter03.plot import plot_regression

kept = panel[panel["inflation"] <= max_inflation]
plot_regression(
    pd.Series(kept["money_growth"]),
    pd.Series(kept["inflation"]),
    xlabel="Money growth (% per year)",
    ylabel="Inflation (% per year)",
    label="Country-years",
)
"""
        ),
        markdown(
            """
## 試してみよう

- `real_growth = 3` にすると、物価上昇率は 2 です（貨幣が 5 % で、実質成長が 3 %）
- `money_growth = 10`、`real_growth = 0` にすると、物価上昇率は 10 です
- `velocity_growth = 2` にすると、物価上昇率は 6 です（流通速度が上がると、
  物価も上がります）
- `max_inflation = 1000` にすると、ハイパーインフレも含むので、
  回帰の傾きは全体と同じ 1.029 です
"""
        ),
    ]


def ch12_money_neutrality() -> list[NotebookNode]:
    return [
        intro("第 12 章 貨幣の中立性", "12-money-neutrality.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
break_period = "1973Q1"  # 固定相場から変動相場に切り替わった四半期
""",
            parameters=True,
        ),
        markdown("## 貨幣の中立性と、為替の制度の比較"),
        code(
            """
from lib.chapter11.money import load_money_panel
from lib.chapter12.exchange import (
    load_exchange,
    money_neutrality_regression,
    regime_statistics,
)

result = money_neutrality_regression(load_money_panel())
print("貨幣の伸び率の係数:", round(float(result.coefficients["money_growth"]), 4))
print("t 値:", round(float(result.t_values()["money_growth"]), 2))

exchange = load_exchange()
stats = regime_statistics(exchange, break_period)
print("名目の変動の大きさ（固定、変動）:",
      stats["nominal_volatility"].round(3).tolist())
print("実質の変動の大きさ（固定、変動）:", stats["real_volatility"].round(3).tolist())
print("名目と実質の変化率の相関（固定、変動）:", stats["correlation"].round(3).tolist())
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter12.plot import plot_exchange_rates

plot_exchange_rates(exchange, break_period)
"""
        ),
        code(
            """
from lib.chapter12.plot import plot_regime_volatility

plot_regime_volatility(stats)
"""
        ),
        markdown(
            """
## 試してみよう

- `break_period = "1980Q1"` にすると、固定相場側の名目の変動の大きさは、
  0.126 から 1.69 に増え、名目と実質の変化率の相関は 0.979 です。
  実際の切り替え（1973Q1）より遅らせると、変動相場の時期が、固定相場側に混ざります
- `break_period = "1990Q1"` にすると、固定相場側の名目の変動の大きさは 2.029、
  変動相場側は 3.187 です
"""
        ),
    ]


def ch13_adas_calibration() -> list[NotebookNode]:
    return [
        intro("第 13 章 AD-AS モデルのキャリブレーション", "13-adas-calibration.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
a = 0.8        # AS 曲線の傾き
c = 0.3        # AD 曲線の傾き
sigma_u = 1.5  # 需要ショックの標準偏差
sigma_v = 1.2  # 供給ショックの標準偏差
deviation = 1.0  # 今期の物価の乖離（%）
""",
            parameters=True,
        ),
        markdown("## 物価の持続性 h"),
        code(
            """
from lib.chapter13.adas import AdasParameters

params = AdasParameters(a=a, c=c, sigma_u=sigma_u, sigma_v=sigma_v)
print(f"h = 1 ÷ (1 + a·c) = {params.h:.4f}")
next_deviation = deviation * params.h
print(f"ショックがなければ、{deviation}% の乖離は、次の期に {next_deviation:.4f} %")
"""
        ),
        markdown("## モデルの特徴と、データの特徴"),
        code(
            """
from lib.chapter13.adas import (
    adas_cycles,
    data_features,
    load_adas_quarterly,
    model_moments,
)

cycles = adas_cycles(load_adas_quarterly())
data = data_features(cycles["y"], cycles["p"])
model = model_moments(params)
for key in data:
    print(f"{key}: データ {data[key]:.3f}、モデル {model[key]:.3f}")
"""
        ),
        markdown("## 図: データとモデルの比較"),
        code(
            """
from lib.chapter13.plot import plot_moment_comparison

plot_moment_comparison(data, model)
"""
        ),
        markdown(
            """
## 試してみよう

- `a = 1.6` にすると、h は 0.8065 から 0.6757 に下がり、
  モデルの物価の自己相関も 0.676 に下がります
- `a = 0.4`、`c = 0.6` にすると、a·c は変わらないので、h は 0.8065 のままで、
  モデルの物価の自己相関も 0.806 のままです。ただし、産出量の標準偏差は 1.608、
  産出量の自己相関は 0.240 に変わります
- `sigma_u = 0.5` にすると、モデルの産出量の標準偏差は 1.364 から 0.649 に下がります
"""
        ),
    ]


def ch14_adas_simulation() -> list[NotebookNode]:
    return [
        intro("第 14 章 AD-AS モデルのシミュレーション", "14-adas-simulation.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
a = 0.8          # AS 曲線の傾き
c = 0.3          # AD 曲線の傾き
sigma_u = 1.5    # 需要ショックの標準偏差
sigma_v = 1.2    # 供給ショックの標準偏差
u = 1.0          # 1 期間だけの需要ショック（%）
v = 0.0          # 1 期間だけの供給ショック（%）
periods_after = 20  # ショックのあと、何期間を見るか
n = 100          # ショックが毎期起きるシミュレーションの長さ
seed = 0         # 乱数の種
""",
            parameters=True,
        ),
        markdown("## ショックへの反応"),
        code(
            """
import numpy as np

from lib.chapter13.adas import AdasParameters
from lib.chapter14.simulation import impulse_response, price_half_life, simulate

params = AdasParameters(a=a, c=c, sigma_u=sigma_u, sigma_v=sigma_v)
df = impulse_response(params, u=u, v=v, periods_after=periods_after)
shock = df.iloc[3]
after = df.iloc[4]
print(f"ショックの期: 物価 {shock['p']:.4f}、産出量 {shock['y']:.4f}")
print(f"次の期: 産出量 {after['y']:.4f}")
print(f"半減期: {price_half_life(params):.2f} 四半期")
simulation = simulate(params, n, np.random.default_rng(seed))
std_y = simulation["y"].std()
print(f"毎期ショックのシミュレーションの産出量の標準偏差: {std_y:.4f}")
"""
        ),
        markdown("## 図: ショックへの反応"),
        code(
            """
from lib.chapter14.plot import plot_impulse_response

plot_impulse_response(df)
"""
        ),
        markdown("## 図: 毎期ショックが起きるシミュレーション"),
        code(
            """
from lib.chapter14.plot import plot_simulation

plot_simulation(simulation)
"""
        ),
        markdown(
            """
## 試してみよう

- `u = 0.0`、`v = 1.0` にすると、供給ショックなので、ショックの期は、
  物価が 0.8065 に上がり、産出量は −0.2419 に下がります
- `a = 1.6` にすると、半減期は 3.22 四半期から 1.77 四半期に短くなり、
  物価は速く元に戻ります
- `seed = 1` にすると、毎期ショックのシミュレーションの産出量の標準偏差は、
  1.2153 から 1.1425 に変わります（種が変わると、乱数が変わります）
"""
        ),
    ]


def ch15_is_mp_pc() -> list[NotebookNode]:
    return [
        intro("第 15 章 IS-MP-PC モデル", "15-is-mp-pc.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
a = 1.0         # IS 曲線の傾き
b = 0.25        # フィリップス曲線の傾き
c = 1.5         # MP 曲線のインフレ率への反応
d = 0.5         # MP 曲線の産出量への反応
shock_pc = 1.0  # 1 期間だけの、フィリップス曲線へのショック
shock_mp = 0.0  # 1 期間だけの、金融政策のショック
""",
            parameters=True,
        ),
        markdown("## ショックへの反応"),
        code(
            """
from lib.chapter15.ismppc import IsMpPcParameters, impulse_response

params = IsMpPcParameters(a=a, b=b, c=c, d=d)
df = impulse_response(params, shock_pc=shock_pc, shock_mp=shock_mp)
shock = df.iloc[3]
after = df.iloc[4]
pi_star = params.pi_star
print(f"ショックの期: インフレ率 {shock['pi']:.4f}、産出量 {shock['y']:.4f}")
print(f"次の期のインフレ率の乖離: {after['pi'] - pi_star:.4f}")
print(f"φ = {params.phi:.4f}（乖離は、毎期 φ 倍になる）")
"""
        ),
        markdown("## 図: ショックへの反応"),
        code(
            """
from lib.chapter15.plot import plot_responses

plot_responses(df)
"""
        ),
        markdown("## 図: 金融政策の姿勢の比較（基本と、産出量を重視）"),
        code(
            """
from lib.chapter15.plot import plot_stance_comparison

plot_stance_comparison(
    impulse_response(IsMpPcParameters(a=a, b=b), shock_pc=shock_pc),
    df,
)
"""
        ),
        markdown(
            """
## 試してみよう

- `c = 0.5`、`d = 1.5` にすると、産出量の落ち込みは小さく（99.8095）なりますが、
  インフレ率は 2.9524 に上がり、φ は 0.9524 に大きくなります（乖離が長く続きます）
- `shock_pc = 0.0`、`shock_mp = 1.0` にすると、金融政策のショックで、
  インフレ率は 1.8667 に、産出量は 99.4667 に下がります
- `c = 3.0` にすると、φ は 0.6667 に下がり、
  次の期のインフレ率の乖離は 0.4444 です（インフレ率に強く反応するほど、
  乖離は早く縮みます）
"""
        ),
    ]


def ch16_stochastic_solow() -> list[NotebookNode]:
    return [
        intro("第 16 章 確率的ソロー・モデル", "16-stochastic-solow.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
alpha = 0.36         # 資本分配率 α
saving = 0.2         # 貯蓄率 s
depreciation = 0.025  # 減耗率 δ
rho = 0.6            # TFP のショックの持続性 ρ
sigma = 0.008        # TFP のショックの標準偏差 σ
hours = 1.0          # 総労働時間 H
n = 200              # シミュレーションの期間
seed = 123           # 乱数の種
""",
            parameters=True,
        ),
        markdown("## シミュレーション"),
        code(
            """
import numpy as np

from lib.chapter16.solow_stochastic import (
    SolowParameters,
    log_deviations,
    stochastic_solow,
)

params = SolowParameters(
    alpha=alpha,
    saving=saving,
    depreciation=depreciation,
    rho=rho,
    sigma=sigma,
    hours=hours,
)
dev = log_deviations(stochastic_solow(params, n, np.random.default_rng(seed)), params)
print("GDP の乖離の標準偏差（%）:", round(float(dev["y"].std()), 4))
print("消費 ÷ GDP の標準偏差の比:", round(float(dev["c"].std() / dev["y"].std()), 4))
print("投資 ÷ GDP の標準偏差の比:", round(float(dev["i"].std() / dev["y"].std()), 4))
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter16.plot import plot_solow_simulation

plot_solow_simulation(dev)
"""
        ),
        markdown("## 景気循環の分解（データ）"),
        code(
            """
from lib.chapter16.plot import plot_decomposition
from lib.chapter16.solow_stochastic import (
    business_cycle_components,
    decompose_business_cycle,
    load_solow_quarterly,
)

cycles = business_cycle_components(load_solow_quarterly(), alpha)
shares = decompose_business_cycle(cycles, alpha)
print("GDP の分散に占める割合:", shares.round(3).to_dict())
plot_decomposition(shares)
"""
        ),
        markdown(
            """
## 試してみよう

- `rho = 0.9` にすると、
  GDP の乖離の標準偏差は 0.885 から 1.302 に増えます（ショックが長く残ります）
- `sigma = 0.016` にすると、標準偏差は 1.77 で、ほぼ 2 倍です
- `seed = 1` にすると、標準偏差は 0.8054 です。消費・投資の比は、
  種や貯蓄率を変えても、1.0 のままです（貯蓄率が一定だからです）
- `alpha = 0.5` にすると、データの分解は、TFP が 0.676、労働が 0.328 に変わります
"""
        ),
    ]


def ch17_log_linearization() -> list[NotebookNode]:
    return [
        intro("第 17 章 対数線形近似", "17-log-linearization.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
alpha = 0.5          # 資本分配率 α
saving = 0.2         # 貯蓄率 s
depreciation = 0.05  # 減耗率 δ
initial_deviation = 0.5  # 定常状態からの、最初の資本の乖離（0.5 は 50%）
periods = 60         # 何期先まで計算するか
""",
            parameters=True,
        ),
        markdown("## 遷移係数と、線形近似の誤差"),
        code(
            """
import numpy as np

from lib.chapter16.solow_stochastic import SolowParameters
from lib.chapter17.loglinear import (
    capital_paths,
    linear_transition,
    log_linearize,
    solow_equations,
    steady_state_capital,
)

params = SolowParameters(
    alpha=alpha, saving=saving, depreciation=depreciation, hours=1.0
)
k_star = steady_state_capital(params)
transition = linear_transition(
    *log_linearize(solow_equations(params), np.array([1.0, k_star]))
)
print(f"遷移係数: {float(transition[1, 1]):.4f}")
print(f"1 − (1 − α)·δ: {1 - (1 - alpha) * depreciation:.4f}")

paths = capital_paths(params, initial_deviation=initial_deviation, periods=periods)
max_error = float((paths["exact"] - paths["linear"]).abs().max())
print(f"最大の誤差: {max_error:.4f} %（最初の乖離は {100 * initial_deviation:.0f} %）")
"""
        ),
        markdown("## 図: 厳密な経路と、線形近似の経路"),
        code(
            """
from lib.chapter17.plot import plot_exact_vs_linear

plot_exact_vs_linear(paths)
"""
        ),
        markdown(
            """
## 試してみよう

- `initial_deviation = 0.01` にすると、最大の誤差は 0.0006 % です。`0.1`
   なら 0.0609 % で、乖離が大きいほど、誤差が大きくなります
- `depreciation = 0.1` にすると、遷移係数は 0.95（= 1 − 0.5 × 0.1）で、
  最大の誤差は 1.4835 % です
"""
        ),
    ]


def ch18_rbc_model() -> list[NotebookNode]:
    return [
        intro("第 18 章 RBC モデル", "18-rbc-model.md"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
alpha = 0.36        # 資本分配率 α
beta = 0.99         # 割引因子 β
delta = 0.025       # 減耗率 δ
rho = 0.551         # TFP のショックの持続性 ρ
shock = 0.01        # 1 期間だけの TFP ショック（0.01 は 1%）
endogenous_labour = False  # True にすると、労働時間も、内生的に決まる
""",
            parameters=True,
        ),
        markdown("## 定常状態と、ショックへの反応"),
        code(
            """
from lib.chapter18.rbc import (
    RbcParameters,
    impulse_response,
    solve_rbc,
    steady_state,
)

params = RbcParameters(alpha=alpha, beta=beta, delta=delta, rho=rho)
ss = steady_state(params)
print(f"実質利子率 R: {ss['r']:.4f}、K ÷ Y: {ss['k'] / ss['y']:.2f}")

df = impulse_response(solve_rbc(params, endogenous_labour), shock=shock)
first = df.iloc[3]
for name, label in (("y", "産出量"), ("c", "消費"), ("i", "投資")):
    print(f"ショックの期の{label}: {first[name]:.2f} %")
"""
        ),
        markdown("## 図: ショックへの反応"),
        code(
            """
from lib.chapter18.plot import plot_rbc_responses

plot_rbc_responses(df)
"""
        ),
        markdown(
            """
## 試してみよう

- `endogenous_labour = True` にすると、
  ショックの期の産出量は 1.00 % から 1.65 % に、投資は 3.65 % から 6.05 % に、
  大きくなります
- `rho = 0.9` にすると、消費は 0.09 % から 0.21 % に、
  投資は 3.28 % に変わります（ショックが長く続くと、消費の反応は大きくなります）
- `alpha = 1 / 3` にすると、K ÷ Y は 9.50 です
- `shock = 0.02` にすると、産出量 2.00 %、消費 0.17 %、投資 7.29 % で、
  反応はほぼ 2 倍です
"""
        ),
    ]


NOTEBOOKS: dict[str, Callable[[], list[NotebookNode]]] = {
    "ch01_development_accounting": ch01_development_accounting,
    "ch02_growth_accounting": ch02_growth_accounting,
    "ch03_regression": ch03_regression,
    "ch04_difference_equations": ch04_difference_equations,
    "ch05_solow_model": ch05_solow_model,
    "ch06_income_convergence": ch06_income_convergence,
    "ch07_purchasing_power_parity": ch07_purchasing_power_parity,
    "ch08_random_variables": ch08_random_variables,
    "ch09_macro_data_features": ch09_macro_data_features,
    "ch10_okun_and_phillips": ch10_okun_and_phillips,
    "ch11_inflation_and_money_stock": ch11_inflation_and_money_stock,
    "ch12_money_neutrality": ch12_money_neutrality,
    "ch13_adas_calibration": ch13_adas_calibration,
    "ch14_adas_simulation": ch14_adas_simulation,
    "ch15_is_mp_pc": ch15_is_mp_pc,
    "ch16_stochastic_solow": ch16_stochastic_solow,
    "ch17_log_linearization": ch17_log_linearization,
    "ch18_rbc_model": ch18_rbc_model,
}


def main() -> None:
    for name, build in sorted(NOTEBOOKS.items()):
        path = NOTEBOOKS_DIR / f"{name}.ipynb"
        write(path, build())
        print(f"生成: {path.name}")


if __name__ == "__main__":
    main()
