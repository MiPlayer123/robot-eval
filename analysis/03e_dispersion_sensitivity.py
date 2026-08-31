"""Phase 3c: is the headline an artefact of the dispersion statistic?

Two questions a reviewer will ask about the as-mined result, answered here
rather than left open:

  1. "Spread grows with popularity" -- the range of n samples grows with n
     even at fixed dispersion, so the reported Spearman(n, spread) has to be
     compared against a null in which no popularity effect exists at all.
     The null draws n values per cell from ONE common distribution.

  2. "Why the range?" -- the ratio of cell dispersion to claimed margin is
     recomputed under range, SD, IQR and MAD, so the reader can see how much
     of the headline rests on that choice.

Outputs:
  dispersion_sensitivity.csv  median dispersion + ratio to margin, per statistic
  spread_popularity_null.csv  observed vs null Spearman(n, statistic)
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
sys.path.insert(0, str(ROOT / "robostats"))

from robostats import dispersion  # noqa: E402

SEED, NULL_DRAWS, BOOT = 7, 2000, 20000
STATS = ("spread", "sd", "iqr", "mad")


def per_paper_cells() -> pd.DataFrame:
    df = pd.read_parquet(PROC / "results_clean.parquet")
    df = df[~df.suspect & df.score.notna()]
    base = df[df.is_base & (df.benchmark != "calvin")]
    pp = (base.groupby(["policy_id", "benchmark", "paper"], dropna=False)["score"]
          .median().reset_index())
    pp["cell"] = pp.policy_id + "/" + pp.benchmark
    return pp


def cell_table(pp: pd.DataFrame, min_papers: int) -> pd.DataFrame:
    rows = []
    for cell, g in pp.groupby("cell"):
        v = g.score.to_numpy(float)
        if v.size < min_papers:
            continue
        rows.append({"cell": cell, **dispersion(v)})
    return pd.DataFrame(rows)


def med_ci(x, rng) -> tuple[float, float, float]:
    x = np.asarray(x, float)
    meds = np.median(rng.choice(x, (BOOT, x.size)), axis=1)
    return float(np.median(x)), *map(float, np.percentile(meds, [2.5, 97.5]))


def main() -> None:
    rng = np.random.default_rng(SEED)
    pp = per_paper_cells()
    c5, c3 = cell_table(pp, 5), cell_table(pp, 3)
    head = pd.read_csv(PROC / "headline_stats.csv").set_index("stat")
    margin = float(head.loc["margin_vs_other_policy", "median"])

    rows = []
    for s in STATS:
        m, lo, hi = med_ci(c5[s].values, rng)
        rows.append({"statistic": s, "n_cells": len(c5), "median": round(m, 2),
                     "ci_lo": round(lo, 2), "ci_hi": round(hi, 2),
                     "ratio_to_margin": round(m / margin, 2)})
        print(f"  {s:6s}: median {m:5.1f} [{lo:.1f}, {hi:.1f}]  "
              f"= {m / margin:4.1f}x the {margin}-pt robust claimed margin")
    pd.DataFrame(rows).to_csv(PROC / "dispersion_sensitivity.csv", index=False)

    print("\nSpearman(n_papers, dispersion) vs a null with NO popularity effect:")
    null_rows = []
    n_vec = c3["n"].to_numpy(int)
    for s in STATS:
        obs = float(stats.spearmanr(n_vec, c3[s].to_numpy(float)).statistic)
        draws = np.array([
            stats.spearmanr(n_vec, [dispersion(rng.normal(0, 1, int(n)))[s]
                                    for n in n_vec]).statistic
            for _ in range(NULL_DRAWS)
        ])
        lo, hi = np.percentile(draws, [2.5, 97.5])
        inside = bool(lo <= obs <= hi)
        null_rows.append({"statistic": s, "observed": round(obs, 3),
                          "null_median": round(float(np.median(draws)), 3),
                          "null_lo": round(float(lo), 3), "null_hi": round(float(hi), 3),
                          "inside_null": inside})
        verdict = "INSIDE null -> no evidence" if inside else "outside null -> real"
        print(f"  {s:6s}: observed {obs:+.3f} | null {np.median(draws):+.3f} "
              f"[{lo:+.3f}, {hi:+.3f}] -> {verdict}")
    pd.DataFrame(null_rows).to_csv(PROC / "spread_popularity_null.csv", index=False)


if __name__ == "__main__":
    main()
