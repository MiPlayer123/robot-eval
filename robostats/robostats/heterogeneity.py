"""Between-report heterogeneity for scores mined from papers.

Scores reported in the literature are not independent measurements: papers
quote one another, so a cell with 28 reporting papers may carry only a
handful of distinct values. These helpers make that visible, and give
dispersion summaries that do not inflate with the number of reporting
papers the way the range does.

The range of n samples grows with n even when the underlying dispersion is
fixed, so ``spread`` is reported here only alongside statistics that do
not share that defect.
"""
from __future__ import annotations

import numpy as np
from scipy import stats

__all__ = [
    "prediction_interval",
    "redundancy",
    "modal_share",
    "n_distinct",
    "dispersion",
]


def _clean(x) -> np.ndarray:
    a = np.asarray(x, dtype=float)
    a = a[np.isfinite(a)]
    if a.size == 0:
        raise ValueError("no finite values")
    return a


def prediction_interval(x, conf: float = 0.95) -> tuple[float, float]:
    """Interval for where a NEW report of the same quantity would land.

    Unlike a confidence interval on the mean, this answers the question a
    reader copying a baseline number actually has. Requires n >= 3.
    """
    a = _clean(x)
    n = a.size
    if n < 3:
        raise ValueError(f"prediction interval needs n >= 3, got {n}")
    if not 0 < conf < 1:
        raise ValueError("conf must be in (0, 1)")
    half = stats.t.ppf(0.5 + conf / 2, n - 1) * a.std(ddof=1) * np.sqrt(1 + 1 / n)
    m = a.mean()
    return float(m - half), float(m + half)


def redundancy(x) -> float:
    """Share of reports that repeat a value another report already gave.

    0.0 means every report is a distinct number; values near 1 mean the
    reports are overwhelmingly quotations of each other.
    """
    a = _clean(x)
    return float(1.0 - np.unique(a).size / a.size)


def modal_share(x) -> float:
    """Share of reports sitting on the single most common value."""
    a = _clean(x)
    _, counts = np.unique(a, return_counts=True)
    return float(counts.max() / a.size)


def n_distinct(x) -> int:
    """Number of distinct reported values."""
    return int(np.unique(_clean(x)).size)


def dispersion(x) -> dict:
    """Dispersion summarised several ways, so no single choice is load-bearing.

    ``spread`` (max - min) is included for continuity with earlier reporting
    but inflates with n; prefer ``sd``, ``iqr`` or ``mad`` for comparisons
    across cells with different numbers of reporting papers.
    """
    a = _clean(x)
    q75, q25 = np.percentile(a, [75, 25])
    return {
        "n": int(a.size),
        "n_distinct": n_distinct(a),
        "spread": float(a.max() - a.min()),
        "sd": float(a.std(ddof=1)) if a.size > 1 else 0.0,
        "iqr": float(q75 - q25),
        "mad": float(np.median(np.abs(a - np.median(a)))),
    }
