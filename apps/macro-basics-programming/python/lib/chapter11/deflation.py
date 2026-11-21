"""デフレの影響: 実質利子率と、借金の実質的な負担。"""

from lib.chapter01.validation import validate_non_negative


def real_interest_rate(nominal: float, inflation: float) -> float:
    """フィッシャー方程式 実質利子率 = 名目利子率 − インフレ率。

    デフレ（インフレ率が負）では、実質利子率は、名目利子率より高い。
    """
    return nominal - inflation


def debt_burden(nominal_debt: float, inflation: float, years: int = 1) -> float:
    """名目の借金の、実質的な負担（もとの物価で測った値）。

    名目の借金は、物価が変わっても、額面が変わらない。物価が (1 + インフレ率)^年数 倍に
    なると、実質的な負担は、その分の 1 になる。デフレでは、負担が増える（債務者から
    債権者への所得の再分配）。
    """
    if inflation <= -1:
        raise ValueError("インフレ率は、−1 より大きくする（物価が 0 以下になる）")
    validate_non_negative(years, "年数は、0 以上にする")
    return nominal_debt / (1 + inflation) ** years
