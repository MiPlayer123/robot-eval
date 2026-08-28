"""Rank agreement with honest uncertainty.

Concordance between two evaluations (two benchmarks, or sim vs. real) is
usually reported as a bare Spearman rho over a handful of policies. With
n <= 10 items that number is close to meaningless without an interval.
These helpers bootstrap the interval and offer the cell-level pairwise
ordering-agreement statistic that stays estimable at small n.
"""
from __future__ import annotations

import numpy as np
from scipy import stats


def spearman_ci(
    x: np.ndarray,
    y: np.ndarray,
    conf: float = 0.95,
    n_boot: int = 10_000,
    seed: int | None = 0,
) -> tuple[float, float, float]:
    """Spearman rho with a bootstrap percentile CI. Returns (rho, lo, hi).

    Warning printed into the result rather than hidden: with n < 8 the
    interval will typically span most of [-1, 1]; that is the point.
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.shape != y.shape or x.ndim != 1:
        raise ValueError("x and y must be 1-d and aligned")
    n = len(x)
    if n < 4:
        raise ValueError("need >= 4 items")
    rho = float(stats.spearmanr(x, y).statistic)
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        if len(np.unique(idx)) < 3:
            boots[i] = np.nan
            continue
        boots[i] = stats.spearmanr(x[idx], y[idx]).statistic
    boots = boots[~np.isnan(boots)]
    alpha = 1 - conf
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return rho, float(lo), float(hi)


def kendall_ci(
    x: np.ndarray,
    y: np.ndarray,
    conf: float = 0.95,
    n_boot: int = 10_000,
    seed: int | None = 0,
) -> tuple[float, float, float]:
    """Kendall tau-b with bootstrap percentile CI. Returns (tau, lo, hi)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    if n < 4:
        raise ValueError("need >= 4 items")
    tau = float(stats.kendalltau(x, y).statistic)
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        boots[i] = stats.kendalltau(x[idx], y[idx]).statistic
    boots = boots[~np.isnan(boots)]
    alpha = 1 - conf
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return tau, float(lo), float(hi)


def pairwise_ordering_agreement(
    a_success: np.ndarray,
    a_trials: np.ndarray,
    b_success: np.ndarray,
    b_trials: np.ndarray,
    min_sep_prob: float = 0.9,
) -> dict:
    """Cell-level agreement between two evaluations (e.g. sim and real).

    Items are policy-task cells with binomial outcomes in both settings.
    For every pair of cells, ask: do the two evaluations agree on which
    cell is better? Pairs are only counted when both evaluations separate
    the pair decisively (posterior P(p_i > p_j) >= min_sep_prob under
    Jeffreys posteriors), so ties/noise do not masquerade as signal.

    Returns dict with counts: decisive_pairs, agreements, agreement_rate,
    and total_pairs for context.
    """
    a_s, a_t = np.asarray(a_success), np.asarray(a_trials)
    b_s, b_t = np.asarray(b_success), np.asarray(b_trials)
    n = len(a_s)
    if not (len(a_t) == len(b_s) == len(b_t) == n):
        raise ValueError("all arrays must align")
    rng = np.random.default_rng(0)
    draws = 4000
    post_a = rng.beta(a_s[:, None] + 0.5, (a_t - a_s)[:, None] + 0.5, (n, draws))
    post_b = rng.beta(b_s[:, None] + 0.5, (b_t - b_s)[:, None] + 0.5, (n, draws))

    total = decisive = agree = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += 1
            pa = (post_a[i] > post_a[j]).mean()
            pb = (post_b[i] > post_b[j]).mean()
            a_dec = pa >= min_sep_prob or pa <= 1 - min_sep_prob
            b_dec = pb >= min_sep_prob or pb <= 1 - min_sep_prob
            if a_dec and b_dec:
                decisive += 1
                if (pa > 0.5) == (pb > 0.5):
                    agree += 1
    return {
        "total_pairs": total,
        "decisive_pairs": decisive,
        "agreements": agree,
        "agreement_rate": agree / decisive if decisive else float("nan"),
    }
