"""第 13 章: 操作変数法の検定（Wu-Hausman・Sargan）と応用のテスト。"""

from typing import Any

import numpy as np
import pandas as pd
import pytest
from linearmodels.iv import IV2SLS

from lib.chapter02.simple import fit_simple
from lib.chapter03.multiple import fit_ols
from lib.chapter05.inference import t_statistics
from lib.chapter12.iv import draw_iv_sample, two_stage_least_squares
from lib.chapter13.iv_tests import (
    draw_market_with_shifter,
    draw_overid_sample,
    draw_two_measurements,
    sargan_rejection_rate,
    sargan_test,
    wu_hausman,
    wu_hausman_rejection_rate,
)


def with_control(n: int = 400) -> pd.DataFrame:
    rng = np.random.default_rng(2)
    s = draw_iv_sample(n, 1.0, 0.5, rng)
    s["w"] = rng.standard_normal(n)
    return s.assign(y=s["y"] + 0.5 * s["w"])


def reference_fit(df: pd.DataFrame, endog: list[str], instruments: list[str]) -> Any:
    exog = pd.DataFrame({"const": np.ones(len(df))})
    if "w" in df:
        exog["w"] = df["w"]
    return IV2SLS(df["y"], exog, df[endog], df[instruments]).fit(
        cov_type="unadjusted", debiased=True
    )


def test_Wu_Hausmanはlinearmodelsと一致する() -> None:
    s = draw_iv_sample(500, 1.0, 0.5, np.random.default_rng(0))
    test = wu_hausman(s["y"], s["x"], s[["z"]])
    reference = reference_fit(s, ["x"], ["z"]).wu_hausman()
    assert test.statistic == pytest.approx(reference.stat)
    assert test.p_value == pytest.approx(reference.pval)


def test_外生の説明変数があってもWu_Hausmanはlinearmodelsと一致する() -> None:
    s = with_control()
    test = wu_hausman(s["y"], s["x"], s[["z"]], s[["w"]])
    reference = reference_fit(s, ["x"], ["z"]).wu_hausman()
    assert test.statistic == pytest.approx(reference.stat)
    assert test.p_value == pytest.approx(reference.pval)


def test_Wu_Hausmanの統計量は第1段階の残差のt値の2乗() -> None:
    s = draw_iv_sample(300, 1.0, 0.5, np.random.default_rng(0))
    v_hat = fit_ols(s["x"], s[["z"]]).residuals
    augmented = fit_ols(s["y"], pd.DataFrame({"x": s["x"], "v_hat": v_hat}))
    test = wu_hausman(s["y"], s["x"], s[["z"]])
    assert test.statistic == pytest.approx(t_statistics(augmented)["v_hat"] ** 2)


def test_説明変数が内生なら外生という仮説を棄却する() -> None:
    s = draw_iv_sample(500, 1.0, 0.5, np.random.default_rng(0))
    assert wu_hausman(s["y"], s["x"], s[["z"]]).p_value < 1e-10


def test_Sarganはlinearmodelsと一致する() -> None:
    for invalid, seed in ((0.0, 1), (0.5, 1)):
        o = draw_overid_sample(500, invalid, np.random.default_rng(seed))
        test = sargan_test(o["y"], o[["x"]], o[["z1", "z2"]])
        reference: Any = IV2SLS(
            o["y"], pd.DataFrame({"const": np.ones(500)}), o[["x"]], o[["z1", "z2"]]
        ).fit(cov_type="unadjusted")
        assert test.statistic == pytest.approx(reference.sargan.stat)
        assert test.p_value == pytest.approx(reference.sargan.pval)


def test_外生の説明変数があってもSarganはlinearmodelsと一致する() -> None:
    s = with_control()
    s["z2"] = 0.5 * s["z"] + np.random.default_rng(3).standard_normal(len(s))
    test = sargan_test(s["y"], s[["x"]], s[["z", "z2"]], s[["w"]])
    reference = reference_fit(s, ["x"], ["z", "z2"])
    assert test.statistic == pytest.approx(reference.sargan.stat)


def test_過剰識別が2つなら自由度2のカイ2乗でlinearmodelsと一致する() -> None:
    o = draw_overid_sample(500, 0.0, np.random.default_rng(1))
    o["z3"] = np.random.default_rng(7).standard_normal(500)
    test = sargan_test(o["y"], o[["x"]], o[["z1", "z2", "z3"]])
    reference: Any = IV2SLS(
        o["y"], pd.DataFrame({"const": np.ones(500)}), o[["x"]], o[["z1", "z2", "z3"]]
    ).fit(cov_type="unadjusted")
    assert test.statistic == pytest.approx(reference.sargan.stat)
    assert test.p_value == pytest.approx(reference.sargan.pval)
    assert reference.sargan.df == 2


