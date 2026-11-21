"""スルツキー分解と、財の種類。

価格が変わると、需要は、2 つの理由で動く。
- 代替効果: 価格比が変わり、割安になった財に、乗り換える（同じ無差別曲線の上の動き）
- 所得効果: 実質所得が変わり、買える量が変わる（予算線の平行移動）
価格効果 = 代替効果 + 所得効果。
"""

from dataclasses import dataclass

from lib.chapter01.utility import cobb_douglas_utility
from lib.chapter01.validation import validate_non_negative, validate_positive
from lib.chapter02.budget import optimal_bundle

# 効果の符号の判定で、同じ値と見なす誤差
_TOLERANCE = 1e-9


@dataclass(frozen=True)
class SlutskyResult:
    """財 x のスルツキー分解。3 つの点と、3 つの効果（財 x の量の変化）。"""

    original: tuple[float, float]
    substitution: tuple[float, float]
    final: tuple[float, float]
    substitution_effect: float
    income_effect: float
    price_effect: float


def compensated_bundle(
    utility_level: float, px: float, py: float, a: float = 1.0, b: float = 1.0
) -> tuple[float, float]:
    """新しい価格のもとで、効用 utility_level を、最も安く達成する点（補償需要）。

    最適点では MRS = Px ÷ Py なので、y = (b ÷ a)(Px ÷ Py)·x。
    これを効用の式に入れて、x を求める。
    """
    validate_positive(utility_level, "効用の水準は、正にする")
    validate_positive(px, "財 x の価格は、正にする")
    validate_positive(py, "財 y の価格は、正にする")
    ratio = (b / a) * (px / py)
    x = (utility_level / ratio**b) ** (1 / (a + b))
    return x, ratio * x


def slutsky_decomposition(
    income: float,
    px_old: float,
    px_new: float,
    py: float,
    a: float = 1.0,
    b: float = 1.0,
) -> SlutskyResult:
    """財 x の価格が px_old から px_new に変わったときの、スルツキー分解。"""
    original = optimal_bundle(income, px_old, py, a, b)
    level = cobb_douglas_utility(*original, a, b)
    substitution = compensated_bundle(level, px_new, py, a, b)
    final = optimal_bundle(income, px_new, py, a, b)
    return SlutskyResult(
        original,
        substitution,
        final,
        substitution[0] - original[0],
        final[0] - substitution[0],
        final[0] - original[0],
    )


def classify_by_effects(substitution_effect: float, income_effect: float) -> str:
    """値下げのときの 2 つの効果から、財の種類を決める。

    代替効果は、値下げで必ず正。所得効果が正なら上級財、負なら下級財。
    所得効果の負が、代替効果より大きければ、価格効果が負になる、ギッフェン財。
    """
    validate_positive(substitution_effect, "代替効果は、値下げで必ず正になる")
    if abs(income_effect) <= _TOLERANCE:
        return "中立財"
    if income_effect > 0:
        return "上級財"
    if -income_effect > substitution_effect + _TOLERANCE:
        return "ギッフェン財"
    return "下級財"


def _check_prices(income: float, px: float, py: float) -> None:
    validate_non_negative(income, "所得は、0 以上にする")
    validate_positive(px, "財 x の価格は、正にする")
    validate_positive(py, "財 y の価格は、正にする")


def demand_perfect_substitutes(income: float, px: float, py: float) -> float:
    """完全代替財（U = x + y）の財 x の需要。安いほうだけを買う（同じなら財 x）。"""
    _check_prices(income, px, py)
    return income / px if px <= py else 0.0


def demand_perfect_complements(income: float, px: float, py: float) -> float:
    """完全補完財（U = min(x, y)）の財 x の需要。1 組の値段 Px + Py で、所得を割る。"""
    _check_prices(income, px, py)
    return income / (px + py)


def cross_price_relation(change_in_demand: float) -> str:
    """財 y の値上げで財 x の需要が、増えれば代替財、減れば補完財、不変なら独立財。"""
    if change_in_demand > _TOLERANCE:
        return "代替財"
    if change_in_demand < -_TOLERANCE:
        return "補完財"
    return "独立財"
