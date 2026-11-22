"""アニメーション（lib/animations）のテスト。

フレームごとのデータは、各章の関数と一致すること。GIF の保存は、全フレームを描くので、
更新の関数が動くことの確認になる。
"""

from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest
from matplotlib.animation import FuncAnimation

from lib.animations.adas import adas_frames, animate_adas_impulse
from lib.animations.common import linear_values
from lib.animations.difference import animate_difference, difference_frames
from lib.animations.ismppc import animate_ismppc_impulse, ismppc_frames
from lib.animations.loglinear import animate_loglinear_error, loglinear_frames
from lib.animations.rbc import animate_rbc_impulse, rbc_frames
from lib.animations.solow import animate_solow_saving, solow_frames
from lib.animations.stochastic import animate_ar1, ar1_frames
from lib.chapter04.difference import linear_path
from lib.chapter05.solow import solow_path, steady_state_capital
from lib.chapter08.stochastic import ar1_series, sample_autocorrelation
from lib.chapter13.adas import AdasParameters
from lib.chapter14.simulation import impulse_response
from lib.chapter15.ismppc import IsMpPcParameters
from lib.chapter15.ismppc import impulse_response as ismppc_impulse
from lib.chapter16.solow_stochastic import SolowParameters
from lib.chapter17.loglinear import capital_paths
from lib.chapter18.rbc import RbcParameters, solve_rbc
from lib.chapter18.rbc import impulse_response as rbc_impulse


def test_等間隔の値は両端を含む() -> None:
    assert linear_values(0, 10, 5) == [0, 2.5, 5, 7.5, 10]
    assert linear_values(4, 1, 4) == [4, 3, 2, 1]


def test_フレーム数は2以上() -> None:
    with pytest.raises(ValueError, match="フレーム数"):
        linear_values(0, 1, 1)


def test_差分方程式の各フレームは係数に応じた経路() -> None:
    data = difference_frames(2.0, 0.0, 5, -1.0, 0.5, 4)
    assert [f.a for f in data] == [-1.0, -0.5, 0.0, 0.5]
    assert data[1].path == linear_path(-0.5, 2.0 * 1.5, 0.0, 5)
    assert data[0].path[:3] == [0.0, 4.0, 0.0]
    assert data[2].path == [0.0] + [2.0] * 5
    assert abs(data[3].path[-1] - 2.0) < abs(data[3].path[0] - 2.0)


def test_ソローの各フレームは貯蓄率に応じた定常状態へ向かう() -> None:
    data = solow_frames(0.1, 0.4, 0.05, 0.5, 2.0, 100, 4)
    assert [f.saving_rate for f in data] == pytest.approx([0.1, 0.2, 0.3, 0.4])
    assert data[0].steady == steady_state_capital(0.1, 0.05, 0.5)
    assert data[1].path == solow_path(2.0, 0.2, 0.05, 0.5, 100)
    steady = [f.steady for f in data]
    assert steady == sorted(steady)
    assert data[0].path[-1] == pytest.approx(data[0].steady, rel=0.1)


def test_AR1の各フレームは同じショックで係数だけが変わる() -> None:
    data = ar1_frames(0.9, 1.0, 50, 0, 4)
    assert [f.rho for f in data] == pytest.approx([0.0, 0.3, 0.6, 0.9])
    expected = ar1_series(0.6, 1.0, 50, np.random.default_rng(0))
    assert np.array_equal(data[2].series, expected)
    assert data[2].autocorrelation == sample_autocorrelation(expected, 1)
    assert data[3].autocorrelation > data[0].autocorrelation


def test_ADASの各フレームは傾きに応じた物価の持続性() -> None:
    data = adas_frames(0.5, 2.0, 0.3, 1.0, 4)
    assert [f.a for f in data] == pytest.approx([0.5, 1.0, 1.5, 2.0])
    params = AdasParameters(1.0, 0.3, 0.0, 0.0)
    assert data[1].h == params.h
    assert data[1].response.equals(impulse_response(params, u=1.0))
    persistence = [f.h for f in data]
    assert persistence == sorted(persistence, reverse=True)


def test_金融政策の各フレームは反応の強さに応じた収束() -> None:
    data = ismppc_frames(0.0, 3.0, 4)
    assert [f.c for f in data] == [0.0, 1.0, 2.0, 3.0]
    params = IsMpPcParameters(c=1.0)
    assert data[1].phi == params.phi
    assert data[1].response.equals(ismppc_impulse(params, shock_pc=1.0))
    assert data[0].phi == 1.0
    persistence = [f.phi for f in data]
    assert persistence == sorted(persistence, reverse=True)


def test_近似の各フレームは初期の乖離に応じた誤差() -> None:
    data = loglinear_frames(0.8, 30, 4)
    assert [f.deviation for f in data] == pytest.approx([0.2, 0.4, 0.6, 0.8])
    expected = capital_paths(SolowParameters(), 0.4, 30)
    assert data[1].paths.equals(expected)
    gaps = [abs(f.paths["exact"] - f.paths["linear"]).max() for f in data]
    assert gaps == sorted(gaps)


def test_RBCの各フレームはショックの持続性に応じた反応() -> None:
    data = rbc_frames(0.2, 0.9, 3)
    assert [f.rho for f in data] == pytest.approx([0.2, 0.55, 0.9])
    expected = rbc_impulse(solve_rbc(RbcParameters(rho=data[1].rho)), shock=0.01)
    assert data[1].response.equals(expected)
    peaks = [f.response["k"].max() for f in data]
    assert peaks == sorted(peaks)


BUILDERS: dict[str, Callable[[], FuncAnimation]] = {
    "difference": lambda: animate_difference(frames=4),
    "solow": lambda: animate_solow_saving(frames=4),
    "ar1": lambda: animate_ar1(frames=4),
    "adas": lambda: animate_adas_impulse(frames=4),
    "ismppc": lambda: animate_ismppc_impulse(frames=4),
    "loglinear": lambda: animate_loglinear_error(frames=4),
    "rbc": lambda: animate_rbc_impulse(frames=4),
}


@pytest.mark.parametrize("name", sorted(BUILDERS))
def test_アニメーションをGIFに保存できる(name: str, tmp_path: Path) -> None:
    animation = BUILDERS[name]()
    assert isinstance(animation, FuncAnimation)
    path = tmp_path / f"{name}.gif"
    animation.save(path, writer="pillow", fps=5, dpi=30)
    assert path.read_bytes()[:6] == b"GIF89a"