def test_識別のちょうどの場合Sargan検定はできない() -> None:
    s = draw_iv_sample(100, 1.0, 0.5, np.random.default_rng(0))
    with pytest.raises(ValueError, match="過剰識別"):
        sargan_test(s["y"], s[["x"]], s[["z"]])


def test_有効な操作変数ではSarganは棄却せず無効な操作変数では棄却する() -> None:
    valid = draw_overid_sample(500, 0.0, np.random.default_rng(1))
    invalid = draw_overid_sample(500, 0.5, np.random.default_rng(1))
    assert sargan_test(valid["y"], valid[["x"]], valid[["z1", "z2"]]).p_value > 0.05
    assert (
        sargan_test(invalid["y"], invalid[["x"]], invalid[["z1", "z2"]]).p_value < 1e-6
    )


def test_過剰識別の標本の相関() -> None:
    o = draw_overid_sample(50000, 0.5, np.random.default_rng(0))
    u = o["y"] - 1 - o["x"]
    assert list(o.columns) == ["y", "x", "z1", "z2"]
    assert np.cov(o["z2"], u)[0, 1] == pytest.approx(0.5, abs=0.03)
    assert np.cov(o["z1"], u)[0, 1] == pytest.approx(0, abs=0.03)
    assert np.cov(o["z1"], o["x"])[0, 1] == pytest.approx(1, abs=0.03)
    assert np.cov(o["z2"], o["x"])[0, 1] == pytest.approx(1, abs=0.03)


def test_外生なら棄却率は有意水準に近く内生なら高い() -> None:
    size = wu_hausman_rejection_rate(500, 0.0, 500, 0.05, np.random.default_rng(0))
    power = wu_hausman_rejection_rate(500, 0.3, 500, 0.05, np.random.default_rng(0))
    assert size == pytest.approx(0.05, abs=4 * (0.05 * 0.95 / 500) ** 0.5)
    assert power > 0.95


def test_操作変数が有効なら棄却率は有意水準に近く無効なほど高い() -> None:
    size = sargan_rejection_rate(500, 0.0, 500, 0.05, np.random.default_rng(0))
    weak = sargan_rejection_rate(500, 0.1, 500, 0.05, np.random.default_rng(0))
    strong = sargan_rejection_rate(500, 0.3, 500, 0.05, np.random.default_rng(0))
    assert size == pytest.approx(0.05, abs=4 * (0.05 * 0.95 / 500) ** 0.5)
    assert 0.2 < weak < strong
    assert strong > 0.95


def test_供給の変動要因を操作変数にすると需要の傾きを識別できる() -> None:
    m = draw_market_with_shifter(5000, np.random.default_rng(0))
    ols = fit_simple(m["p"], m["q"]).slope
    result = two_stage_least_squares(m["q"], m[["p"]], m[["w"]])
    assert abs(ols + 1) > 0.2
    assert abs(result.coefficients["p"] + 1) < 4 * result.standard_errors["p"]


def test_供給の変動要因は価格を下げ需要の誤差とは無関係() -> None:
    m = draw_market_with_shifter(50000, np.random.default_rng(0))
    assert list(m.columns) == ["p", "q", "w"]
    assert np.cov(m["w"], m["p"])[0, 1] == pytest.approx(-1.0, abs=0.03)
    demand_shock = m["q"] - (10 - m["p"])
    assert np.cov(m["w"], demand_shock)[0, 1] == pytest.approx(0, abs=0.03)


def test_2回目の測定を操作変数にすると測定誤差のバイアスが消える() -> None:
    d = draw_two_measurements(5000, 1.0, np.random.default_rng(0))
    ols = fit_simple(d["x1"], d["y"]).slope
    result = two_stage_least_squares(d["y"], d[["x1"]], d[["x2"]])
    assert ols == pytest.approx(0.5, abs=0.05)
    assert abs(result.coefficients["x1"] - 1) < 4 * result.standard_errors["x1"]


def test_2回の測定の標本の形() -> None:
    d = draw_two_measurements(20000, 1.0, np.random.default_rng(0))
    assert list(d.columns) == ["y", "x1", "x2"]
    assert np.var(d["x1"]) == pytest.approx(2, rel=0.05)
    assert np.var(d["x2"]) == pytest.approx(2, rel=0.05)
    assert np.cov(d["x1"], d["x2"])[0, 1] == pytest.approx(1, abs=0.05)
