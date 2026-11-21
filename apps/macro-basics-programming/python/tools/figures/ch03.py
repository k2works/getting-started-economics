"""第 3 章の図の登録。"""

from collections.abc import Callable
from pathlib import Path

import pandas as pd
from matplotlib.figure import Figure

from lib.chapter03.indicators import (
    composite_index,
    diffusion_index,
    load_indicators,
)
from lib.chapter03.plot import plot_business_indexes, plot_price_indexes
from lib.chapter03.price_index import price_indexes

# data/ は、tools/ の 1 つ上（アプリの直下）にある
_INDICATORS = load_indicators(
    Path(__file__).resolve().parents[2] / "data" / "ch03_indicators.csv"
)

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch03-price-indexes": lambda: plot_price_indexes(
        price_indexes(
            pd.DataFrame(
                {"bread": [100, 110, 121], "milk": [200, 180, 170]},
                index=["2020", "2021", "2022"],
            ),
            pd.DataFrame(
                {"bread": [10, 12, 14], "milk": [5, 4, 3]},
                index=["2020", "2021", "2022"],
            ),
            base="2020",
        )
    ),
    "ch03-business-indexes": lambda: plot_business_indexes(
        diffusion_index(_INDICATORS), composite_index(_INDICATORS, base="2025-01")
    ),
}
