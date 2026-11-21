"""章をまたいで使う、入力の検証のテスト。"""

import pytest

from lib.chapter01.validation import validate_non_negative, validate_positive


def test_正の値を通す() -> None:
    validate_positive(0.5, "x は、正にする")
    validate_positive(1, "x は、正にする")


def test_0と負は正でないのでエラー() -> None:
    for value in (0, -0.1, -5):
        with pytest.raises(ValueError, match="x は、正にする"):
            validate_positive(value, "x は、正にする")


def test_0以上を通す() -> None:
    validate_non_negative(0, "x は、0 以上にする")
    validate_non_negative(0.5, "x は、0 以上にする")


def test_負はエラー() -> None:
    with pytest.raises(ValueError, match="x は、0 以上にする"):
        validate_non_negative(-1e-9, "x は、0 以上にする")
