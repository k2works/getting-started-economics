"""コブ・ダグラス型の効用関数 U(x, y) = x^a * y^(1-a)。"""


def cobb_douglas_utility(x: float, y: float, alpha: float = 0.5) -> float:
    """財 x を x 単位、財 y を y 単位消費したときの効用を返す。"""
    if x < 0 or y < 0:
        raise ValueError("財の量は 0 以上でなければならない")
    return float(x**alpha * y ** (1 - alpha))


def marginal_rate_of_substitution(x: float, y: float, alpha: float = 0.5) -> float:
    """限界代替率 MRS = a / (1 - a) * y / x を返す。"""
    if x <= 0:
        raise ValueError("限界代替率は財 x の量が 0 より大きいときだけ求められる")
    return alpha / (1 - alpha) * y / x
