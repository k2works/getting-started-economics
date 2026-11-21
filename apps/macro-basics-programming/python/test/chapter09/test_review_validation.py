"""全体レビュー（2026-11-21）の指摘: 利子率の変化でも、h の検証を通す。"""

import math

import pytest

from lib.chapter09.policy import fiscal_effect, policy_interest_change


def test_hが0なら日本語のエラー() -> None:
    with pytest.raises(ValueError, match="利子率への感応度"):
        policy_interest_change(0.5, 0.0, 10)


def test_hが無限大なら利子率は動かない() -> None:
    assert policy_interest_change(0.5, math.inf, 10, 5) == 0


def test_流動性のわなでは財政政策の効果は単純な乗数() -> None:
    assert fiscal_effect(0.6, 20, 0.5, math.inf, 10) == pytest.approx(25)
