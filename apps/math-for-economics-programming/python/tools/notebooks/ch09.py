"""第 9 章のノートブック（セルの並び）。"""

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import code, markdown
from tools.notebooks.common import title

NAME = "ch09_matrices_and_regression"


def cells() -> list[NotebookNode]:
    """ノートブックのセルの並び。"""
    return [
        title(9, "行列と回帰分析", "09-matrices-and-regression"),
        code(
            """
# --- Parameters: ここの数字を書き換えます ---
matrix = [[4, 7], [2, 6]]  # 行列式と逆行列を調べる正方行列（行のリスト）
intercept = 120            # データを作る「真の」需要 q = β₀ + β₁·p の切片 β₀
slope = -2                 # 真の傾き β₁
noise_sd = 5               # 誤差の標準偏差（0 以上。0 ならデータは直線にちょうど乗る）
seed = 3                   # 乱数の種（同じ種なら、同じデータになる）
prices = [10, 15, 20, 25, 30, 35, 40, 45, 50]  # 価格（2 つ以上の違う値）
""",
            parameters=True,
        ),
        markdown("## 行列式と逆行列"),
        code(
            """
from lib.chapter09.matrix import (
    is_singular_matrix,
    matrix_determinant,
    matrix_inverse,
    matrix_product,
)

print(f"行列式: {matrix_determinant(matrix):.6g}")
if is_singular_matrix(matrix):
    print("特異な行列です（逆行列はありません）")
else:
    inverse = matrix_inverse(matrix)
    print("逆行列:", [[round(x, 6) for x in row] for row in inverse])
    check = matrix_product(matrix, inverse)
    print("A × A⁻¹:", [[round(x, 6) + 0.0 for x in row] for row in check])
"""
        ),
        markdown("## データを作り、最小 2 乗法で当てはめる"),
        code(
            """
from lib.chapter07.vectors import vector_dot
from lib.chapter09.regression import (
    coefficient_of_determination,
    least_squares_beta,
    noisy_regression_sample,
    regression_design_matrix,
    regression_residuals,
    simple_regression_coefficients,
)

design = regression_design_matrix([prices])
quantities = noisy_regression_sample(design, [intercept, slope], noise_sd, seed=seed)
print("数量:", [round(q, 2) for q in quantities])

b0, b1 = simple_regression_coefficients(prices, quantities)
beta = least_squares_beta(design, quantities)
print(f"単回帰の公式:   β₀ = {b0:.4f}、β₁ = {b1:.4f}")
print(f"行列の正規方程式: β₀ = {beta[0]:.4f}、β₁ = {beta[1]:.4f}")

residuals = regression_residuals(design, quantities, beta)
r2 = coefficient_of_determination(quantities, residuals)
print(f"決定係数 R² = {r2:.4f}")
print(f"残差の和 = {sum(residuals):.1e}、価格と残差の内積 = "
      f"{vector_dot(prices, residuals):.1e}（どちらも、ほぼ 0）")
"""
        ),
        markdown("## 図"),
        code(
            """
from lib.chapter09.plot import plot_regression_with_residuals

plot_regression_with_residuals(prices, quantities)
"""
        ),
        code(
            """
from lib.chapter09.plot import plot_residuals_against_x

plot_residuals_against_x(prices, quantities)
"""
        ),
        markdown(
            """
## 試してみよう

- `noise_sd` を 0 にすると、データは直線にちょうど乗り、β = (120, −2)・R² = 1
  になります。5 のとき（既定）は β ≈ (122.12, −2.15)・R² ≈ 0.956 です
- `noise_sd` を 20 にすると β ≈ (128.47, −2.61)・R² ≈ 0.668、50 にすると
  β ≈ (141.17, −3.53)・R² ≈ 0.370 です。このデータでは、誤差が大きいほど、推定が
  真の値から離れ、R² が下がります
- `seed` を 4 に変えると、同じ式から別のデータができ、β ≈ (122.81, −2.13)
  になります。推定値は、データの偶然によって変わります
- `slope` を 0 にする（価格と数量に関係がない）と、R² ≈ 0.099 に下がります
- `matrix` を `[[1, 2], [2, 4]]`（2 行目が 1 行目の 2 倍）にすると、行列式は 0 で、
  「特異な行列です」と表示されます
"""
        ),
    ]
