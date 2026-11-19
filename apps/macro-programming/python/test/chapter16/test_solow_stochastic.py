"""第 16 章: 確率的ソロー・モデルと景気循環の要素分解のテスト。

生産関数 Y = A·B·K^α·H^(1-α)（A: 変動、B: トレンド）、資本の蓄積 K' = s·Y + (1-δ)·K、
TFP は、log A(t) = ρ·log A(t-1) + ε(t)。
"""

import numpy as np
import pandas as pd
import pytest

from lib.chapter08.stochastic import ar1_series
from lib.chapter16.solow_stochastic import (
    SolowParameters,
    business_cycle_components,
    decompose_business_cycle,
    fit_ar1_without_constant,
    load_solow_quarterly,
    log_deviations,
    simulate_with_shocks,
    steady_state_capital,
    stochastic_solow,
    total_factor_productivity,
)

PARAMS = SolowParameters(
    alpha=0.36, saving=0.2, depreciation=0.025, rho=0.55, sigma=0.0078, hours=1.0
)


def test_TFPは産出量を要素投入で割った値() -> None:
    gdp = pd.Series([4.0, 100.0])
    capital = pd.Series([4.0, 100.0])
    hours = pd.Series([1.0, 100.0])
    tfp = total_factor_productivity(gdp, capital, hours, alpha=0.5)
    assert tfp.tolist() == pytest.approx([2.0, 1.0])


def test_パラメーターの範囲が合わなければ受け付けない() -> None:
    with pytest.raises(ValueError, match="パラメーター"):
        SolowParameters(alpha=1.0)
    with pytest.raises(ValueError, match="パラメーター"):
        SolowParameters(saving=0.0)
    with pytest.raises(ValueError, match="パラメーター"):
        SolowParameters(depreciation=1.5)
    with pytest.raises(ValueError, match="パラメーター"):
        SolowParameters(rho=1.0)
    with pytest.raises(ValueError, match="パラメーター"):
        SolowParameters(sigma=-0.1)
    with pytest.raises(ValueError, match="パラメーター"):
        SolowParameters(saving=1.0)
    with pytest.raises(ValueError, match="パラメーター"):
        SolowParameters(depreciation=1.0)
    with pytest.raises(ValueError, match="パラメーター"):
        SolowParameters(hours=0.0)


def test_定常状態の資本は貯蓄と減耗が等しくなる水準() -> None:
    k = steady_state_capital(PARAMS)
    output = k**PARAMS.alpha * PARAMS.hours ** (1 - PARAMS.alpha)
    assert PARAMS.saving * output == pytest.approx(PARAMS.depreciation * k)


def test_ショックがなければ定常状態にとどまる() -> None:
    quiet = SolowParameters(sigma=0.0)
    df = stochastic_solow(quiet, 30, np.random.default_rng(0))
    assert df["K"].tolist() == pytest.approx([steady_state_capital(quiet)] * 30)
    assert df["A"].tolist() == pytest.approx([1.0] * 30)
    assert df["Y"].nunique() == 1


def test_消費と投資は産出量を貯蓄率で分ける() -> None:
    df = stochastic_solow(PARAMS, 50, np.random.default_rng(1))
    assert df["C"].to_numpy() == pytest.approx(
        ((1 - PARAMS.saving) * df["Y"]).to_numpy()
    )
    assert df["I"].to_numpy() == pytest.approx((PARAMS.saving * df["Y"]).to_numpy())
    assert (df["C"] + df["I"]).to_numpy() == pytest.approx(df["Y"].to_numpy())


def test_資本は前期の投資と減耗後の資本の和() -> None:
    df = stochastic_solow(PARAMS, 50, np.random.default_rng(1))
    expected = df["I"] + (1 - PARAMS.depreciation) * df["K"]
    assert df["K"].iloc[1:].to_numpy() == pytest.approx(expected.iloc[:-1].to_numpy())


def test_生産関数は産出量を決める() -> None:
    df = stochastic_solow(PARAMS, 20, np.random.default_rng(2))
    expected = df["A"] * df["K"] ** PARAMS.alpha * PARAMS.hours ** (1 - PARAMS.alpha)
    assert df["Y"].to_numpy() == pytest.approx(expected.to_numpy())


