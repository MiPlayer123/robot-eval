"""Confidence intervals for robot policy evaluation.

Success rates from rollout trials are binomial proportions estimated from
small N. These helpers make the uncertainty explicit. Clopper-Pearson is
the conservative default (guaranteed coverage); Wilson is the tighter
choice for reporting; Jeffreys is the Bayesian middle ground.

All functions return (low, high) on the success-rate scale [0, 1].
"""
from __future__ import annotations

import math

from scipy import stats


def clopper_pearson(successes: int, trials: int, conf: float = 0.95) -> tuple[float, float]:
    """Exact (conservative) binomial CI. Guaranteed >= conf coverage."""
    _check(successes, trials)
    alpha = 1.0 - conf
    lo = 0.0 if successes == 0 else stats.beta.ppf(alpha / 2, successes, trials - successes + 1)
    hi = 1.0 if successes == trials else stats.beta.ppf(1 - alpha / 2, successes + 1, trials - successes)
    return float(lo), float(hi)


def wilson(successes: int, trials: int, conf: float = 0.95) -> tuple[float, float]:
    """Wilson score interval. Good coverage, tighter than Clopper-Pearson."""
    _check(successes, trials)
    z = stats.norm.ppf(1 - (1 - conf) / 2)
    p = successes / trials
    denom = 1 + z**2 / trials
    center = (p + z**2 / (2 * trials)) / denom
    half = z * math.sqrt(p * (1 - p) / trials + z**2 / (4 * trials**2)) / denom
    return max(0.0, center - half), min(1.0, center + half)


def jeffreys(successes: int, trials: int, conf: float = 0.95) -> tuple[float, float]:
    """Jeffreys prior (Beta(1/2, 1/2)) equal-tailed credible interval."""
    _check(successes, trials)
    alpha = 1.0 - conf
    a, b = successes + 0.5, trials - successes + 0.5
    lo = 0.0 if successes == 0 else stats.beta.ppf(alpha / 2, a, b)
    hi = 1.0 if successes == trials else stats.beta.ppf(1 - alpha / 2, a, b)
    return float(lo), float(hi)


def cluster_robust(successes_per_cluster: list[int], trials_per_cluster: list[int], conf: float = 0.95) -> tuple[float, float]:
    """CI for a success rate when rollouts are clustered (e.g. by initial
    condition, scene, or session) and therefore not independent.

    Uses the cluster-level ratio estimator with a t-interval over cluster
    proportions weighted by cluster size. With one cluster this degrades
    to a degenerate interval; callers should require >= 2 clusters.
    """
    if len(successes_per_cluster) != len(trials_per_cluster):
        raise ValueError("cluster lists must align")
    k = len(trials_per_cluster)
    if k < 2:
        raise ValueError("need >= 2 clusters for a cluster-robust interval")
    n = sum(trials_per_cluster)
    p_hat = sum(successes_per_cluster) / n
    # weighted cluster residual variance (ratio estimator, standard survey form)
    resid_sq = [
        (s - p_hat * t) ** 2 for s, t in zip(successes_per_cluster, trials_per_cluster)
    ]
    var = k / (k - 1) * sum(resid_sq) / n**2
    half = stats.t.ppf(1 - (1 - conf) / 2, df=k - 1) * math.sqrt(var)
    return max(0.0, p_hat - half), min(1.0, p_hat + half)


def _check(successes: int, trials: int) -> None:
    if trials <= 0:
        raise ValueError("trials must be positive")
    if not 0 <= successes <= trials:
        raise ValueError("successes must be within [0, trials]")
