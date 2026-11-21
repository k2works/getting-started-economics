"""45 度線分析: 消費関数・貯蓄関数・総需要・均衡国民所得・乗数。"""


def validate_mpc(mpc: float) -> None:
    """限界消費性向は 0 以上 1 未満。1 は、乗数の分母が 0 になる。"""
    if mpc < 0:
        raise ValueError("限界消費性向は、0 以上にする")
    if mpc >= 1:
        raise ValueError("限界消費性向は、1 未満にする（1 では乗数の分母が 0）")


def consumption(
    income: float, mpc: float, autonomous_consumption: float, tax: float = 0
) -> float:
    """消費関数 C = c(Y − T) + C0。課税で、c × T だけ下へ動く。"""
    return mpc * (income - tax) + autonomous_consumption


def saving(
    income: float, mpc: float, autonomous_consumption: float, tax: float = 0
) -> float:
    """貯蓄関数 S = (Y − T) − C = (1 − c)(Y − T) − C0。"""
    disposable = income - tax
    return disposable - consumption(income, mpc, autonomous_consumption, tax)


def aggregate_demand(
    income: float,
    mpc: float,
    autonomous_consumption: float,
    investment: float,
    government: float,
    net_exports: float,
    tax: float = 0,
) -> float:
    """総需要 D = C + I + G + X。"""
    c = consumption(income, mpc, autonomous_consumption, tax)
    return c + investment + government + net_exports


def equilibrium_income(
    mpc: float,
    autonomous_consumption: float,
    investment: float,
    government: float,
    net_exports: float,
    tax: float = 0,
) -> float:
    """均衡国民所得 Y = A ÷ (1 − c)。A = C0 − cT + I + G + X（独立支出）。"""
    validate_mpc(mpc)
    autonomous = (
        autonomous_consumption - mpc * tax + investment + government + net_exports
    )
    return autonomous / (1 - mpc)


def spending_multiplier(mpc: float) -> float:
    """政府支出・投資の乗数 1 ÷ (1 − c)。"""
    validate_mpc(mpc)
    return 1 / (1 - mpc)


def tax_multiplier(mpc: float) -> float:
    """租税乗数 −c ÷ (1 − c)。増税（T の増加）は所得を減らすので、符号は負。"""
    validate_mpc(mpc)
    return -mpc / (1 - mpc)


def balanced_budget_multiplier(mpc: float) -> float:
    """均衡予算乗数 = 政府支出乗数 + 租税乗数（常に 1）。"""
    return spending_multiplier(mpc) + tax_multiplier(mpc)


def income_change(
    mpc: float, delta_government: float = 0, delta_tax: float = 0
) -> float:
    """政府支出の変化と租税の変化による、均衡所得の変化。"""
    government = spending_multiplier(mpc) * delta_government
    return government + tax_multiplier(mpc) * delta_tax
