"""Statistical utilities. Wilson score interval for a binomial proportion."""

import math


def wilson_ci(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Return (low, high) 95% Wilson interval as fractions in [0, 1].

    Preferred over the normal-approximation Wald interval for small n
    and for proportions near 0 or 1 (as in our 0/23 cases).
    """
    if total == 0:
        return (0.0, 0.0)
    p = successes / total
    denom = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denom
    half = z * math.sqrt((p * (1 - p) / total + z * z / (4 * total * total))) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def fmt_ci(successes: int, total: int) -> str:
    lo, hi = wilson_ci(successes, total)
    return "{:.1f}-{:.1f}%".format(lo * 100, hi * 100)