def test_TFPはAR1で最初の期はショックそのもの() -> None:
    shocks = np.array([0.01, 0.0, 0.0])
    df = simulate_with_shocks(PARAMS, shocks)
    assert np.log(df["A"]).tolist() == pytest.approx(
        [0.01, 0.55 * 0.01, 0.55**2 * 0.01]
    )


def test_プラスのTFPショックは同じ期の産出を増やし資本は翌期から増える() -> None:
    shocks = np.array([0.01, 0.0, 0.0, 0.0])
    df = simulate_with_shocks(PARAMS, shocks)
    k_star = steady_state_capital(PARAMS)
    assert df["K"].iloc[0] == pytest.approx(k_star)
    assert df["Y"].iloc[0] > df["Y"].iloc[1] > 0
    assert df["K"].iloc[1] > k_star
    assert df["K"].iloc[2] > df["K"].iloc[1]


def test_初期の資本が定常状態より大きければ収束速度は1マイナス1マイナスα倍のδ() -> None:
    quiet = SolowParameters(sigma=0.0)
    k_star = steady_state_capital(quiet)
    df = simulate_with_shocks(quiet, np.zeros(40), initial_capital=k_star * 1.001)
    gap = np.log(df["K"] / k_star)
    speed = (1 - quiet.alpha) * quiet.depreciation
    assert gap.iloc[1] / gap.iloc[0] == pytest.approx(1 - speed, abs=1e-4)
    assert gap.iloc[-1] < gap.iloc[0]


def test_乱数の種が同じなら同じ結果() -> None:
    first = stochastic_solow(PARAMS, 30, np.random.default_rng(3))
    second = stochastic_solow(PARAMS, 30, np.random.default_rng(3))
    pd.testing.assert_frame_equal(first, second)


def test_シミュレーションの長さは1以上() -> None:
    with pytest.raises(ValueError, match="1 以上"):
        stochastic_solow(PARAMS, 0, np.random.default_rng(0))


def test_定常状態からの対数乖離は百分率() -> None:
    shocks = np.array([0.01, 0.0])
    df = simulate_with_shocks(PARAMS, shocks)
    dev = log_deviations(df, PARAMS)
    assert list(dev.columns) == ["a", "y", "k", "c", "i"]
    assert dev["a"].iloc[0] == pytest.approx(1.0)
    assert dev["y"].iloc[0] == pytest.approx(1.0)
    assert dev["k"].iloc[0] == pytest.approx(0.0, abs=1e-9)


def test_消費と投資の変動は産出量と同じになる() -> None:
    """貯蓄率が一定なので、モデルは、消費の平滑化を再現できない。"""
    df = stochastic_solow(PARAMS, 200, np.random.default_rng(5))
    dev = log_deviations(df, PARAMS)
    assert dev["c"].to_numpy() == pytest.approx(dev["y"].to_numpy())
    assert dev["i"].to_numpy() == pytest.approx(dev["y"].to_numpy())


def test_AR1の係数は定数なしの回帰で求める() -> None:
    rho, sigma = fit_ar1_without_constant(pd.Series([1.0, 0.5, 0.25, 0.125]))
    assert rho == pytest.approx(0.5)
    assert sigma == pytest.approx(0.0, abs=1e-12)


def test_長いAR1系列から係数と標準偏差を復元する() -> None:
    x = pd.Series(ar1_series(0.6, 0.8, 20000, np.random.default_rng(4)))
    rho, sigma = fit_ar1_without_constant(x)
    assert rho == pytest.approx(0.6, abs=0.02)
    assert sigma == pytest.approx(0.8, abs=0.02)


def test_要素分解の寄与は手計算の例と一致する() -> None:
    cycles = pd.DataFrame(
        {
            "a": [1.0, -1.0, 1.0, -1.0],
            "k": [1.0, 1.0, -1.0, -1.0],
            "h": [1.0, -1.0, -1.0, 1.0],
        }
    )
    cycles["y"] = cycles["a"] + 0.5 * cycles["k"] + 0.5 * cycles["h"]
    shares = decompose_business_cycle(cycles, alpha=0.5)
    assert shares["tfp"] == pytest.approx(4 / 6)
    assert shares["capital"] == pytest.approx(1 / 6)
    assert shares["labour"] == pytest.approx(1 / 6)
    assert shares.sum() == pytest.approx(1.0)


