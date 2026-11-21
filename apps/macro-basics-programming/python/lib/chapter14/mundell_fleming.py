"""マンデル・フレミング・モデル（小国開放経済、資本移動が自由）。

IS: (1 − c)Y + b·r = A + n·e、LM: k·Y − h·r = M/P、BP: r = r*（世界の利子率）。
e は為替レート（外国通貨 1 単位あたりの自国通貨。上がると円安）。

- 固定相場: e を固定する。M/P は、為替介入で、内生になる（LM で調整される）
- 変動相場: M/P を固定する。e は、内生になる（IS で調整される）
"""

import math
from dataclasses import dataclass, replace

from lib.chapter01.validation import validate_non_negative, validate_positive
from lib.chapter04.multiplier import validate_mpc
from lib.chapter07.money_market import validate_h, validate_k
from lib.chapter08.is_lm import is_lm_residuals, validate_b


@dataclass(frozen=True)
class SmallOpenEconomy:
    """小国開放経済の係数。intercept は、為替レートに依らない支出 A。"""

    mpc: float
    b: float
    intercept: float
    n: float
    k: float
    h: float
    real_money: float
    world_rate: float
    exchange_rate: float

    def __post_init__(self) -> None:
        validate_mpc(self.mpc)
        validate_b(self.b)
        validate_positive(self.n, "為替レートへの純輸出の感応度 n は、正にする")
        validate_k(self.k)
        validate_h(self.h)
        if not math.isfinite(self.h):
            raise ValueError("貨幣需要の利子率への感応度 h は、有限にする")
        validate_non_negative(self.world_rate, "世界の利子率 r* は、0 以上にする")
        validate_positive(self.exchange_rate, "為替レート e は、正にする")


@dataclass(frozen=True)
class OpenEquilibrium:
    """均衡の所得・利子率・為替レート・実質貨幣供給。"""

    income: float
    interest: float
    exchange_rate: float
    real_money: float


def fixed_rate_equilibrium(economy: SmallOpenEconomy) -> OpenEquilibrium:
    """固定相場の均衡。r = r* を IS に入れて Y を決め、LM から M/P を逆算する。

    入力の real_money は使わない（内生）。逆算した M/P が負になる条件は、
    このモデルの範囲外だが、エラーにせず、そのまま返す。
    """
    e = economy
    income = (e.intercept + e.n * e.exchange_rate - e.b * e.world_rate) / (1 - e.mpc)
    real_money = e.k * income - e.h * e.world_rate
    return OpenEquilibrium(income, e.world_rate, e.exchange_rate, real_money)


def floating_rate_equilibrium(economy: SmallOpenEconomy) -> OpenEquilibrium:
    """変動相場の均衡。LM と r = r* から Y を決め、IS から e を逆算する。

    入力の exchange_rate は使わない（内生）。逆算した e が 0 以下になる条件は、
    このモデルの範囲外だが、エラーにせず、そのまま返す（n が小さいと、政策で
    e が 0 になる）。
    """
    e = economy
    income = (e.real_money + e.h * e.world_rate) / e.k
    exchange_rate = ((1 - e.mpc) * income + e.b * e.world_rate - e.intercept) / e.n
    return OpenEquilibrium(income, e.world_rate, exchange_rate, e.real_money)


def open_economy_residuals(
    economy: SmallOpenEconomy, point: OpenEquilibrium
) -> tuple[float, float, float]:
    """点が、IS・LM・BP を満たさない量。均衡では、3 つとも 0。"""
    e = economy
    # IS・LM の式は第 8 章の関数を再利用する。為替レートに依る支出は、IS の切片に足す
    is_residual, lm_residual = is_lm_residuals(
        point.income,
        point.interest,
        e.mpc,
        e.b,
        e.intercept + e.n * point.exchange_rate,
        e.k,
        e.h,
        point.real_money,
    )
    return is_residual, lm_residual, point.interest - e.world_rate


def fixed_rate_fiscal_effect(
    economy: SmallOpenEconomy, delta_government: float
) -> float:
    """固定相場の財政政策 ΔY = ΔG ÷ (1 − c)。クラウディングアウトがない。"""
    return delta_government / (1 - economy.mpc)


def fixed_rate_monetary_effect(
    economy: SmallOpenEconomy, delta_real_money: float
) -> float:
    """固定相場の金融政策。資本流出で貨幣供給が元に戻るので、ΔY = 0。"""
    return 0.0


def floating_rate_fiscal_effect(
    economy: SmallOpenEconomy, delta_government: float
) -> float:
    """変動相場の財政政策。円高が純輸出を減らして相殺するので、ΔY = 0。"""
    return 0.0


def floating_rate_monetary_effect(
    economy: SmallOpenEconomy, delta_real_money: float
) -> float:
    """変動相場の金融政策 ΔY = Δ(M/P) ÷ k。"""
    return delta_real_money / economy.k


def fixed_rate_devaluation_effect(
    economy: SmallOpenEconomy, delta_exchange_rate: float
) -> float:
    """固定相場で、為替レートの水準を Δe 切り下げたときの ΔY = n·Δe ÷ (1 − c)。"""
    return economy.n * delta_exchange_rate / (1 - economy.mpc)


@dataclass(frozen=True)
class PolicyEffect:
    """1 つの政策の効果（為替制度 × 政策の 1 通り）。"""

    regime: str
    policy: str
    income_change: float
    exchange_rate_change: float
    real_money_change: float


def _effect(
    regime: str,
    policy: str,
    before: OpenEquilibrium,
    after: OpenEquilibrium,
) -> PolicyEffect:
    return PolicyEffect(
        regime,
        policy,
        after.income - before.income,
        after.exchange_rate - before.exchange_rate,
        after.real_money - before.real_money,
    )


def policy_effects_table(
    economy: SmallOpenEconomy, delta_government: float, delta_real_money: float
) -> list[PolicyEffect]:
    """固定・変動 × 財政・金融の 4 通りを、政策の前後の均衡の差で求める。"""
    fiscal = replace(economy, intercept=economy.intercept + delta_government)
    monetary = replace(economy, real_money=economy.real_money + delta_real_money)
    fixed_before = fixed_rate_equilibrium(economy)
    float_before = floating_rate_equilibrium(economy)
    return [
        _effect("固定相場", "財政政策", fixed_before, fixed_rate_equilibrium(fiscal)),
        _effect("固定相場", "金融政策", fixed_before, fixed_rate_equilibrium(monetary)),
        _effect(
            "変動相場", "財政政策", float_before, floating_rate_equilibrium(fiscal)
        ),
        _effect(
            "変動相場", "金融政策", float_before, floating_rate_equilibrium(monetary)
        ),
    ]
