"""Power analysis for eval design: how many rollouts before you can claim
anything. Used to design part 3 before data collection and to critique
reported results in part 1.
"""
from __future__ import annotations

import math

from scipy import stats


def trials_for_ci_halfwidth(p: float, halfwidth: float, conf: float = 0.95) -> int:
    """Trials needed so a Wald-approx CI on a success rate p has the given
    half-width. Conservative choice: use p=0.5 when p unknown."""
    if not 0 < p < 1:
        raise ValueError("p in (0,1)")
    z = stats.norm.ppf(1 - (1 - conf) / 2)
    return math.ceil(z**2 * p * (1 - p) / halfwidth**2)


def trials_to_separate(
    p1: float, p2: float, power: float = 0.8, alpha: float = 0.05, two_sided: bool = True
) -> int:
    """Trials per policy for a two-proportion z-test to detect p1 vs p2.

    Sanity anchor: p1=0.50 vs p2=0.58 at 75% power, one-sided, ~ 417/arm,
    matching the STEP paper's "~400 trials for an 8pp gap" example (the
    STEP figure is one-sided; the two-sided requirement is ~538).
    """
    if not (0 < p1 < 1 and 0 < p2 < 1) or p1 == p2:
        raise ValueError("need distinct p1, p2 in (0,1)")
    za = stats.norm.ppf(1 - alpha / 2) if two_sided else stats.norm.ppf(1 - alpha)
    zb = stats.norm.ppf(power)
    pbar = (p1 + p2) / 2
    num = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / (p1 - p2) ** 2)


def min_detectable_gap(trials: int, p_base: float = 0.5, power: float = 0.8, alpha: float = 0.05) -> float:
    """Smallest success-rate gap detectable with the given per-policy trial
    budget. Solved by bisection over trials_to_separate."""
    lo, hi = 1e-4, 1 - p_base - 1e-4
    for _ in range(60):
        mid = (lo + hi) / 2
        if trials_to_separate(p_base, p_base + mid, power, alpha) > trials:
            lo = mid
        else:
            hi = mid
    return hi
