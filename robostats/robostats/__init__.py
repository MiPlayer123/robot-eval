"""robostats: honest statistics for robot policy evaluation.

Permissively licensed (MIT) implementations of the statistical practices
the robot-learning eval literature recommends but no harness enforces:
binomial CIs, cluster-robust intervals, rank agreement with uncertainty,
pairwise ordering agreement, and power analysis for eval design.

Method sources are cited in each module; this library is an engineering
integration of published methods, not a claim of statistical novelty.
"""
from .intervals import clopper_pearson, cluster_robust, jeffreys, wilson
from .power import min_detectable_gap, trials_for_ci_halfwidth, trials_to_separate
from .rank import kendall_ci, pairwise_ordering_agreement, spearman_ci

__version__ = "0.0.1"
__all__ = [
    "clopper_pearson",
    "wilson",
    "jeffreys",
    "cluster_robust",
    "spearman_ci",
    "kendall_ci",
    "pairwise_ordering_agreement",
    "trials_for_ci_halfwidth",
    "trials_to_separate",
    "min_detectable_gap",
]
