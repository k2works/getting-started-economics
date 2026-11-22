"""第 3 章のアニメーション（利子率を動かす）のテスト。"""

import pytest
from matplotlib.animation import FuncAnimation

from lib.animations.ch03 import ANIMATIONS, animate_compound_rate, compound_rate_frames
from lib.chapter03.interest import compound_amount, rule_of_72_years, years_to_multiply


def test_端のフレームは最小と最大の利子率() -> None:
    data = compound_rate_frames(100, 30, 0.01, 0.12, 12)
    assert [round(f.rate, 10) for f in data] == [
        round(0.01 * k, 10) for k in range(1, 13)
    ]
    assert data[0].years == list(range(31))


def test_フレームの値は章の関数と一致する() -> None:
    for frame in compound_rate_frames(100, 30, 0.01, 0.12, 5):
        assert frame.compound == pytest.approx(
            [compound_amount(100, frame.rate, t) for t in frame.years]
        )
        assert frame.simple == pytest.approx(
            [100 * (1 + frame.rate * t) for t in frame.years]
        )
        assert frame.doubling_years == pytest.approx(years_to_multiply(frame.rate, 2))
        assert frame.rule_of_72 == pytest.approx(rule_of_72_years(frame.rate))


def test_利子率が上がると倍になる年数は短くなり最後の額は増える() -> None:
    data = compound_rate_frames(100, 30, 0.01, 0.12, 12)
    doubling = [f.doubling_years for f in data]
    last = [f.compound[-1] for f in data]
    assert all(a > b for a, b in zip(doubling, doubling[1:], strict=False))
    assert all(a < b for a, b in zip(last, last[1:], strict=False))


def test_利子率が正でなければフレームを作らない() -> None:
    with pytest.raises(ValueError):
        compound_rate_frames(100, 30, 0, 0.12, 12)


def test_アニメーションは全フレームを描ける() -> None:
    anim = animate_compound_rate(frames=4)
    assert isinstance(anim, FuncAnimation)
    for i in range(4):
        anim._func(i)  # type: ignore[attr-defined]


def test_登録名は章の静止画と紛らわしくない() -> None:
    assert list(ANIMATIONS) == ["ch03-compound-rate"]
