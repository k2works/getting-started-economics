"""ディマンドプルとコストプッシュ。第 10 章の AD-AS で、物価と所得の変化を比べる。"""

from functools import partial

from lib.chapter01.validation import validate_positive
from lib.chapter10.ad_as import (
    AdEconomy,
    expand_demand,
    keynesian_supply,
    shift_supply,
    solve_ad_as,
)


def demand_pull_effect(
    economy: AdEconomy,
    full_employment_income: float,
    base_income: float,
    slope: float,
    delta_government: float,
) -> tuple[float, float]:
    """ディマンドプル（AD の右シフト）による、物価と所得の変化 (ΔP, ΔY)。"""
    validate_positive(delta_government, "需要の増加は、正にする")
    supply = partial(
        keynesian_supply,
        full_employment_income=full_employment_income,
        base_income=base_income,
        slope=slope,
    )
    price0, income0 = solve_ad_as(economy, supply)
    price1, income1 = solve_ad_as(
        expand_demand(economy, delta_government=delta_government), supply
    )
    return price1 - price0, income1 - income0


def cost_push_effect(
    economy: AdEconomy,
    full_employment_income: float,
    base_income: float,
    slope: float,
    supply_loss: float,
) -> tuple[float, float]:
    """コストプッシュ（AS の左シフト）による、物価と所得の変化 (ΔP, ΔY)。"""
    validate_positive(supply_loss, "供給の減少は、正にする")
    before = partial(
        keynesian_supply,
        full_employment_income=full_employment_income,
        base_income=base_income,
        slope=slope,
    )
    full, base = shift_supply(full_employment_income, base_income, -supply_loss)
    after = partial(
        keynesian_supply, full_employment_income=full, base_income=base, slope=slope
    )
    price0, income0 = solve_ad_as(economy, before)
    price1, income1 = solve_ad_as(economy, after)
    return price1 - price0, income1 - income0
