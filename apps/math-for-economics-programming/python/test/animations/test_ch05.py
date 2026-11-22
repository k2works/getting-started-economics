import pytest
from matplotlib.animation import FuncAnimation

from lib.animations.ch05 import ANIMATIONS, animate_secant_tangent, secant_frames
from lib.chapter05.cost import marginal_cost
from lib.chapter05.derivative import Polynomial, numerical_derivative

CUBIC = Polynomial((20, 15, -6, 1))  # C(q) = q³ − 6q² + 15q + 20。q = 4 で MC = 15


def test_刻み幅は対数で等間隔に縮む() -> None:
    data = secant_frames(CUBIC, 4, 2, 0.001, 4)
    steps = [f.step for f in data]
    assert steps[0] == pytest.approx(2)
    assert steps[-1] == pytest.approx(0.001)
    ratios = [a / b for a, b in zip(steps, steps[1:], strict=False)]
    assert ratios == pytest.approx([ratios[0]] * 3)


def test_割線の傾きは中心差分で接線の傾きに近づく() -> None:
    data = secant_frames(CUBIC, 4, 2, 0.001, 20)
    for frame in data:
        assert frame.slope == pytest.approx(numerical_derivative(CUBIC, 4, frame.step))
        # 3 次の費用の中心差分は MC + h²（C''' = 6 なので h²·6 ÷ 6）
        assert frame.slope == pytest.approx(15 + frame.step**2)
    errors = [abs(f.slope - marginal_cost(CUBIC, 4)) for f in data]
    assert errors == sorted(errors, reverse=True)
    assert errors[0] == pytest.approx(4)
    assert errors[-1] < 1e-5


def test_割線は左右の点を通る() -> None:
    first = secant_frames(CUBIC, 4, 2, 0.001, 3)[0]
    assert first.left == (2, CUBIC(2))
    assert first.right == (6, CUBIC(6))


def test_刻み幅が正でなければフレームを作らない() -> None:
    for start, end in [(0, 0.001), (2, 0), (2, -1)]:
        with pytest.raises(ValueError):
            secant_frames(CUBIC, 4, start, end, 5)


def test_アニメーションは全フレームを更新できる() -> None:
    animation = ANIMATIONS["ch05-secant-tangent"]()
    assert isinstance(animation, FuncAnimation)
    small = animate_secant_tangent(frames=3)
    for i in range(3):
        small._func(i)  # type: ignore[attr-defined]
    texts = [t.get_text() for t in small._fig.axes[0].texts]  # type: ignore[attr-defined]
    assert any("h = 0.001" in t for t in texts)


def test_描いた割線は左右の点を通る() -> None:
    animation = animate_secant_tangent(frames=3)
    animation._func(0)  # type: ignore[attr-defined]
    ax = animation._fig.axes[0]  # type: ignore[attr-defined]
    line = next(x for x in ax.lines if x.get_label() == "Secant")
    (x0, x1), (y0, y1) = line.get_xdata(), line.get_ydata()
    slope = (y1 - y0) / (x1 - x0)
    first = secant_frames(CUBIC, 4, 2, 0.001, 3)[0]
    for x, y in [first.left, first.right]:
        assert y0 + slope * (x - x0) == pytest.approx(y)
