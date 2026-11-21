"""フィリップス曲線。

短期: π = π^e − β·(u − u_n)。失業率 u が、自然失業率 u_n より低いほど、インフレ率 π が
期待インフレ率 π^e より高い（右下がり）。長期には、期待が現実に追いつき、π = π^e で、
失業率は u_n に戻る（垂直）。
"""

from lib.chapter01.validation import validate_non_negative, validate_positive


def _check_beta(beta: float) -> None:
    validate_positive(beta, "失業率への感応度 β は、正にする")


def short_run_inflation(
    unemployment: float,
    natural_rate: float,
    expected_inflation: float,
    beta: float,
) -> float:
    """短期のフィリップス曲線 π = π^e − β·(u − u_n)。"""
    _check_beta(beta)
    return expected_inflation - beta * (unemployment - natural_rate)


def implied_natural_rate(
    unemployment: float,
    inflation: float,
    expected_inflation: float,
    beta: float,
) -> float:
    """観測 (u, π) から逆算した自然失業率 u_n = u + (π − π^e) ÷ β。"""
    _check_beta(beta)
    return unemployment + (inflation - expected_inflation) / beta


def accelerating_inflation_path(
    unemployment: float,
    natural_rate: float,
    initial_inflation: float,
    beta: float,
    periods: int,
) -> list[float]:
    """失業率を u に保ち続けたときの、インフレ率の経路。

    期待インフレ率は、前の期のインフレ率に等しい（期待が、現実に追いつく）。
    u が u_n より低いと、毎期、インフレ率が上がり続ける（長期のトレードオフは無い）。
    """
    _check_beta(beta)
    validate_non_negative(periods, "期間は、0 以上にする")
    path = [initial_inflation]
    for _ in range(periods):
        path.append(
            short_run_inflation(unemployment, natural_rate, path[-1], beta),
        )
    return path
