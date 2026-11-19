"""第 13 章: 動学的 AD-AS モデルとカリブレーションのテスト。

モデル（y: 産出量の乖離、p: 物価の乖離。どちらも、トレンドからの乖離、%）:
  AS 曲線  p(t) = p(t-1) + a·y(t) + v(t)
  AD 曲線  y(t) = -c·p(t) + u(t)
均衡式:  p(t) = h·p(t-1) + h·(a·u(t) + v(t))、h = 1 ÷ (1 + a·c)
"""

import numpy as np
import pandas as pd
import pytest

from lib.chapter13.adas import (
    AdasParameters,
    adas_cycles,
    adas_step,
    calibrate,
    data_features,
    load_adas_quarterly,
    model_moments,
)

TRUE = AdasParameters(a=0.8, c=0.3, sigma_u=1.5, sigma_v=1.2)


def simulated_cycles(
    params: AdasParameters, n: int, seed: int
) -> tuple[pd.Series, pd.Series]:
    """モデルから、乖離の系列（y, p）を作る。第 14 章の simulate の下書き。"""
    rng = np.random.default_rng(seed)
    p = 0.0
    ys, ps = [], []
    for _ in range(n):
        u = rng.normal(0, params.sigma_u)
        v = rng.normal(0, params.sigma_v)
        p, y = adas_step(p, u, v, params)
        ys.append(y)
        ps.append(p)
    return pd.Series(ys), pd.Series(ps)


def test_hはaとcの積で決まる() -> None:
    assert TRUE.h == pytest.approx(1 / (1 + 0.8 * 0.3))


@pytest.mark.parametrize(
    ("a", "c", "su", "sv"),
    [
        (0, 0.3, 1, 1),
        (-0.1, 0.3, 1, 1),
        (0.8, 0, 1, 1),
        (0.8, 0.3, -1, 1),
        (0.8, 0.3, 1, -1),
    ],
)
def test_パラメーターの符号が合わなければ受け付けない(
    a: float, c: float, su: float, sv: float
) -> None:
    with pytest.raises(ValueError, match="パラメーター"):
        AdasParameters(a=a, c=c, sigma_u=su, sigma_v=sv)


def test_ショックがなければ定常状態にとどまる() -> None:
    assert adas_step(0.0, 0.0, 0.0, TRUE) == (0.0, 0.0)


def test_需要ショックは物価も産出量も上げる() -> None:
    params = AdasParameters(a=1, c=1, sigma_u=1, sigma_v=1)
    p, y = adas_step(0.0, 1.0, 0.0, params)
    assert p == pytest.approx(0.5)
    assert y == pytest.approx(0.5)


def test_供給ショックは物価を上げて産出量を下げる() -> None:
    params = AdasParameters(a=1, c=1, sigma_u=1, sigma_v=1)
    p, y = adas_step(0.0, 0.0, 1.0, params)
    assert p == pytest.approx(0.5)
    assert y == pytest.approx(-0.5)


@pytest.mark.parametrize(
    ("p_prev", "u", "v"), [(0.0, 1.0, 0.0), (2.0, -0.5, 0.7), (-1.3, 0.2, -0.4)]
)
def test_均衡はAS曲線とAD曲線を同時に満たす(p_prev: float, u: float, v: float) -> None:
    p, y = adas_step(p_prev, u, v, TRUE)
    assert p == pytest.approx(p_prev + TRUE.a * y + v)
    assert y == pytest.approx(-TRUE.c * p + u)


def test_ショックのないデータからaとcをちょうど復元できる() -> None:
    h = TRUE.h
    p = pd.Series([h**t for t in range(30)])
    y = -TRUE.c * p
    result = calibrate(y, p)
    assert result.a == pytest.approx(0.8)
    assert result.c == pytest.approx(0.3)
    assert result.sigma_u == pytest.approx(0, abs=1e-6)
    assert result.sigma_v == pytest.approx(0, abs=1e-6)


def test_長い系列から真のパラメーターに近い値を復元する() -> None:
    y, p = simulated_cycles(TRUE, 20000, seed=6)
    result = calibrate(y, p)
    assert result.a == pytest.approx(0.8, abs=0.05)
    assert result.c == pytest.approx(0.3, abs=0.05)
    assert result.sigma_u == pytest.approx(1.5, abs=0.05)
    assert result.sigma_v == pytest.approx(1.2, abs=0.05)


def test_物価が上がっても産出量が下がらないデータはモデルと合わない() -> None:
    p = pd.Series([0.8**t for t in range(30)])
    y = 0.3 * p
    with pytest.raises(ValueError, match="パラメーター"):
        calibrate(y, p)


