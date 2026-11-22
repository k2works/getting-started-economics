"""情報の非対称性（逆選択・シグナル・モラルハザード）。

小さな離散的な例で、手計算できる形にする。
- 逆選択: 買い手は、質が分からない。平均の質にしか払わないので、良い品が市場から消える
- シグナル: 高い能力の人だけが、割に合う、教育という費用を払って、能力を示す
- モラルハザード: 依頼人は、努力を観察できない。成果報酬で、努力させる
"""

from collections.abc import Sequence

from lib.chapter01.validation import validate_non_negative, validate_positive

_TOLERANCE = 1e-9  # 境界ちょうどの判定を、浮動小数点の誤差に左右させない


def _check_share(share: float) -> None:
    if not 0 <= share <= 1:
        raise ValueError("良い品の割合は、0 以上 1 以下にする")


def expected_value_of_unknown_quality(
    good_share: float, value_good: float, value_bad: float
) -> float:
    """質が分からない買い手の、支払意思額 = 良い品の割合で重みづけた、価値の期待値。"""
    _check_share(good_share)
    return good_share * value_good + (1 - good_share) * value_bad


def good_quality_sells(
    good_share: float,
    value_good: float,
    value_bad: float,
    seller_reservation: float,
) -> bool:
    """良い品が、市場に出るか。期待値が、良い品の売り手の最低価格以上のとき。"""
    expected = expected_value_of_unknown_quality(good_share, value_good, value_bad)
    return expected >= seller_reservation - _TOLERANCE


def unraveling(qualities: Sequence[float], premium: float) -> list[float]:
    """市場が崩れる過程。売り手の最低価格は質、買い手の支払意思額は平均 × premium。

    価格が最低価格に届かない質は、市場から出る。変わらなくなるまで、繰り返す。
    """
    if not qualities:
        raise ValueError("質が、1 つもありません")
    validate_positive(premium, "買い手の評価の倍率は、正にする")
    selling = sorted(qualities)
    while selling:
        price = premium * sum(selling) / len(selling)
        remaining = [quality for quality in selling if quality <= price]
        if remaining == selling:
            break
        selling = remaining
    return selling


def separating_education_range(
    wage_high: float, wage_low: float, cost_high: float, cost_low: float
) -> tuple[float, float]:
    """高い能力の人だけが、教育を選ぶ、教育年数 e の範囲。

    低い能力の人は、まねしない: w_low ≥ w_high − c_low·e
        → e ≥ (w_high − w_low) ÷ c_low
    高い能力の人は、選ぶ: w_high − c_high·e ≥ w_low
        → e ≤ (w_high − w_low) ÷ c_high
    """
    if wage_high <= wage_low:
        raise ValueError("賃金は、高い能力の方を高くする")
    validate_positive(cost_high, "教育の費用は、正にする")
    if cost_low <= cost_high:
        raise ValueError("教育の費用は、低い能力の人の方を大きくする")
    premium = wage_high - wage_low
    return premium / cost_low, premium / cost_high


def signal_separates(
    education: float,
    wage_high: float,
    wage_low: float,
    cost_high: float,
    cost_low: float,
) -> bool:
    """教育年数 e で、高い能力の人だけが、教育を選ぶか。"""
    low, high = separating_education_range(wage_high, wage_low, cost_high, cost_low)
    return low - _TOLERANCE <= education <= high + _TOLERANCE


def _check_probabilities(p_high: float, p_low: float) -> None:
    if not 0 <= p_low < p_high <= 1:
        raise ValueError("成功確率は、0 ≤ 努力しない < 努力する ≤ 1 にする")


def minimum_bonus(p_high: float, p_low: float, effort_cost: float) -> float:
    """努力させる、最低の成果報酬 b = 努力の費用 ÷ (p_high − p_low)。"""
    _check_probabilities(p_high, p_low)
    validate_non_negative(effort_cost, "努力の費用は、0 以上にする")
    return effort_cost / (p_high - p_low)


def agent_works(bonus: float, p_high: float, p_low: float, effort_cost: float) -> bool:
    """努力すると、期待報酬 p_high·b − 費用 が、努力しない p_low·b 以上になるか。"""
    _check_probabilities(p_high, p_low)
    return bonus >= minimum_bonus(p_high, p_low, effort_cost) - _TOLERANCE


def principal_profit_with_bonus(
    value: float, p_high: float, p_low: float, effort_cost: float
) -> float:
    """最低の成果報酬で、努力させたときの、依頼人の期待利潤 p_high·(V − b)。"""
    bonus = minimum_bonus(p_high, p_low, effort_cost)
    return p_high * (value - bonus)


def worth_paying_bonus(
    value: float, p_high: float, p_low: float, effort_cost: float
) -> bool:
    """努力させる利潤が、努力しない場合の期待利潤 p_low·V を、上回るか。"""
    profit = principal_profit_with_bonus(value, p_high, p_low, effort_cost)
    return profit > p_low * value + _TOLERANCE
