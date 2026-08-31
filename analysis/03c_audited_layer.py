"""Phase 3a'': the audited layer, scripted.

Applies the extreme-value audit verdicts (extreme_audit_corrections.csv)
to the per-paper cell table and recomputes reporting spreads, so the
paper's audited numbers (6.9 overall, 13.8 top-10) reproduce from one
command and carry bootstrap CIs like every other headline number.

Outputs:
  extreme_audit_effect.csv   per-cell raw vs audited spread, with a flag
                             when an audited endpoint comes from a paper
                             the audit did not cover
  audited_headline.csv       medians + bootstrap CIs, raw vs audited
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"


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


def apply_audit(pp: pd.DataFrame) -> tuple[pd.DataFrame, set]:
    corr = pd.read_csv(PROC / "extreme_audit_corrections.csv", dtype={"paper_id": str})
    pp = pp.copy()
    audited_rows = set()
    drop_idx = []
    for _, c in corr.iterrows():
        m = (pp.cell == c.cell) & pp.paper.astype(str).str.contains(str(c.paper_id), na=False)
        if not m.any():
            raise RuntimeError(f"correction has no matching row: {c.cell} {c.paper_id}")
        audited_rows.update(pp[m].index)
        if c.action == "drop":
            drop_idx += list(pp[m].index)
        elif c.action == "correct":
            pp.loc[m, "score"] = float(c.score)
    return pp.drop(index=drop_idx), audited_rows


def spreads(pp: pd.DataFrame, min_papers: int = 5) -> pd.DataFrame:
    g = pp.groupby("cell")["score"].agg(n="count", lo="min", hi="max")
    g["spread"] = g.hi - g.lo
    return g[g.n >= min_papers]


def med_ci(x: np.ndarray, seed: int = 7, n: int = 20000) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    meds = np.median(rng.choice(x, (n, len(x))), axis=1)
    return float(np.median(x)), *map(float, np.percentile(meds, [2.5, 97.5]))


def main() -> None:
    pp_raw = per_paper_cells()
    pp_aud, audited_rows = apply_audit(pp_raw)
    corr = pd.read_csv(PROC / "extreme_audit_corrections.csv")
    targets = list(corr.cell.unique())

    raw = spreads(pp_raw, 1)
    aud = spreads(pp_aud, 1)
    rows = []
    for c in targets:
        r, a = raw.loc[c], aud.loc[c]
        cell_rows = pp_aud[pp_aud.cell == c]
        hi_row = cell_rows[cell_rows.score == a.hi].index
        lo_row = cell_rows[cell_rows.score == a.lo].index
        rows.append({
            "cell": c, "raw_spread": round(r.spread, 1),
            "aud_spread": round(a.spread, 1),
            "aud_lo": a.lo, "aud_hi": a.hi, "aud_n": int(a.n),
            # endpoint provenance: was the surviving extreme itself audited?
            "hi_audited": bool(set(hi_row) & audited_rows),
            "lo_audited": bool(set(lo_row) & audited_rows),
        })
    effect = pd.DataFrame(rows)
    effect.to_csv(PROC / "extreme_audit_effect.csv", index=False)

    raw5, aud5 = spreads(pp_raw, 5), spreads(pp_aud, 5)
    stats = []
    for tag, arr in [("raw_ge5", raw5.spread.values),
                     ("audited_ge5", aud5.spread.values),
                     ("raw_top10", effect.raw_spread.values),
                     ("audited_top10", effect.aud_spread.values)]:
        m, lo, hi = med_ci(np.asarray(arr, float))
        stats.append({"stat": tag, "n": len(arr), "median": round(m, 2),
                      "ci_lo": round(lo, 2), "ci_hi": round(hi, 2)})
        print(f"{tag}: n={len(arr)} median={m:.1f} [{lo:.1f}, {hi:.1f}]")
    pd.DataFrame(stats).to_csv(PROC / "audited_headline.csv", index=False)

    unaudited_ends = effect[~effect.hi_audited | ~effect.lo_audited]
    if len(unaudited_ends):
        print("\ncells whose surviving extreme was NOT itself audited "
              "(limitation; listed in the paper):")
        for _, r in unaudited_ends.iterrows():
            side = []
            if not r.lo_audited: side.append(f"lo={r.aud_lo}")
            if not r.hi_audited: side.append(f"hi={r.aud_hi}")
            print(f"  {r.cell}: {', '.join(side)}")


if __name__ == "__main__":
    main()
