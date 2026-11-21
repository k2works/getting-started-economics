"""章をまたいで使う、入力の検証。

メッセージは、呼び出す側が決める（変数の意味が、章ごとに違うため）。
"""


def validate_positive(value: float, message: str) -> None:
    """value が、正（0 より大きい）でなければ、message のエラーにする。"""
    if value <= 0:
        raise ValueError(message)


def validate_non_negative(value: float, message: str) -> None:
    """value が、負なら、message のエラーにする（0 は、許す）。"""
    if value < 0:
        raise ValueError(message)
