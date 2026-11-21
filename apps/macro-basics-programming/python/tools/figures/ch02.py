"""第 2 章の図の登録。"""

from collections.abc import Callable

from matplotlib.figure import Figure

from lib.chapter02.plot import plot_io_output, plot_three_way

FIGURES: dict[str, Callable[[], Figure]] = {
    "ch02-three-way": lambda: plot_three_way(
        {
            "Production": {"Industry A": 100, "Industry B": 200, "Industry C": 200},
            "Distribution": {
                "Compensation": 280,
                "Operating surplus": 120,
                "Depreciation": 80,
                "Taxes less subsidies": 20,
            },
            "Expenditure": {
                "Consumption": 290,
                "Government": 80,
                "Investment": 100,
                "Inventory": 10,
                "Net exports": 20,
            },
        }
    ),
    "ch02-io-output": lambda: plot_io_output(
        [[0.2, 0.3], [0.4, 0.1]], [100, 200], ["Manufacturing", "Services"]
    ),
}
