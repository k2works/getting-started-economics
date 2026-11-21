"""貨幣需要と LM 曲線（中核）。

貨幣需要 L = k·Y − h·r（k: 所得への感応度、h: 利子率への感応度）。
貨幣市場の均衡は、実質貨幣供給 M/P = L。
"""


def _check_k(k: float) -> None:
    if k <= 0:
        raise ValueError("貨幣需要の所得への感応度 k は、正にする")


def _check_h(h: float) -> None:
    if h <= 0:
        raise ValueError("貨幣需要の利子率への感応度 h は、正にする")


def money_demand(income: float, interest: float, k: float, h: float) -> float:
    """貨幣需要 L = k·Y − h·r。所得の増加関数で、利子率の減少関数。"""
    _check_k(k)
    _check_h(h)
    return k * income - h * interest


def lm_interest(income: float, real_money: float, k: float, h: float) -> float:
    """LM 曲線: 貨幣市場を均衡させる利子率 r = (k·Y − M/P) ÷ h。"""
    _check_k(k)
    _check_h(h)
    return (k * income - real_money) / h


def lm_income(interest: float, real_money: float, k: float, h: float) -> float:
    """LM 曲線: 貨幣市場を均衡させる所得 Y = (M/P + h·r) ÷ k。"""
    _check_k(k)
    _check_h(h)
    return (real_money + h * interest) / k


def lm_slope(k: float, h: float) -> float:
    """LM 曲線の傾き dr/dY = k ÷ h（所得を横軸、利子率を縦軸にしたとき）。"""
    _check_k(k)
    _check_h(h)
    return k / h
