"""貨幣供給と貨幣乗数。

マネーストック（M1・M3・広義流動性）と、中央銀行が直接動かせるハイパワードマネー
（マネタリーベース）、その間をつなぐ貨幣乗数 M = 貨幣乗数 × H を扱う。
"""

_BUY = "買いオペ"
_SELL = "売りオペ"


def _check_amount(value: float, name: str) -> None:
    if value < 0:
        raise ValueError(f"{name}は、0 以上にする")


def _check_ratios(cash_ratio: float, reserve_ratio: float) -> None:
    if cash_ratio < 0:
        raise ValueError("現金預金比率 C/D は、0 以上にする")
    if not 0 < reserve_ratio <= 1:
        raise ValueError("準備預金比率 R/D は、0 より大きく 1 以下にする")


def m1(currency: float, demand_deposits: float) -> float:
    """M1 = 現金通貨 + 預金通貨（全預金取扱機関）。"""
    _check_amount(currency, "現金通貨")
    _check_amount(demand_deposits, "預金通貨")
    return currency + demand_deposits


def m3(m1_value: float, quasi_money: float, cd: float) -> float:
    """M3 = M1 + 準通貨 + CD（譲渡性預金）。代表的なマネーストックの指標。"""
    _check_amount(m1_value, "M1")
    _check_amount(quasi_money, "準通貨")
    _check_amount(cd, "CD")
    return m1_value + quasi_money + cd


def broad_liquidity(m3_value: float, investment_trusts: float, bonds: float) -> float:
    """広義流動性 = M3 + 投資信託・国債など。"""
    _check_amount(m3_value, "M3")
    _check_amount(investment_trusts, "投資信託")
    _check_amount(bonds, "国債など")
    return m3_value + investment_trusts + bonds


def monetary_base(currency: float, reserves: float) -> float:
    """ハイパワードマネー（マネタリーベース）H = 現金通貨 + 準備預金。"""
    _check_amount(currency, "現金通貨")
    _check_amount(reserves, "準備預金")
    return currency + reserves


def money_multiplier(cash_ratio: float, reserve_ratio: float) -> float:
    """貨幣乗数 = (C/D + 1) ÷ (C/D + R/D)。C/D・R/D が上がると下がる。"""
    _check_ratios(cash_ratio, reserve_ratio)
    return (cash_ratio + 1) / (cash_ratio + reserve_ratio)


def money_stock(cash_ratio: float, reserve_ratio: float, base: float) -> float:
    """マネーストック M = 貨幣乗数 × ハイパワードマネー H。"""
    _check_amount(base, "ハイパワードマネー")
    return money_multiplier(cash_ratio, reserve_ratio) * base


def open_market_operation(base: float, amount: float, operation: str) -> float:
    """公開市場操作後のハイパワードマネー。買いオペで増え、売りオペで減る。"""
    _check_amount(base, "ハイパワードマネー")
    _check_amount(amount, "操作の額")
    if operation == _BUY:
        return base + amount
    if operation == _SELL:
        if amount > base:
            raise ValueError("売りオペの額が、ハイパワードマネーを超えている")
        return base - amount
    raise ValueError(f"操作は「{_BUY}」か「{_SELL}」にする: {operation}")


def reserve_requirement_change(
    base: float, cash_ratio: float, new_reserve_ratio: float
) -> float:
    """法定準備率を new_reserve_ratio にしたあとのマネーストック。"""
    return money_stock(cash_ratio, new_reserve_ratio, base)


def credit_creation_path(
    base: float, cash_ratio: float, reserve_ratio: float, rounds: int
) -> list[float]:
    """信用創造を、ラウンドごとに追い、各ラウンド後のマネーストックを返す。

    各ラウンドで、手元の資金 x を、預金 d と現金 C/D × d に分ける（x = (1 + C/D) d）。
    銀行は、預金 d の R/D を準備に置き、残りを貸し出す。貸出は、次のラウンドの
    手元の資金になる。
    """
    _check_amount(base, "ハイパワードマネー")
    _check_ratios(cash_ratio, reserve_ratio)
    if rounds < 1:
        raise ValueError("ラウンド数は、1 以上にする")
    deposit = base / (1 + cash_ratio)
    total = 0.0
    path = []
    for _ in range(rounds):
        total += deposit
        path.append((1 + cash_ratio) * total)
        deposit *= (1 - reserve_ratio) / (1 + cash_ratio)
    return path
