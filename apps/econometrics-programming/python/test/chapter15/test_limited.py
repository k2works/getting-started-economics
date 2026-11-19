"""第 15 章: トービットと切断回帰（最尤法）のテスト。"""

import math
from collections.abc import Callable
from types import SimpleNamespace

import numpy as np
import pytest

from lib.chapter03.multiple import fit_ols
from lib.chapter15 import limited
from lib.chapter15.limited import (
    censor,
    draw_latent_sample,
    fit_tobit,
    fit_truncreg,
    hessian_from_gradient,
    tobit_expected_value,
    tobit_gradient,
    tobit_log_likelihood,
    tobit_marginal_effects,
    truncate,
    truncreg_gradient,
    truncreg_log_likelihood,
)

# 手計算用: x = 0 と 1、β = (0.5, 1)、σ = 1（ln σ = 0）、下限 0
PARAMS = np.array([0.5, 1.0, 0.0])
DESIGN = np.column_stack([np.ones(2), [0.0, 1.0]])


def latent(n: int = 20000, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    return draw_latent_sample(n, np.random.default_rng(seed))


def test_トービットの対数尤度の手計算() -> None:
    # y = 0（打ち切り）: ln Φ(−0.5)、y = 2: ln φ(2 − 1.5)
    expected = (
        math.log(0.5 * math.erfc(0.5 / math.sqrt(2)))
        - 0.5 * math.log(2 * math.pi)
        - 0.125
    )
    value = tobit_log_likelihood(PARAMS, np.array([0.0, 2.0]), DESIGN, 0.0)
    assert value == pytest.approx(expected)
    assert value == pytest.approx(-2.2199, abs=1e-4)


def test_切断回帰の対数尤度の手計算() -> None:
    value = truncreg_log_likelihood(PARAMS, np.array([1.0, 2.0]), DESIGN, 0.0)
    assert value == pytest.approx(-1.6498, abs=1e-4)


def numerical_gradient(
    f: Callable[[np.ndarray], float], point: np.ndarray
) -> np.ndarray:
    step = 1e-6
    result = np.zeros(len(point))
    for i in range(len(point)):
        e = np.eye(len(point))[i] * step
        result[i] = (f(point + e) - f(point - e)) / (2 * step)
    return result


def test_トービットの解析的な勾配は数値微分に一致する() -> None:
    x, y = latent(400)
    observed = censor(y)
    design = np.column_stack([np.ones(400), x])
    for params in (np.array([0.5, 1.5, 0.3]), np.array([-1.0, 3.0, 1.0])):
        numeric = numerical_gradient(
            lambda p: tobit_log_likelihood(p, observed, design, 0.0), params
        )
        assert tobit_gradient(params, observed, design, 0.0) == pytest.approx(
            numeric, rel=1e-5, abs=1e-5
        )


def test_切断回帰の解析的な勾配は数値微分に一致する() -> None:
    x, y = latent(400)
    kept_x, kept_y = truncate(x, y)
    design = np.column_stack([np.ones(len(kept_x)), kept_x])
    for params in (np.array([0.5, 1.5, 0.3]), np.array([1.0, 2.0, 0.7])):
        numeric = numerical_gradient(
            lambda p: truncreg_log_likelihood(p, kept_y, design, 0.0), params
        )
        assert truncreg_gradient(params, kept_y, design, 0.0) == pytest.approx(
            numeric, rel=1e-5, abs=1e-5
        )


def test_yの単位を1000倍しても係数と標準偏差が1000倍になるだけ() -> None:
    x, y = latent(3000)
    observed = censor(y)
    small = fit_tobit(observed, x)
    large = fit_tobit(observed * 1000, x)
    assert large.coefficients.to_numpy() == pytest.approx(
        small.coefficients.to_numpy() * 1000, rel=1e-4
    )
    assert large.standard_errors.to_numpy() == pytest.approx(
        small.standard_errors.to_numpy() * 1000, rel=1e-3
    )


def test_ヘッセ行列は既知の2次式の勾配の差分に一致する() -> None:
    def gradient(v: np.ndarray) -> np.ndarray:
        # f = 3a² + ab + 2b² の勾配
        return np.array([6 * v[0] + v[1], v[0] + 4 * v[1]])

    hessian = hessian_from_gradient(gradient, np.array([1.0, 2.0]))
    assert hessian == pytest.approx(np.array([[6.0, 1.0], [1.0, 4.0]]), abs=1e-6)


def test_ヘッセ行列は対称にそろえる() -> None:
    # 勾配 (b, 0) の微分は [[0, 1], [0, 0]]。対称にそろえると [[0, 0.5], [0.5, 0]]
    def gradient(v: np.ndarray) -> np.ndarray:
        return np.array([v[1], 0.0])

    hessian = hessian_from_gradient(gradient, np.array([1.0, 2.0]))
    assert hessian == pytest.approx(np.array([[0.0, 0.5], [0.5, 0.0]]), abs=1e-6)
    assert hessian == pytest.approx(hessian.T)


def test_大きな値のパラメータでもヘッセ行列を求められる() -> None:
    def gradient(v: np.ndarray) -> np.ndarray:
        return np.array([2 * v[0], 6 * v[1]])

    hessian = hessian_from_gradient(gradient, np.array([1000.0, 5.0]))
    assert hessian == pytest.approx(np.array([[2.0, 0.0], [0.0, 6.0]]), abs=1e-4)


def test_打ち切りは下限未満を下限にし_切断は下限以下を除く() -> None:
    x = np.array([1.0, 2.0, 3.0, 4.0])
    y = np.array([-1.0, 0.0, 0.5, 2.0])
    assert censor(y).tolist() == [0, 0, 0.5, 2]
    assert censor(y, 1.0).tolist() == [1, 1, 1, 2]
    kept_x, kept_y = truncate(x, y)
    assert kept_x.tolist() == [3, 4]
    assert kept_y.tolist() == [0.5, 2]


def test_潜在変数の標本() -> None:
    x, y = latent()
    assert x.shape == y.shape == (20000,)
    fit = fit_ols(y, x)
    assert fit.coefficients.to_numpy() == pytest.approx([1.0, 2.0], abs=0.1)
    assert np.std(fit.residuals) == pytest.approx(2.0, abs=0.05)
    assert (censor(y) == 0).mean() == pytest.approx(0.36, abs=0.02)


def test_打ち切りがなければトービットはOLSと一致する() -> None:
    rng = np.random.default_rng(1)
    x = rng.standard_normal(300)
    y = 5 + 2 * x + rng.standard_normal(300)
    tobit = fit_tobit(y, x, left=-1000.0)
    ols = fit_ols(y, x)
    assert tobit.coefficients["const"] == pytest.approx(
        ols.coefficients["const"], abs=1e-4
    )
    assert tobit.coefficients["x1"] == pytest.approx(ols.coefficients["x1"], abs=1e-4)
    assert tobit.coefficients["sigma"] == pytest.approx(
        math.sqrt(ols.residuals @ ols.residuals / 300), abs=1e-4
    )


def test_係数の名前と標本の大きさ() -> None:
    x, y = latent(2000)
    fit = fit_tobit(censor(y), x)
    assert list(fit.coefficients.index) == ["const", "x1", "sigma"]
    assert list(fit.standard_errors.index) == ["const", "x1", "sigma"]
    assert fit.n_obs == 2000
    assert (fit.standard_errors > 0).all()


def test_最適点では対数尤度の勾配がほぼ0で周りより大きい() -> None:
    x, y = latent(3000)
    observed = censor(y)
    fit = fit_tobit(observed, x)
    design = np.column_stack([np.ones(3000), x])
    best = np.append(
        fit.coefficients.iloc[:-1].to_numpy(), np.log(fit.coefficients["sigma"])
    )
    assert fit.log_likelihood == pytest.approx(
        tobit_log_likelihood(best, observed, design, 0.0)
    )
    for direction in np.eye(3):
        for delta in (0.02, -0.02):
            moved = tobit_log_likelihood(
                best + delta * direction, observed, design, 0.0
            )
            assert moved < fit.log_likelihood
    step = 1e-5
    for i in range(3):
        e = np.eye(3)[i] * step
        gradient = (
            tobit_log_likelihood(best + e, observed, design, 0.0)
            - tobit_log_likelihood(best - e, observed, design, 0.0)
        ) / (2 * step)
        assert abs(gradient) / 3000 < 1e-4


def test_トービットは真の値を復元しOLSは0の方向に偏る() -> None:
    x, y = latent()
    observed = censor(y)
    tobit = fit_tobit(observed, x)
    truth = {"const": 1.0, "x1": 2.0, "sigma": 2.0}
    for name, value in truth.items():
        assert abs(tobit.coefficients[name] - value) < 4 * tobit.standard_errors[name]
    ols = fit_ols(observed, x).coefficients["x1"]
    assert ols < 1.5
    assert abs(ols - 2.0) > 0.5


def test_打ち切られていない観測値だけのOLSも偏る() -> None:
    x, y = latent()
    keep = y > 0
    assert fit_ols(y[keep], x[keep]).coefficients["x1"] < 1.5


def test_下限が0以外でもトービットは真の値を復元する() -> None:
    x, y = latent()
    fit = fit_tobit(censor(y, 2.0), x, left=2.0)
    assert abs(fit.coefficients["x1"] - 2.0) < 4 * fit.standard_errors["x1"]
    assert abs(fit.coefficients["const"] - 1.0) < 4 * fit.standard_errors["const"]


def test_切断回帰は真の値を復元しOLSは0の方向に偏る() -> None:
    x, y = latent()
    kept_x, kept_y = truncate(x, y)
    fit = fit_truncreg(kept_y, kept_x)
    truth = {"const": 1.0, "x1": 2.0, "sigma": 2.0}
    for name, value in truth.items():
        assert abs(fit.coefficients[name] - value) < 4 * fit.standard_errors[name]
    assert fit_ols(kept_y, kept_x).coefficients["x1"] < 1.5
    assert fit.n_obs == len(kept_y)


def test_標準誤差は推定値の実際のばらつきに近い() -> None:
    slopes, errors = [], []
    for seed in range(150):
        x, y = latent(500, seed)
        fit = fit_tobit(censor(y), x)
        slopes.append(fit.coefficients["x1"])
        errors.append(fit.standard_errors["x1"])
    assert np.mean(errors) == pytest.approx(np.std(slopes, ddof=1), rel=0.2)
    assert np.mean(slopes) == pytest.approx(2.0, abs=4 * np.std(slopes) / 150**0.5)


def test_期待値の平均は観測値の平均に近い() -> None:
    x, y = latent()
    observed = censor(y)
    fit = fit_tobit(observed, x)
    expected = tobit_expected_value(fit, x)
    assert expected.mean() == pytest.approx(observed.mean(), abs=0.05)
    assert (expected >= 0).all()


def test_限界効果は期待値の数値微分の平均に一致する() -> None:
    x, y = latent()
    fit = fit_tobit(censor(y), x)
    h = 1e-4
    numeric = np.mean(
        (tobit_expected_value(fit, x + h) - tobit_expected_value(fit, x - h)) / (2 * h)
    )
    effect = tobit_marginal_effects(fit, x)
    assert effect["x1"] == pytest.approx(numeric, rel=1e-4)
    assert 0 < effect["x1"] < fit.coefficients["x1"]


def test_複数の説明変数でも期待値と限界効果を求められる() -> None:
    rng = np.random.default_rng(3)
    x = rng.standard_normal((4000, 2))
    y = 1 + 2 * x[:, 0] - x[:, 1] + 2 * rng.standard_normal(4000)
    fit = fit_tobit(censor(y), x)
    assert list(fit.coefficients.index) == ["const", "x1", "x2", "sigma"]
    assert tobit_expected_value(fit, x).shape == (4000,)
    assert list(tobit_marginal_effects(fit, x).index) == ["x1", "x2"]


def test_最適化が収束しなければエラー(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_minimize(*args: object, **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(success=False, jac=np.array([1.0, 1.0, 1.0]), x=None)

    monkeypatch.setattr(limited.optimize, "minimize", fake_minimize)
    x, y = latent(200)
    with pytest.raises(ValueError, match="収束"):
        fit_tobit(censor(y), x)
