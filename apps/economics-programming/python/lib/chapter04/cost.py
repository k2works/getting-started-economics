"""費用関数 C(q) = q^3 - 6q^2 + 15q + 固定費用。"""


def total_cost(quantity: float, fixed_cost: float = 10) -> float:
    """生産量 q の総費用 C(q) = q^3 - 6q^2 + 15q + 固定費用 を返す。"""
    if quantity < 0:
        raise ValueError("生産量は 0 以上でなければならない")
    return quantity**3 - 6 * quantity**2 + 15 * quantity + fixed_cost


def marginal_cost(quantity: float) -> float:
    """限界費用 MC(q) = 3q^2 - 12q + 15 を返す（総費用を q で微分したもの）。"""
    return 3 * quantity**2 - 12 * quantity + 15


def average_cost(quantity: float, fixed_cost: float = 10) -> float:
    """平均費用 AC(q) = C(q) / q を返す。"""
    if quantity <= 0:
        raise ValueError("平均費用は生産量が 0 より大きいときだけ求められる")
    return total_cost(quantity, fixed_cost) / quantity


def average_variable_cost(quantity: float) -> float:
    """平均可変費用 AVC(q) = q^2 - 6q + 15 を返す。"""
    return quantity**2 - 6 * quantity + 15