def test_生産関数が成り立てば寄与の和は1() -> None:
    rng = np.random.default_rng(9)
    cycles = pd.DataFrame({name: rng.normal(size=100) for name in ("a", "k", "h")})
    cycles["y"] = cycles["a"] + 0.36 * cycles["k"] + 0.64 * cycles["h"]
    shares = decompose_business_cycle(cycles, alpha=0.36)
    assert shares.sum() == pytest.approx(1.0)
    assert list(shares.index) == ["tfp", "capital", "labour"]


def test_同梱のデータは1980年から2019年までの160四半期() -> None:
    df = load_solow_quarterly()
    assert len(df) == 160
    assert str(df.index[0]) == "1980Q1"
    assert list(df.columns) == ["gdp", "capital", "total_hours"]


def test_乖離の系列は4列で生産関数の恒等式を満たす() -> None:
    cycles = business_cycle_components(load_solow_quarterly(), alpha=0.36)
    assert list(cycles.columns) == ["y", "k", "h", "a"]
    identity = cycles["a"] + 0.36 * cycles["k"] + 0.64 * cycles["h"]
    assert identity.to_numpy() == pytest.approx(cycles["y"].to_numpy())


def test_同梱のデータの要素分解() -> None:
    cycles = business_cycle_components(load_solow_quarterly(), alpha=0.36)
    shares = decompose_business_cycle(cycles, alpha=0.36)
    assert shares["tfp"] == pytest.approx(0.583, abs=0.001)
    assert shares["capital"] == pytest.approx(-0.003, abs=0.001)
    assert shares["labour"] == pytest.approx(0.420, abs=0.001)
    assert shares.sum() == pytest.approx(1.0)


def test_同梱のデータのTFPの変動はGDPの変動と強く相関する() -> None:
    cycles = business_cycle_components(load_solow_quarterly(), alpha=0.36)
    assert cycles["y"].std() == pytest.approx(1.279, abs=0.001)
    assert cycles["a"].std() == pytest.approx(0.823, abs=0.001)
    assert cycles["y"].corr(cycles["a"]) == pytest.approx(0.907, abs=0.001)
    assert cycles["a"].corr(cycles["h"]) == pytest.approx(0.561, abs=0.001)


def test_同梱のデータのAR1の推定() -> None:
    """真の値（TFP は ρ = 0.6、σ = 0.8、労働時間は ρ = 0.8）とは、少し違う。"""
    cycles = business_cycle_components(load_solow_quarterly(), alpha=0.36)
    rho_a, sigma_a = fit_ar1_without_constant(cycles["a"])
    rho_h, _ = fit_ar1_without_constant(cycles["h"])
    assert rho_a == pytest.approx(0.514, abs=0.001)
    assert sigma_a == pytest.approx(0.708, abs=0.001)
    assert rho_h == pytest.approx(0.829, abs=0.001)


def test_シミュレーションの特徴は産出量とTFPが同じ動きで資本は緩やか() -> None:
    params = SolowParameters(
        alpha=0.36, saving=0.2, depreciation=0.025, rho=0.6, sigma=0.008, hours=1.0
    )
    simulated = stochastic_solow(params, 200, np.random.default_rng(123))
    dev = log_deviations(simulated, params)
    assert dev["y"].std() == pytest.approx(0.885, abs=0.001)
    assert dev["k"].std() == pytest.approx(0.122, abs=0.001)
    assert dev["y"].autocorr() == pytest.approx(0.576, abs=0.001)
    assert dev["k"].autocorr() == pytest.approx(0.983, abs=0.001)
    assert dev["y"].corr(dev["k"]) == pytest.approx(0.002, abs=0.001)
    assert dev["y"].corr(dev["a"]) == pytest.approx(0.999, abs=0.001)


def test_トレンドは最初の期が1で毎期1プラスg倍になる() -> None:
    params = SolowParameters(sigma=0.0, growth=0.01)
    df = simulate_with_shocks(params, np.zeros(2))
    k0 = df["K"].iloc[0]
    assert df["Y"].iloc[0] == pytest.approx(k0**params.alpha)
    k1 = params.saving * df["Y"].iloc[0] + (1 - params.depreciation) * k0
    assert df["Y"].iloc[1] == pytest.approx(1.01 * k1**params.alpha)
