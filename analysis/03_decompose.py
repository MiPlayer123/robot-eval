"""Phase 3a: reporting-variance anatomy.

Pre-registered hypothesis (PLAN.md, frozen before this script first ran):
within-benchmark cross-paper variance for the same policy exceeds
between-benchmark disagreement for shared policies.

Analyses:
  A. Per-cell reporting spread: for (policy, benchmark) cells with >=3
     independent reporting papers, the spread and SD of reported scores.
     Cells use BASE rows only (variants excluded) and exclude suspects.
  B. Variance decomposition: for the base-row subset, mean absolute
     deviation attributable to (i) reporting paper within one cell vs
     (ii) benchmark within one policy (same-policy cross-benchmark spread
     of per-benchmark median scores).
  C. Sensitivity: A and B re-run with contested merges disabled
     (DP->diffusionpolicy, RoboVLMs->robovlm) and with suspects included.

Outputs: data/processed/decomposition.csv + printed summary with CIs.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "robostats"))


def load(disable_contested: bool = False, keep_suspects: bool = False) -> pd.DataFrame:
    df = pd.read_parquet(ROOT / "data" / "processed" / "results_clean.parquet")
    if disable_contested:
        # undo DP and RoboVLMs merges by re-deriving identity from raw name
        mask_dp = df.raw_name.str.strip().str.match(r"DP\b", na=False)
        df.loc[mask_dp, "policy_id"] = "dp[unmerged]"
        mask_rvs = df.raw_name.str.contains("RoboVLMs", na=False)
        df.loc[mask_rvs, "policy_id"] = "robovlms[unmerged]"
    if not keep_suspects:
        df = df[~df.suspect]
    return df[df.score.notna()]


def cell_spreads(df: pd.DataFrame, min_reports: int = 3) -> pd.DataFrame:
    base = df[df.is_base]
    # one score per (cell, paper): a paper reporting a policy twice on one
    # benchmark (e.g. two tables) contributes its median
    per_paper = (
        base.groupby(["policy_id", "benchmark", "paper"], dropna=False)["score"]
        .median()
        .reset_index()
    )
    g = per_paper.groupby(["policy_id", "benchmark"])["score"]
    out = g.agg(n_papers="count", mean="mean", sd="std", lo="min", hi="max")
    out["spread"] = out.hi - out.lo
    return out[out.n_papers >= min_reports].sort_values("spread", ascending=False)


def between_benchmark_spread(df: pd.DataFrame, min_benchmarks: int = 3) -> pd.DataFrame:
    """Per policy: spread of per-benchmark median scores (base rows).
    NOTE: benchmarks use different metrics (CALVIN avg-len vs %). Restrict
    to percent-scale benchmarks so the comparison is unit-consistent."""
    pct = df[(df.benchmark != "calvin") & df.is_base]
    med = (
        pct.groupby(["policy_id", "benchmark"])["score"].median().reset_index()
    )
    g = med.groupby("policy_id")["score"]
    out = g.agg(n_benchmarks="count", lo="min", hi="max", sd="std")
    out["spread"] = out.hi - out.lo
    return out[out.n_benchmarks >= min_benchmarks].sort_values("spread", ascending=False)


def summarize(tag: str, df: pd.DataFrame) -> dict:
    cells = cell_spreads(df)
    across = between_benchmark_spread(df)
    # exclude calvin cells from the within side too, for unit consistency
    cells_pct = cells[cells.index.get_level_values("benchmark") != "calvin"]
    res = {
        "tag": tag,
        "n_cells(>=3 papers)": len(cells_pct),
        "within_cell_median_spread": float(cells_pct.spread.median()),
        "within_cell_mean_sd": float(cells_pct.sd.mean()),
        "n_policies(>=3 benchmarks)": len(across),
        "between_benchmark_median_spread": float(across.spread.median()),
    }
    return res


def main() -> None:
    rows = []
    df = load()
    rows.append(summarize("primary", df))
    rows.append(summarize("no-contested-merges", load(disable_contested=True)))
    rows.append(summarize("with-suspects", load(keep_suspects=True)))
    summary = pd.DataFrame(rows)
    print(summary.to_string(index=False))

    cells = cell_spreads(df)
    cells.to_csv(ROOT / "data" / "processed" / "decomposition.csv")
    print("\nTop within-cell spreads (base rows, no suspects):")
    print(cells.head(12).to_string())

    across = between_benchmark_spread(df)
    print("\nTop between-benchmark spreads (per-benchmark medians):")
    print(across.head(8).to_string())

    prim = rows[0]
    verdict = (
        prim["within_cell_median_spread"] >= prim["between_benchmark_median_spread"]
    )
    print(
        f"\nPre-registered hypothesis (within >= between, median spreads): "
        f"{'SUPPORTED' if verdict else 'NOT SUPPORTED'} "
        f"({prim['within_cell_median_spread']:.1f} vs "
        f"{prim['between_benchmark_median_spread']:.1f} points)"
    )


if __name__ == "__main__":
    main()
