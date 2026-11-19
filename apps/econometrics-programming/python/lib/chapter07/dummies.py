"""ダミー変数・カテゴリー変数・交差項。"""

import numpy as np
import pandas as pd

# 地域の効果（基準は north）
REGION_EFFECTS = {"north": 0.0, "south": -0.1, "west": 0.15}


def group_means(y: pd.Series, groups: pd.Series) -> pd.Series:
    """グループごとの平均。"""
    return y.groupby(groups).mean()


def make_dummies(values: pd.Series, base: str | None = None) -> pd.DataFrame:
    """カテゴリー変数から、ダミー変数（0 と 1）を作る。基準のカテゴリーは除く。

    基準を指定しなければ、小さい順で最初のカテゴリーを基準にする。
    """
    levels = sorted(values.unique())
    reference = levels[0] if base is None else base
    if reference not in levels:
        raise ValueError(f"基準のカテゴリー {reference!r} が、データにない")
    prefix = "d" if values.name is None else str(values.name)
    return pd.DataFrame(
        {
            f"{prefix}_{level}": (values == level).astype(float)
            for level in levels
            if level != reference
        },
        index=values.index,
    )


def has_dummy_trap(x: pd.DataFrame, constant: bool = True) -> bool:
    """ダミー変数の罠: 定数項があり、ダミー変数が全カテゴリー分そろっているか。

    すべてのダミー変数の和が、どの行でも 1（定数項と同じ）になると、推定できない。
    """
    return constant and bool((x.sum(axis=1) == 1).all())


def with_interaction(x: pd.Series, d: pd.Series) -> pd.Series:
    """交差項（2 つの変数の積）。"""
    product = x * d
    product.name = f"{x.name}:{d.name}"
    return product


def draw_wage_sample(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """対数賃金・教育年数・女性ダミー・地域の標本を、母集団の式から作る。

    lwage = 1 + 0.08·educ − 0.25·female + 0.02·educ·female + 地域の効果 + 0.3·u
    """
    educ = rng.integers(8, 19, n)
    female = rng.integers(0, 2, n)
    region = rng.choice(list(REGION_EFFECTS), n)
    effect = np.array([REGION_EFFECTS[r] for r in region])
    u = rng.standard_normal(n)
    lwage = 1 + 0.08 * educ - 0.25 * female + 0.02 * educ * female + effect + 0.3 * u
    return pd.DataFrame(
        {"lwage": lwage, "educ": educ, "female": female, "region": region}
    )
