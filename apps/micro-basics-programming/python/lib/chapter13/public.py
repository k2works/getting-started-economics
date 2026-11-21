"""公共財（非競合性・非排除性、フリーライダー）。

各人の限界便益 MB_i = a_i − b_i·q。公共財は、全員が同時に消費できるので、
社会全体の限界便益は、縦に足す（Σ MB_i）。最適な供給量は Σ MB_i = MC の点。
フリーライダーがいると、最も欲しい人 1 人の量しか、自発的には供給されない。
"""

from dataclasses import dataclass

from lib.chapter01.validation import validate_non_negative, validate_positive


@dataclass(frozen=True)
class PublicGood:
    """各人の限界便益の切片・傾きと、限界費用。"""

    benefit_intercepts: tuple[float, ...]
    benefit_slopes: tuple[float, ...]
    marginal_cost: float

    def __post_init__(self) -> None:
        if not self.benefit_intercepts:
            raise ValueError("人が、1 人もいません")
        if len(self.benefit_intercepts) != len(self.benefit_slopes):
            raise ValueError("切片と傾きは、同じ人数にする")
        for slope in self.benefit_slopes:
            validate_positive(slope, "限界便益の傾きは、正にする")
        validate_non_negative(self.marginal_cost, "限界費用は、0 以上にする")


def public_good_optimal_quantity(good: PublicGood) -> float:
    """最適な供給量。正の限界便益だけを縦に足した Σ max(a_i − b_i·q, 0) = MC の点。

    限界便益が 0 になる数量（a_i ÷ b_i）を超えた人は、足さない。足す人を絞りながら、
    q = (Σa − MC) ÷ Σb を、足す人が変わらなくなるまで、求め直す。
    """
    active = list(range(len(good.benefit_intercepts)))
    while True:
        quantity = (
            sum(good.benefit_intercepts[i] for i in active) - good.marginal_cost
        ) / sum(good.benefit_slopes[i] for i in active)
        still = [
            i
            for i in active
            if good.benefit_intercepts[i] / good.benefit_slopes[i] >= quantity
        ]
        if still == active:
            return max(quantity, 0.0)
        active = still


def individual_quantity(good: PublicGood, person: int) -> float:
    """その人 1 人が、自分の便益だけで、供給するなら、MB = MC の点。負なら 0。"""
    if not 0 <= person < len(good.benefit_intercepts):
        raise ValueError("人の番号が、範囲外です")
    quantity = (
        good.benefit_intercepts[person] - good.marginal_cost
    ) / good.benefit_slopes[person]
    return max(quantity, 0.0)


def voluntary_quantity(good: PublicGood) -> float:
    """自発的な供給量。最も欲しい人 1 人の量（他の人は、ただ乗りする）。"""
    return max(
        individual_quantity(good, person)
        for person in range(len(good.benefit_intercepts))
    )


def under_provision(good: PublicGood) -> float:
    """過少供給の大きさ = 最適な量 − 自発的な量。"""
    return public_good_optimal_quantity(good) - voluntary_quantity(good)


def classify_good(rival: bool, excludable: bool) -> str:
    """競合性・排除性による、財の 4 分類。"""
    if rival:
        return "private" if excludable else "common"
    return "club" if excludable else "public"
