import math

import numpy as np
import pytest

from robostats import (
    clopper_pearson,
    cluster_robust,
    jeffreys,
    kendall_ci,
    min_detectable_gap,
    pairwise_ordering_agreement,
    spearman_ci,
    trials_for_ci_halfwidth,
    trials_to_separate,
    wilson,
)


# ---------- intervals ----------

def test_clopper_pearson_known_value():
    # 63/70 successes: NVIDIA's blog example — 90% point estimate,
    # 95% CI roughly (0.805, 0.959)
    lo, hi = clopper_pearson(63, 70)
    assert 0.79 < lo < 0.82
    assert 0.95 < hi < 0.97


def test_interval_orderings():
    for f in (clopper_pearson, wilson, jeffreys):
        lo, hi = f(15, 30)
        assert 0 <= lo < 0.5 < hi <= 1


def test_edge_cases():
    assert clopper_pearson(0, 20)[0] == 0.0
    assert clopper_pearson(20, 20)[1] == 1.0
    with pytest.raises(ValueError):
        clopper_pearson(5, 0)
    with pytest.raises(ValueError):
        clopper_pearson(6, 5)


def test_wilson_tighter_than_cp():
    cp = clopper_pearson(15, 30)
    wi = wilson(15, 30)
    assert (wi[1] - wi[0]) <= (cp[1] - cp[0]) + 1e-9


def test_cluster_robust_widens_under_clustering():
    # Heterogeneous clusters -> wider than pooled binomial CI
    succ = [10, 2, 9, 1]
    tri = [10, 10, 10, 10]
    lo, hi = cluster_robust(succ, tri)
    plo, phi = clopper_pearson(sum(succ), sum(tri))
    assert (hi - lo) > (phi - plo)
    with pytest.raises(ValueError):
        cluster_robust([5], [10])


# ---------- rank ----------

def test_spearman_small_n_interval_is_wide():
    rng = np.random.default_rng(1)
    x = rng.random(6)
    y = x + rng.normal(0, 0.3, 6)  # moderate correlation, realistic case
    rho, lo, hi = spearman_ci(x, y, n_boot=2000)
    assert rho > 0.3
    assert hi - lo > 0.4  # the honest-uncertainty point: n=6 is wide


def test_spearman_large_n_tightens():
    rng = np.random.default_rng(2)
    x = rng.random(80)
    y = x + rng.normal(0, 0.1, 80)
    rho, lo, hi = spearman_ci(x, y, n_boot=2000)
    assert hi - lo < 0.35


def test_kendall_runs():
    tau, lo, hi = kendall_ci(np.arange(10), np.arange(10) + np.random.default_rng(0).normal(0, 0.1, 10), n_boot=500)
    assert tau > 0.7
    assert lo <= tau <= hi


def test_pairwise_agreement_perfect_and_noise():
    trials = np.full(8, 50)
    strong = np.array([2, 8, 14, 20, 28, 34, 42, 48])
    res = pairwise_ordering_agreement(strong, trials, strong, trials)
    assert res["decisive_pairs"] > 0
    assert res["agreement_rate"] == 1.0

    # identical mediocre cells: nothing should be decisive
    flat = np.full(8, 25)
    res2 = pairwise_ordering_agreement(flat, trials, flat, trials)
    assert res2["decisive_pairs"] == 0
    assert math.isnan(res2["agreement_rate"])


# ---------- power ----------

def test_step_anchor():
    # STEP paper anchor: ~400 trials (one-sided) to separate an 8pp gap
    # at 75% power; two-sided is ~538
    n1 = trials_to_separate(0.50, 0.58, power=0.75, two_sided=False)
    assert 380 < n1 < 460
    n2 = trials_to_separate(0.50, 0.58, power=0.75)
    assert 500 < n2 < 580


def test_halfwidth():
    # +/-2pp at p=0.5 requires ~2,400 trials (Wald); NVIDIA's ~1,030 for
    # +/-2pp used a different criterion, so just check monotonicity + scale
    n2 = trials_for_ci_halfwidth(0.5, 0.02)
    n5 = trials_for_ci_halfwidth(0.5, 0.05)
    assert n2 > n5 > 100


def test_min_detectable_gap_matches_inverse():
    gap = min_detectable_gap(trials=400, p_base=0.5, power=0.75)
    assert 0.06 < gap < 0.10  # inverse of the STEP anchor
