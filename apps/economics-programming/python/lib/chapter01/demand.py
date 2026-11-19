"""需要曲線 Q = a - bP。"""


def quantity_demanded(price: float, intercept: float, slope: float) -> float:
    """価格 P のときの需要量 Q = a - bP を返す。需要量は負にならない。"""
    if price < 0:
        raise ValueError("価格は 0 以上でなければならない")
    return max(intercept - slope * price, 0)


def check_slope(slope: float, name: str = "傾き") -> None:
    """曲線の傾きが正であることを確かめる。0 以下では、ゼロ除算や右上がりになる。"""
    if slope <= 0:
        raise ValueError(f"{name}は正でなければならない")


def choke_price(intercept: float, slope: float) -> float:
    """需要量がちょうど 0 になる価格 P = a / b を返す。"""
    check_slope(slope, "需要曲線の傾き")
    return intercept / slope
