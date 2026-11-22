"""サイコロを、乱数で何度も投げる（種を固定して、毎回同じ結果にする）。"""

import random
from collections import Counter


def simulate_dice_sum_frequencies(
    trials: int, seed: int, dice: int = 2, faces: int = 6
) -> dict[int, float]:
    """サイコロ dice 個を trials 回投げ、目の和ごとの相対頻度（回数 ÷ 投げた回数）。"""
    if trials < 1:
        raise ValueError("投げる回数は、1 以上でなければなりません")
    rng = random.Random(seed)
    counts = Counter(
        sum(rng.randint(1, faces) for _ in range(dice)) for _ in range(trials)
    )
    return {s: counts[s] / trials for s in range(dice, dice * faces + 1)}
