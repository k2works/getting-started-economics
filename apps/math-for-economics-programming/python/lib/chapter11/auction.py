"""オークション: 評価額が独立に [0, 1] の一様分布に従う n 人の、入札と期待収入。"""

import functools
import math
from collections.abc import Sequence
from fractions import Fraction
from typing import Literal

import numpy as np

from lib.chapter11.distribution import continuous_expectation, continuous_expected_value


def _require_bidders(bidders: int) -> None:
    if bidders < 2:
        raise ValueError("オークションには、2 人以上の参加者が必要です")


def _require_rank(bidders: int, rank: int) -> None:
    if not 1 <= rank <= bidders:
        raise ValueError("順位は、1 から人数までです")


def order_statistic_density(value: float, bidders: int, rank: int) -> float:
    """n 人で rank 番目に高い評価額の密度 n·C(n−1, k−1)·v^(n−k)·(1 − v)^(k−1)。"""
    _require_rank(bidders, rank)
    ways = bidders * math.comb(bidders - 1, rank - 1)
    return float(ways * value ** (bidders - rank) * (1 - value) ** (rank - 1))


def expected_auction_revenue_formula(bidders: int) -> Fraction:
    """売り手の期待収入の公式 (n − 1) ÷ (n + 1)（2 番目に高い評価額の期待値）。"""
    _require_bidders(bidders)
    return Fraction(bidders - 1, bidders + 1)


def second_price_payoff(value: float, bid: float, rival_bids: Sequence[float]) -> float:
    """セカンドプライス: 最高の入札なら勝ち、相手の最高の入札額を払う。利得を返す。"""
    if not rival_bids:
        raise ValueError("競争相手が、1 人以上必要です")
    highest_rival = max(rival_bids)
    return value - highest_rival if bid > highest_rival else 0


def second_price_expected_revenue(bidders: int, pieces: int = 1000) -> float:
    """セカンドプライスの期待収入 = 2 番目に高い評価額の期待値 ∫ v·f₍₂₎(v) dv。"""
    _require_bidders(bidders)
    second = functools.partial(order_statistic_density, bidders=bidders, rank=2)
    return continuous_expected_value(second, 0, 1, pieces)


def first_price_equilibrium_bid(value: float, bidders: int) -> float:
    """ファーストプライスの均衡入札 b(v) = (n − 1) ÷ n × v（評価額を割り引く）。"""
    _require_bidders(bidders)
    return (bidders - 1) / bidders * value


def first_price_expected_revenue(bidders: int, pieces: int = 1000) -> float:
    """ファーストプライスの期待収入 = 最高の評価額の人の入札 ∫ b(v)·f₍₁₎(v) dv。"""
    _require_bidders(bidders)
    bid = functools.partial(first_price_equilibrium_bid, bidders=bidders)
    highest = functools.partial(order_statistic_density, bidders=bidders, rank=1)
    return continuous_expectation(bid, highest, 0, 1, pieces)


def simulate_auction_revenues(
    bidders: int, rounds: int, seed: int, rule: Literal["first", "second"]
) -> list[float]:
    """評価額を乱数で引き、rounds 回のオークションの、各回の売り手の収入を返す。"""
    _require_bidders(bidders)
    if rounds < 1:
        raise ValueError("回数は、1 以上でなければなりません")
    rng = np.random.default_rng(seed)
    values = np.sort(rng.random((rounds, bidders)), axis=1)
    if rule == "second":
        return [float(v) for v in values[:, -2]]
    return [first_price_equilibrium_bid(float(v), bidders) for v in values[:, -1]]


def expected_order_statistic(bidders: int, rank: int) -> Fraction:
    """n 個の一様乱数の、rank 番目に大きい値の期待値 (n − k + 1) ÷ (n + 1)。"""
    _require_rank(bidders, rank)
    return Fraction(bidders - rank + 1, bidders + 1)


def first_price_expected_payoff(value: float, bid: float, bidders: int) -> float:
    """相手が全員 b(v) で入札するとき、bid で入札する人の期待利得 (v − b)·P(勝つ)。"""
    rival_below = min(bid * bidders / (bidders - 1), 1)
    return (value - bid) * rival_below ** (bidders - 1)
