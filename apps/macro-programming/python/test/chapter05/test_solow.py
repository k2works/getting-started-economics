"""第 5 章: ソロー・モデルのテスト。

k(t+1) = s·A·k(t)^α + (1−δ)·k(t)。α = 0.5、s = 0.2、δ = 0.05、A = 1 なら、
定常状態は k* = (s·A ÷ δ)^(1 ÷ (1−α)) = 4² = 16、y* = √16 = 4。
"""

import numpy as np
import pytest

from lib.chapter05.solow import (
    approximation_error,
    convergence_speed,
    half_life,
    log_linear_path,
    solow_path,
    solow_step,
    steady_state_capital,
    steady_state_output,
)

MODEL = {"saving_rate": 0.2, "depreciation": 0.05, "alpha": 0.5}


def test_定常状態の資本は16() -> None:
    assert steady_state_capital(**MODEL) == pytest.approx(16)


def test_定常状態の所得は4() -> None:
    assert steady_state_output(**MODEL) == pytest.approx(4)


def test_定常状態では貯蓄が減耗と等しい() -> None:
    k = steady_state_capital(**MODEL)
    assert 0.2 * k**0.5 == pytest.approx(0.05 * k)


def test_資本4の次の期は4_2() -> None:
    # 0.2·√4 + 0.95·4 = 0.4 + 3.8
    assert solow_step(4, **MODEL) == pytest.approx(4.2)


def test_定常状態から出発すれば動かない() -> None:
    assert solow_step(16, **MODEL) == pytest.approx(16)


def test_資本が少ない国は定常状態に向けて増え続ける() -> None:
    path = solow_path(4, **MODEL, periods=300)
    assert all(a < b for a, b in zip(path, path[1:], strict=False))
    assert max(path) < 16
    assert path[-1] == pytest.approx(16, abs=0.1)


def test_資本が多い国は定常状態に向けて減り続ける() -> None:
    path = solow_path(25, **MODEL, periods=200)
    assert all(a > b for a, b in zip(path, path[1:], strict=False))
    assert min(path) > 16
    assert path[-1] == pytest.approx(16, abs=0.1)


def test_貯蓄率が2倍なら定常状態の資本は4倍() -> None:
    # (s ÷ δ)^(1 ÷ (1−α)) = (0.4 ÷ 0.05)² = 64
    k = steady_state_capital(saving_rate=0.4, depreciation=0.05, alpha=0.5)
    assert k == pytest.approx(64)


def test_技術水準が4倍なら定常状態の資本は16倍() -> None:
    k = steady_state_capital(**MODEL, technology=4)
    assert k == pytest.approx(256)
    assert steady_state_output(**MODEL, technology=4) == pytest.approx(64)


def test_収束の速さは1引くアルファかける減耗率() -> None:
    assert convergence_speed(alpha=0.5, depreciation=0.05) == pytest.approx(0.025)


def test_定常状態での写像の傾きは1引く収束の速さ() -> None:
    # 数値微分。linearsolve（pandas 2 の隔離環境）が返した遷移係数 0.975 と同じ値
    k = steady_state_capital(**MODEL)
    h = 1e-4
    slope = (solow_step(k + h, **MODEL) - solow_step(k - h, **MODEL)) / (2 * h)
    assert slope == pytest.approx(1 - convergence_speed(0.5, 0.05), abs=1e-6)
    assert slope == pytest.approx(0.975, abs=1e-6)


def test_半減期は収束の速さが0_5なら1期() -> None:
    assert half_life(0.5) == pytest.approx(1)


def test_収束の速さ0_025の半減期は約27期() -> None:
    assert half_life(0.025) == pytest.approx(27.38, abs=0.01)


def test_対数線形近似は初期値から始まる() -> None:
    path = log_linear_path(4, 16, 0.025, 5)
    assert path[0] == pytest.approx(4)
    assert len(path) == 6


def test_対数線形近似は定常状態に近づく() -> None:
    path = log_linear_path(4, 16, 0.025, 400)
    assert path[-1] == pytest.approx(16, abs=0.01)


def test_対数線形近似は対数の乖離が毎期1引くラムダ倍になる() -> None:
    path = log_linear_path(4, 16, 0.025, 3)
    gaps = [np.log(k / 16) for k in path]
    assert gaps[1] / gaps[0] == pytest.approx(0.975)
    assert gaps[2] / gaps[1] == pytest.approx(0.975)


def test_定常状態の近くでは近似の誤差が小さい() -> None:
    assert approximation_error(15, **MODEL, periods=100) < 0.01


def test_定常状態から遠いほど近似の誤差が大きい() -> None:
    near = approximation_error(14, **MODEL, periods=100)
    far = approximation_error(2, **MODEL, periods=100)
    assert far > near


@pytest.mark.parametrize("alpha", [0, 1, -0.5, 1.5])
def test_資本分配率は0より大きく1より小さくなければならない(alpha: float) -> None:
    with pytest.raises(ValueError, match="資本分配率"):
        steady_state_capital(0.2, 0.05, alpha)


@pytest.mark.parametrize("saving_rate", [0, 1, -0.1])
def test_貯蓄率は0より大きく1より小さくなければならない(saving_rate: float) -> None:
    with pytest.raises(ValueError, match="貯蓄率"):
        steady_state_capital(saving_rate, 0.05, 0.5)


@pytest.mark.parametrize("depreciation", [0, -0.1, 1.5])
def test_減耗率は0より大きく1以下でなければならない(depreciation: float) -> None:
    with pytest.raises(ValueError, match="減耗率"):
        steady_state_capital(0.2, depreciation, 0.5)


def test_減耗率は1ちょうどでもよい() -> None:
    # 資本が毎期すべて失われる。k* = (s·A)^(1 ÷ (1−α)) = 0.2² = 0.04
    assert steady_state_capital(0.2, 1, 0.5) == pytest.approx(0.04)


def test_技術水準は正でなければならない() -> None:
    with pytest.raises(ValueError, match="技術"):
        steady_state_capital(0.2, 0.05, 0.5, technology=0)


def test_資本は正でなければならない() -> None:
    with pytest.raises(ValueError, match="資本"):
        solow_step(0, **MODEL)


def test_繰り返しの回数は負にできない() -> None:
    with pytest.raises(ValueError, match="回数"):
        solow_path(4, **MODEL, periods=-1)


@pytest.mark.parametrize("speed", [0, 1, -0.1, 1.5])
def test_半減期の収束の速さは0より大きく1より小さくなければならない(
    speed: float,
) -> None:
    with pytest.raises(ValueError, match="収束の速さ"):
        half_life(speed)


def test_資本分配率が0_25のとき定常状態の資本は4の3分の4乗() -> None:
    # (0.2 ÷ 0.05)^(1 ÷ 0.75) = 4^(4/3)
    k = steady_state_capital(0.2, 0.05, 0.25)
    assert k == pytest.approx(4 ** (4 / 3))


def test_資本分配率が0_3のとき次の期の資本() -> None:
    # 0.2·10^0.3 + 0.95·10
    assert solow_step(10, 0.2, 0.05, 0.3) == pytest.approx(0.2 * 10**0.3 + 0.95 * 10)


def test_資本分配率が0_3のとき収束の速さは0_035() -> None:
    assert convergence_speed(0.3, 0.05) == pytest.approx(0.035)
