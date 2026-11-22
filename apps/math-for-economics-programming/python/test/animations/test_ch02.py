import numpy as np
import pytest
from matplotlib.animation import FuncAnimation

from lib.animations.ch02 import ANIMATIONS, animate_cournot_n, cournot_frames
from lib.chapter02.monopoly import (
    competitive_outcome,
    cournot_outcome,
    monopoly_outcome,
)


def test_企業の数ごとのフレームはクールノー均衡() -> None:
    data = cournot_frames(100, 1, 20, 10)
    assert [f.firms for f in data] == list(range(1, 11))
    assert data[0].outcome == monopoly_outcome(100, 1, 20)
    assert data[1].outcome == cournot_outcome(2, 100, 1, 20)
    assert data[1].firm_quantity == pytest.approx(80 / 3)


def test_企業が増えると価格は下がり総数量は増えて完全競争に近づく() -> None:
    data = cournot_frames(100, 2, 20, 10)
    prices = [f.outcome.price for f in data]
    quantities = [f.outcome.quantity for f in data]
    assert prices == sorted(prices, reverse=True)
    assert quantities == sorted(quantities)
    assert quantities[-1] < competitive_outcome(100, 2, 20).quantity


def test_1社だけなら独占のフレームが1つ() -> None:
    data = cournot_frames(100, 1, 20, 1)
    assert len(data) == 1
    assert data[0].firm_quantity == 40


def test_アニメーションは均衡の点を企業の数に合わせて動かす() -> None:
    anim = animate_cournot_n(100, 1, 20, 10)
    assert isinstance(anim, FuncAnimation)
    ax = anim._fig.axes[0]  # type: ignore[attr-defined]
    point = next(x for x in ax.lines if x.get_label() == "Cournot equilibrium")
    for i, n in [(0, 1), (5, 2), (29, 10)]:
        anim._func(i)  # type: ignore[attr-defined]
        expected = cournot_outcome(n, 100, 1, 20)
        xs = np.asarray(point.get_xdata(), dtype=float).tolist()
        ys = np.asarray(point.get_ydata(), dtype=float).tolist()
        assert (xs, ys) == ([expected.quantity], [pytest.approx(expected.price)])


def test_登録した名前はGIFのファイル名() -> None:
    assert set(ANIMATIONS) == {"ch02-cournot-n"}
