"""生産関数と費用最小化。

生産関数 q = L^α · K^β（L: 労働、K: 資本）。限界生産性は、投入を増やすほど逓減する。
費用最小化は、消費者の効用最大化（第 2 章）と、同じ形をしている。
- 等産出量曲線（無差別曲線に相当）: 同じ生産量になる (L, K) の組
- 等費用線（予算線に相当）: w·L + r·K = 費用。傾きは −w ÷ r
- 最適点では、技術的限界代替率 MRTS = w ÷ r（等産出量曲線と等費用線が接する）
"""

from lib.chapter01.validation import validate_non_negative, validate_positive


def _check_exponents(alpha: float, beta: float) -> None:
    validate_positive(alpha, "べき指数 α は、正にする")
    validate_positive(beta, "べき指数 β は、正にする")


def _check_prices(w: float, r: float) -> None:
    validate_positive(w, "賃金（労働の価格）は、正にする")
    validate_positive(r, "資本の価格は、正にする")


def production(
    labor: float, capital: float, alpha: float = 0.5, beta: float = 0.5
) -> float:
    """生産量 q = L^α · K^β。投入量が増えると、生産量が増える。"""
    validate_non_negative(labor, "労働の投入量は、0 以上にする")
    validate_non_negative(capital, "資本の投入量は、0 以上にする")
    _check_exponents(alpha, beta)
    return float(labor**alpha * capital**beta)


def marginal_product_labor(
    labor: float, capital: float, alpha: float = 0.5, beta: float = 0.5
) -> float:
    """労働の限界生産性 MPL = α · q ÷ L。労働が増えると、逓減する。"""
    validate_positive(labor, "労働の投入量は、正にする")
    return alpha * production(labor, capital, alpha, beta) / labor


def marginal_product_capital(
    labor: float, capital: float, alpha: float = 0.5, beta: float = 0.5
) -> float:
    """資本の限界生産性 MPK = β · q ÷ K。資本が増えると、逓減する。"""
    validate_positive(capital, "資本の投入量は、正にする")
    return beta * production(labor, capital, alpha, beta) / capital


def isocost_slope(w: float, r: float) -> float:
    """等費用線の傾き −w ÷ r（賃金と資本の価格の比のマイナス）。"""
    _check_prices(w, r)
    return -w / r


def isocost_k(cost: float, w: float, r: float, labor: float) -> float:
    """等費用線の上の、資本の量。K = (費用 − w·L) ÷ r。"""
    _check_prices(w, r)
    return (cost - w * labor) / r


def isoquant_k(
    quantity: float, labor: float, alpha: float = 0.5, beta: float = 0.5
) -> float:
    """等産出量曲線の上の、資本の量。q = L^α · K^β から、K = (q ÷ L^α)^(1/β)。"""
    validate_positive(quantity, "生産量は、正にする")
    validate_positive(labor, "労働の投入量は、正にする")
    _check_exponents(alpha, beta)
    return float((quantity / labor**alpha) ** (1 / beta))


def mrts(labor: float, capital: float, alpha: float = 0.5, beta: float = 0.5) -> float:
    """技術的限界代替率 MRTS = MPL ÷ MPK = (α·K) ÷ (β·L)。

    等産出量曲線の、接線の傾きの大きさ。
    """
    validate_positive(labor, "労働の投入量は、正にする")
    validate_non_negative(capital, "資本の投入量は、0 以上にする")
    _check_exponents(alpha, beta)
    return (alpha * capital) / (beta * labor)


def cost_minimizing_inputs(
    quantity: float, w: float, r: float, alpha: float = 0.5, beta: float = 0.5
) -> tuple[float, float]:
    """生産量 q を、最も安く作る (L, K)（閉じた式）。

    最適点では MRTS = w ÷ r なので、K = (β ÷ α)(w ÷ r)·L。
    これを生産関数に入れて、L を求める。
    """
    validate_positive(quantity, "生産量は、正にする")
    _check_prices(w, r)
    _check_exponents(alpha, beta)
    ratio = (beta / alpha) * (w / r)
    labor = (quantity / ratio**beta) ** (1 / (alpha + beta))
    return float(labor), float(ratio * labor)


def cost_minimizing_inputs_by_grid(
    quantity: float,
    w: float,
    r: float,
    alpha: float = 0.5,
    beta: float = 0.5,
    steps: int = 400,
    l_max: float = 100.0,
) -> tuple[float, float]:
    """等産出量曲線の上を steps 等分して、費用が最小の点を探す（答え合わせ用）。"""
    validate_positive(steps - 1, "格子の分割数は、2 以上にする")
    validate_positive(l_max, "労働の探索の上限は、正にする")
    _check_prices(w, r)
    labors = [l_max * i / steps for i in range(1, steps + 1)]
    points = [(x, isoquant_k(quantity, x, alpha, beta)) for x in labors]
    return min(points, key=lambda p: w * p[0] + r * p[1])


def minimum_cost(
    quantity: float, w: float, r: float, alpha: float = 0.5, beta: float = 0.5
) -> float:
    """生産量 q を作る、最小の費用 w·L + r·K。"""
    labor, capital = cost_minimizing_inputs(quantity, w, r, alpha, beta)
    return w * labor + r * capital
