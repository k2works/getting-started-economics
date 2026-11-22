"""等比数列・級数と、貯蓄・債券・株価の割引現在価値。"""


def geometric_term(first: float, ratio: float, n: int) -> float:
    """等比数列の第 n 項 = 初項 × 公比^(n − 1)。n は 1 から数える。"""
    if n < 1:
        raise ValueError("第 n 項の n は 1 以上でなければなりません")
    return first * ratio ** (n - 1)


def geometric_partial_sum(first: float, ratio: float, n: int) -> float:
    """等比数列の、初項から第 n 項までの和 S_n = a(1 − r^n) ÷ (1 − r)。"""
    if n < 0:
        raise ValueError("項数は 0 以上でなければなりません")
    if ratio == 1:
        return first * n
    return first * (1 - ratio**n) / (1 - ratio)


def geometric_series_limit(first: float, ratio: float) -> float:
    """無限級数 a + ar + ar² + … = a ÷ (1 − r)。|r| < 1 のときだけ収束する。"""
    if abs(ratio) >= 1:
        raise ValueError("公比の絶対値が 1 以上では、無限級数は収束しません")
    return first / (1 - ratio)


def partial_sums(first: float, ratio: float, n: int) -> list[float]:
    """第 1 項までの和、第 2 項までの和、…、第 n 項までの和の列。"""
    return [geometric_partial_sum(first, ratio, k) for k in range(1, n + 1)]


def terms_until_within(first: float, ratio: float, tolerance: float) -> int:
    """部分和と無限級数の差が、tolerance より小さくなる、最初の項数 n。"""
    if tolerance <= 0:
        raise ValueError("許容誤差は正でなければなりません（0 では、終わりません）")
    limit = geometric_series_limit(first, ratio)
    n = 1
    while abs(limit - geometric_partial_sum(first, ratio, n)) >= tolerance:
        n += 1
    return n


def _require_rate_above_minus_one(rate: float) -> None:
    if rate <= -1:
        raise ValueError(
            "利子率が −100% 以下では、割り引くことも、積み立てることもできません"
        )


def annuity_present_value(payment: float, rate: float, periods: int) -> float:
    """毎期末に payment を periods 期受け取る年金の現在価値 C(1 − (1 + r)^−n) ÷ r。"""
    _require_rate_above_minus_one(rate)
    discount = 1 / (1 + rate)
    return geometric_partial_sum(payment * discount, discount, periods)


def perpetuity_present_value(payment: float, rate: float) -> float:
    """毎期末に payment を、永久に受け取る債券（コンソル債）の現在価値 C ÷ r。"""
    if rate <= 0:
        raise ValueError("利子率が正でなければ、永久債の現在価値は決まりません")
    return payment / rate


def savings_future_value(payment: float, rate: float, periods: int) -> float:
    """毎期末に payment を積み立てたときの、periods 期末の残高 C((1 + r)^n − 1) ÷ r。"""
    _require_rate_above_minus_one(rate)
    return geometric_partial_sum(payment, 1 + rate, periods)


def coupon_bond_price(face: float, coupon: float, rate: float, years: int) -> float:
    """利付債の価格: 毎年のクーポンの現在価値の和 + 満期の額面の現在価値。"""
    return annuity_present_value(coupon, rate, years) + face / (1 + rate) ** years


def iterate_map(a: float, b: float, start: float, steps: int) -> list[float]:
    """漸化式 x(t + 1) = a·x(t) + b を、x(0) = start から steps 回、反復した列。"""
    path = [start]
    for _ in range(steps):
        path.append(a * path[-1] + b)
    return path


def affine_fixed_point(a: float, b: float) -> float:
    """x = a·x + b を満たす不動点 b ÷ (1 − a)。a = 1 では、不動点がない。"""
    if a == 1:
        raise ValueError("a = 1 では、x = x + b を満たす点がありません")
    return b / (1 - a)


def gordon_stock_price(dividend: float, rate: float, growth: float) -> float:
    """配当割引モデル（ゴードン）: 来期の配当 D が率 g で増え続けるときの株価。

    株価 = D ÷ (r − g)。r > g のときだけ、決まる。
    """
    if rate <= growth:
        raise ValueError("利子率が成長率より大きくなければ、株価は決まりません")
    return dividend / (rate - growth)
