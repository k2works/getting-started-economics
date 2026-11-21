"""消費の理論: 絶対所得・ライフサイクル・恒常所得・相対所得・流動資産仮説。"""

from collections.abc import Sequence

from lib.chapter01.validation import validate_positive


def consumption_from_absolute_income(
    income: float, mpc: float, autonomous: float = 0
) -> float:
    """絶対所得仮説 C = cY + C0。長期は C0 = 0 で、C = cY。"""
    return mpc * income + autonomous


def average_propensity(income: float, mpc: float, autonomous: float = 0) -> float:
    """平均消費性向 C ÷ Y = c + C0 ÷ Y。C0 > 0 なら、所得が増えると下がる。"""
    if income == 0:
        raise ValueError("所得が 0 のとき、平均消費性向は計算できない")
    return consumption_from_absolute_income(income, mpc, autonomous) / income


def _validate_years(working_years: float, lifetime_years: float) -> None:
    validate_positive(lifetime_years, "生涯の年数は、正にする")
    if working_years < 0 or working_years > lifetime_years:
        raise ValueError("働く年数は、0 以上、生涯の年数以下にする")


def lifecycle_consumption(
    annual_income: float, working_years: float, lifetime_years: float
) -> float:
    """ライフサイクル仮説。生涯所得を生涯の年数で割った、毎年の消費（平準化）。"""
    _validate_years(working_years, lifetime_years)
    return annual_income * working_years / lifetime_years


def lifecycle_saving(
    annual_income: float, working_years: float, lifetime_years: float
) -> float:
    """働いている間の、年間の貯蓄 = 年収 − 毎年の消費。"""
    return annual_income - lifecycle_consumption(
        annual_income, working_years, lifetime_years
    )


def permanent_income(incomes: Sequence[float], adjust: float) -> list[float]:
    """恒常所得 Yp(t) = λ·Y(t) + (1 − λ)·Yp(t−1)。過去の所得の加重平均。

    最初の恒常所得は、最初の所得とする。λ は調整係数で、1 なら今期の所得に等しい。
    """
    if not incomes:
        raise ValueError("所得の系列が空")
    if adjust <= 0 or adjust > 1:
        raise ValueError("調整係数は、0 より大きく 1 以下にする")
    path = [float(incomes[0])]
    for income in incomes[1:]:
        path.append(adjust * income + (1 - adjust) * path[-1])
    return path


def permanent_consumption(
    incomes: Sequence[float], propensity: float, adjust: float
) -> list[float]:
    """恒常所得仮説の消費 C = k·Yp。今期の所得ではなく、恒常所得で決まる。"""
    return [propensity * yp for yp in permanent_income(incomes, adjust)]


def ratchet_consumption(incomes: Sequence[float], mpc: float) -> list[float]:
    """相対所得仮説（ラチェット効果）。消費は、過去の最高所得 × c で決まる。"""
    peak = float("-inf")
    path = []
    for income in incomes:
        peak = max(peak, income)
        path.append(mpc * peak)
    return path


def consumption_from_liquid_assets(
    income: float, assets: float, mpc_income: float, mpc_assets: float
) -> float:
    """流動資産仮説 C = c1·Y + c2·A。預貯金などの流動資産にも依存する。"""
    return mpc_income * income + mpc_assets * assets