def test_計算に使う期間が短すぎると受け付けない() -> None:
    p = pd.Series([1.0, 0.8, 0.64])
    with pytest.raises(ValueError, match="観測数"):
        calibrate(-0.3 * p, p)


def test_モデルの積率を手計算の例と照合する() -> None:
    params = AdasParameters(a=1, c=1, sigma_u=1, sigma_v=0)
    moments = model_moments(params)
    assert moments["p_std"] == pytest.approx(np.sqrt(1 / 3))
    assert moments["y_std"] == pytest.approx(np.sqrt(1 / 3))
    assert moments["p_autocorr"] == pytest.approx(0.5)
    assert moments["y_autocorr"] == pytest.approx(-0.25)
    assert moments["correlation"] == pytest.approx(0.5)


def test_物価の自己相関はhに等しい() -> None:
    assert model_moments(TRUE)["p_autocorr"] == pytest.approx(TRUE.h)


def test_積率は長いシミュレーションの標本の値に近い() -> None:
    y, p = simulated_cycles(TRUE, 100000, seed=1)
    simulated = data_features(y, p)
    theory = model_moments(TRUE)
    for key in ("y_std", "p_std", "y_autocorr", "p_autocorr", "correlation"):
        assert simulated[key] == pytest.approx(theory[key], abs=0.02)


def test_データの特徴は標準偏差と自己相関と相関() -> None:
    y = pd.Series([1.0, 2.0, 3.0, 4.0])
    p = pd.Series([4.0, 3.0, 2.0, 1.0])
    features = data_features(y, p)
    assert list(features) == [
        "y_std",
        "p_std",
        "y_autocorr",
        "p_autocorr",
        "correlation",
    ]
    assert features["y_std"] == pytest.approx(np.std([1, 2, 3, 4], ddof=1))
    assert features["y_autocorr"] == pytest.approx(0.25)
    assert features["correlation"] == pytest.approx(-1.0)


def test_同梱のデータは1980年から2019年までの160四半期() -> None:
    df = load_adas_quarterly()
    assert len(df) == 160
    assert str(df.index[0]) == "1980Q1"
    assert str(df.index[-1]) == "2019Q4"
    assert list(df.columns) == ["gdp", "deflator"]


def test_乖離の系列は平均がほぼ0で産出量と物価の2列() -> None:
    cycles = adas_cycles(load_adas_quarterly())
    assert list(cycles.columns) == ["y", "p"]
    assert abs(cycles["y"].mean()) < 0.1
    assert abs(cycles["p"].mean()) < 0.1


def test_同梱のデータのカリブレーション() -> None:
    cycles = adas_cycles(load_adas_quarterly())
    result = calibrate(cycles["y"], cycles["p"])
    assert result.a == pytest.approx(1.083, abs=0.001)
    assert result.c == pytest.approx(0.550, abs=0.001)
    assert result.sigma_u == pytest.approx(1.706, abs=0.001)
    assert result.sigma_v == pytest.approx(1.206, abs=0.001)
    assert result.h == pytest.approx(0.627, abs=0.001)


def test_短い系列とHPフィルターでは真の値から離れる() -> None:
    """真のパラメーター（0.8, 0.3）とは、HP フィルターと標本の短さの分だけ違う。"""
    cycles = adas_cycles(load_adas_quarterly())
    result = calibrate(cycles["y"], cycles["p"])
    assert abs(result.a - TRUE.a) > 0.2
    assert abs(result.h - TRUE.h) > 0.15


def test_同梱のデータの特徴とモデルの積率() -> None:
    cycles = adas_cycles(load_adas_quarterly())
    features = data_features(cycles["y"], cycles["p"])
    assert features["y_std"] == pytest.approx(1.310, abs=0.001)
    assert features["p_std"] == pytest.approx(1.722, abs=0.001)
    assert features["p_autocorr"] == pytest.approx(0.620, abs=0.001)
    moments = model_moments(calibrate(cycles["y"], cycles["p"]))
    assert moments["y_std"] == pytest.approx(1.300, abs=0.001)
    assert moments["p_autocorr"] == pytest.approx(0.627, abs=0.001)


def test_ショックの標準偏差が0でもパラメーターとして受け付ける() -> None:
    params = AdasParameters(a=0.8, c=0.3, sigma_u=0, sigma_v=0)
    assert params.sigma_u == 0
    assert params.sigma_v == 0


def test_水準がずれていても係数と残差は変わらない() -> None:
    y, p = simulated_cycles(TRUE, 2000, seed=3)
    base = calibrate(y, p)
    shifted = calibrate(y + 3, p + 5)
    assert shifted.a == pytest.approx(base.a)
    assert shifted.c == pytest.approx(base.c)
    assert shifted.sigma_u == pytest.approx(base.sigma_u)
    assert shifted.sigma_v == pytest.approx(base.sigma_v)
