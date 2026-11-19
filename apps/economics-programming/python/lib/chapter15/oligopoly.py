"""寡占（クールノー競争）。逆需要曲線 P = a/b - Q/b、限界費用は各社で一定とする。"""


def best_response(
    opponent_quantity: float,
    demand_intercept: float,
    demand_slope: float,
    marginal_cost: float,
) -> float:
    """相手の生産量が与えられたときの、自社の利潤を最大にする生産量。

    q = (A - MC - B × 相手の生産量) ÷ 2B（A = a/b、B = 1/b）。負にはならない。
    """
    highest_price = demand_intercept / demand_slope
    price_slope = 1 / demand_slope
    quantity = (highest_price - marginal_cost - price_slope * opponent_quantity) / (
        2 * price_slope
    )
    return max(quantity, 0)


def cournot_by_iteration(
    demand_intercept: float,
    demand_slope: float,
    marginal_cost: float,
    initial: tuple[float, float] = (0.0, 0.0),
    tolerance: float = 1e-9,
    max_iterations: int = 1000,
) -> tuple[float, float]:
    """2 社が交互に最適反応をとり続けて、クールノー・ナッシュ均衡を求める。"""
    q1, q2 = initial
    for _ in range(max_iterations):
        new_q1 = best_response(q2, demand_intercept, demand_slope, marginal_cost)
        new_q2 = best_response(new_q1, demand_intercept, demand_slope, marginal_cost)
        if abs(new_q1 - q1) < tolerance and abs(new_q2 - q2) < tolerance:
            return new_q1, new_q2
        q1, q2 = new_q1, new_q2
    raise RuntimeError("均衡に収束しなかった")


def cournot_symmetric(
    firms: int,
    demand_intercept: float,
    demand_slope: float,
    marginal_cost: float,
) -> tuple[float, float, float]:
    """同じ費用の企業が firms 社あるときの、各社の生産量・価格・各社の利潤。

    各社の生産量 q = (A - MC) ÷ (B × (n + 1))。
    1 社なら独占、n が大きいと完全競争に近づく。
    """
    if firms < 1:
        raise ValueError("企業の数は 1 以上でなければならない")
    highest_price = demand_intercept / demand_slope
    price_slope = 1 / demand_slope
    quantity = (highest_price - marginal_cost) / (price_slope * (firms + 1))
    price = highest_price - price_slope * firms * quantity
    return quantity, price, (price - marginal_cost) * quantity


def duopoly_profits(
    quantity1: float,
    quantity2: float,
    demand_intercept: float,
    demand_slope: float,
    marginal_cost: float,
) -> tuple[float, float]:
    """2 社の生産量が決まったときの、各社の利潤。"""
    price = (demand_intercept - quantity1 - quantity2) / demand_slope
    return (price - marginal_cost) * quantity1, (price - marginal_cost) * quantity2
