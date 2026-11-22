"""効用関数の偏微分（限界効用・限界代替率）と、予算制約のもとでの効用最大化。"""

from collections.abc import Sequence

from lib.chapter07.budget import budget_intercepts
from lib.chapter08.partial import Surface, numerical_partial_x, numerical_partial_y


def _check_share(share: float) -> None:
    if not 0 < share < 1:
        raise ValueError("指数 a は、0 より大きく 1 より小さくなければなりません")


def _two_good_intercepts(prices: Sequence[float], income: float) -> list[float]:
    """2 財の予算線の切片 [m ÷ p_x, m ÷ p_y]（第 7 章）。所得は 0 以上。"""
    if len(prices) != 2 or income < 0:
        raise ValueError("2 財の価格と、0 以上の所得が必要です")
    return budget_intercepts(prices, income)


def cobb_douglas_utility(x: float, y: float, share: float) -> float:
    """コブ・ダグラス型の効用 U = x^a·y^(1−a)。"""
    _check_share(share)
    if x < 0 or y < 0:
        raise ValueError("数量は 0 以上でなければなりません")
    return float(x**share * y ** (1 - share))


def cobb_douglas_indifference_y(level: float, x: float, share: float) -> float:
    """無差別曲線 x^a·y^(1−a) = U の上で、x のときの y = (U ÷ x^a)^(1 ÷ (1 − a))。"""
    _check_share(share)
    if x <= 0 or level < 0:
        raise ValueError("x が 0 以下か、効用水準が負では、無差別曲線が決まりません")
    return float((level / x**share) ** (1 / (1 - share)))


def cobb_douglas_marginal_utilities(
    x: float, y: float, share: float
) -> tuple[float, float]:
    """限界効用 (U_x, U_y) = (a·U ÷ x, (1 − a)·U ÷ y)（偏微分の公式）。"""
    if x <= 0 or y <= 0:
        raise ValueError("数量が 0 の点では、限界効用が決まりません")
    utility = cobb_douglas_utility(x, y, share)
    return share * utility / x, (1 - share) * utility / y


def cobb_douglas_mrs(x: float, y: float, share: float) -> float:
    """限界代替率 MRS = U_x ÷ U_y = (a ÷ (1 − a))·(y ÷ x)。"""
    mu_x, mu_y = cobb_douglas_marginal_utilities(x, y, share)
    return mu_x / mu_y


def numerical_mrs(utility: Surface, x: float, y: float) -> float:
    """どんな効用関数でも、偏微分の数値の比で、限界代替率を求める。"""
    return numerical_partial_x(utility, x, y) / numerical_partial_y(utility, x, y)


def cobb_douglas_demand(
    prices: Sequence[float], income: float, share: float
) -> tuple[float, float]:
    """効用最大化の解析解 x* = a·m ÷ p_x、y* = (1 − a)·m ÷ p_y。"""
    _check_share(share)
    x_max, y_max = _two_good_intercepts(prices, income)
    return share * x_max, (1 - share) * y_max


def cobb_douglas_lagrange_multiplier(
    prices: Sequence[float], income: float, share: float
) -> float:
    """最適点でのラグランジュ乗数 λ = U_x ÷ p_x（1 円あたりの限界効用）。"""
    x, y = cobb_douglas_demand(prices, income, share)
    mu_x, _ = cobb_douglas_marginal_utilities(x, y, share)
    return mu_x / prices[0]


def budget_line_bundles(
    prices: Sequence[float], income: float, points: int
) -> list[tuple[float, float]]:
    """予算線を points 個の点に等分する。財 2 の切片から、財 1 の切片まで。"""
    if points < 2:
        raise ValueError("格子の点は、2 つ以上必要です")
    x_max, y_max = _two_good_intercepts(prices, income)
    shares = [i / (points - 1) for i in range(points)]
    return [(t * x_max, (1 - t) * y_max) for t in shares]


def best_bundle_on_budget_line(
    utility: Surface, prices: Sequence[float], income: float, points: int
) -> tuple[float, float]:
    """格子探索: 予算線上の点を並べて、効用が最大の点を返す。"""
    bundles = budget_line_bundles(prices, income, points)
    return max(bundles, key=lambda bundle: utility(*bundle))


def quasilinear_utility(x: float, y: float, weight: float) -> float:
    """準線形効用 U = b·√x + y（y について線形）。"""
    if x < 0 or y < 0:
        raise ValueError("数量は 0 以上でなければなりません")
    return float(weight * x**0.5 + y)


def quasilinear_demand(
    prices: Sequence[float], income: float, weight: float
) -> tuple[float, float]:
    """MRS = b ÷ (2√x) = p_x ÷ p_y の x。所得で買えなければ、y = 0 の端点解。"""
    if weight <= 0:
        raise ValueError("重み b は、正でなければなりません")
    x_max, y_max = _two_good_intercepts(prices, income)
    x = (weight * prices[1] / (2 * prices[0])) ** 2
    if x >= x_max:
        return x_max, 0.0
    return x, y_max - prices[0] * x / prices[1]
