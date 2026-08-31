"""Phase 3b: are cross-paper reports independent measurements?

The as-mined analysis (03b) treats each reporting paper as one observation
of a (policy, benchmark) cell. That is only valid if papers evaluate rather
than quote. This script tests that assumption directly by looking for
repeated values, and replaces the range-based headline with a statistic
that does not depend on how many papers happen to report a cell:

  what share of reported numbers differ from their own cell's median by
  more than the median claimed improvement?

That is the question facing anyone who copies a baseline number out of the
literature, and unlike the range it does not inflate with cell popularity.

Outputs:
  independence.csv           per-cell distinct values, redundancy, modal share
  independence_headline.csv  corpus-level totals + the consumer statistic
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
sys.path.insert(0, str(ROOT / "robostats"))

from robostats import modal_share, n_distinct, redundancy  # noqa: E402

MIN_PAPERS = 5


def per_paper_cells() -> pd.DataFrame:
    df = pd.read_parquet(PROC / "results_clean.parquet")
    df = df[~df.suspect & df.score.notna()]
    base = df[df.is_base & (df.benchmark != "calvin")]
    pp = (
        base.groupby(["policy_id", "benchmark", "paper"], dropna=False)["score"]
        .median()
        .reset_index()
    )
    pp["cell"] = pp.policy_id + "/" + pp.benchmark
    return pp


def main() -> None:
    pp = per_paper_cells()
    counts = pp.groupby("cell")["score"].count()
    margin = float(
        pd.read_csv(PROC / "headline_stats.csv")
        .set_index("stat")
        .loc["margin_top1_top2", "median"]
    )

    rows = []
    for cell in counts[counts >= MIN_PAPERS].index:
        v = pp.loc[pp.cell == cell, "score"].to_numpy(float)
        med = float(np.median(v))
        rows.append({
            "cell": cell,
            "n_papers": v.size,
            "n_distinct": n_distinct(v),
            "redundancy": round(redundancy(v), 3),
            "modal_share": round(modal_share(v), 3),
            "all_identical": bool(n_distinct(v) == 1),
            "frac_off_median": round(float(np.mean(np.abs(v - med) > margin)), 3),
        })
    cells = pd.DataFrame(rows).sort_values("n_papers", ascending=False)
    cells.to_csv(PROC / "independence.csv", index=False)

    # pooled over every report, so big cells are not down-weighted to one row
    pooled = np.concatenate([
        np.abs(pp.loc[pp.cell == c, "score"].to_numpy(float)
               - np.median(pp.loc[pp.cell == c, "score"].to_numpy(float)))
        for c in cells.cell
    ])
    n_reports, n_values = int(cells.n_papers.sum()), int(cells.n_distinct.sum())

    # every cell with >=3 papers, to catch perfectly-copied small cells too
    wide = counts[counts >= 3].index
    identical3 = sum(
        n_distinct(pp.loc[pp.cell == c, "score"].to_numpy(float)) == 1 for c in wide
    )

    stats = [
        {"stat": "reports_in_popular_cells", "value": n_reports},
        {"stat": "distinct_values_in_popular_cells", "value": n_values},
        {"stat": "corpus_redundancy", "value": round(1 - n_values / n_reports, 3)},
        {"stat": "cells_all_identical_ge3papers", "value": identical3},
        {"stat": "cells_ge3papers", "value": len(wide)},
        {"stat": "median_modal_share", "value": round(float(cells.modal_share.median()), 3)},
        {"stat": "margin_used", "value": margin},
        {"stat": "frac_reports_off_median_gt_margin", "value": round(float(np.mean(pooled > margin)), 3)},
        {"stat": "frac_reports_off_median_gt_5pts", "value": round(float(np.mean(pooled > 5)), 3)},
        {"stat": "frac_reports_off_median_gt_10pts", "value": round(float(np.mean(pooled > 10)), 3)},
    ]
    pd.DataFrame(stats).to_csv(PROC / "independence_headline.csv", index=False)

    print(f"popular cells (>={MIN_PAPERS} papers): {len(cells)}")
    print(f"  {n_reports} paper-reports carry {n_values} distinct values "
          f"({100 * (1 - n_values / n_reports):.0f}% redundancy)")
    print(f"  median share of a cell held by its single most common value: "
          f"{100 * cells.modal_share.median():.0f}%")
    print(f"  cells (>=3 papers) where EVERY paper reports the identical value: "
          f"{identical3}/{len(wide)}")
    print(f"\nconsumer statistic (margin = {margin} pts, the median claimed improvement):")
    print(f"  {100 * np.mean(pooled > margin):.0f}% of reports differ from their cell median "
          f"by more than the median claimed improvement")
    print(f"  {100 * np.mean(pooled > 5):.0f}% differ by >5 pts; "
          f"{100 * np.mean(pooled > 10):.0f}% by >10 pts")


if __name__ == "__main__":
    main()
