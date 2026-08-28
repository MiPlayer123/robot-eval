"""Audit of the AI2 vla-evaluation-harness leaderboard corpus.

Verifies the load-bearing claims behind the project plan before any
analysis is built on them:
  A. corpus size (rows, benchmarks, models)
  B. how many distinct policies appear on >= 2 and >= 3 benchmarks
     (feasibility of cross-benchmark concordance)
  C. reporting spread for the same model on the same benchmark
     (e.g. pi-0 on LIBERO across many reporting papers)
  D. per-task score coverage (feasibility of variance decomposition)
  E. name-normalization mess size (how many raw names collapse together)

Run: python analysis/01_audit.py
"""
import json
import re
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "raw" / "leaderboard.json"


def norm_name(name: str) -> str:
    """First-pass policy-name normalization. Deliberately conservative:
    lowercase, strip punctuation/subscripts/unicode pi, collapse spaces.
    A curated alias table replaces this in 02_normalize.py."""
    s = name.lower().strip()
    s = s.replace("π", "pi")          # unicode pi
    s = re.sub(r"[_\-\s\{\}\\$]+", "", s)  # pi_0, pi-0, pi 0, $\pi_0$ -> pi0
    s = re.sub(r"\(.*?\)", "", s)          # drop parentheticals
    return s


def main() -> None:
    with open(DATA) as f:
        raw = json.load(f)
    rows = raw["results"]

    # A. corpus size
    benchmarks = sorted({r["benchmark"] for r in rows})
    models = {r["model"] for r in rows}
    print(f"last_updated       : {raw.get('last_updated')}")
    print(f"result rows        : {len(rows)}")
    print(f"benchmarks         : {len(benchmarks)} -> {benchmarks}")
    print(f"unique model keys  : {len(models)}")

    # B. cross-benchmark presence per normalized policy name
    by_policy = defaultdict(set)
    for r in rows:
        by_policy[norm_name(r.get("name_in_paper") or r["display_name"])].add(
            r["benchmark"]
        )
    ge2 = {p: b for p, b in by_policy.items() if len(b) >= 2}
    ge3 = {p: b for p, b in by_policy.items() if len(b) >= 3}
    print(f"\npolicies on >=2 benchmarks : {len(ge2)}")
    print(f"policies on >=3 benchmarks : {len(ge3)}")
    top = sorted(by_policy.items(), key=lambda kv: -len(kv[1]))[:15]
    print("widest-coverage policies:")
    for p, b in top:
        print(f"  {p:<22} {len(b)} benchmarks")

    # C. same-model same-benchmark reporting spread
    cell = defaultdict(list)
    for r in rows:
        key = (norm_name(r.get("name_in_paper") or r["display_name"]), r["benchmark"])
        if r.get("overall_score") is not None:
            cell[key].append((r["overall_score"], r.get("reported_paper")))
    multi = {k: v for k, v in cell.items() if len(v) >= 3}
    print(f"\nmodel-benchmark cells with >=3 independent reports: {len(multi)}")
    spreads = sorted(
        ((k, max(s for s, _ in v) - min(s for s, _ in v), len(v)) for k, v in multi.items()),
        key=lambda kv: -kv[1],
    )[:12]
    print("largest reporting spreads (same model, same benchmark):")
    for (p, b), spread, n in spreads:
        lo = min(s for s, _ in cell[(p, b)])
        hi = max(s for s, _ in cell[(p, b)])
        print(f"  {p:<18} on {b:<22} n={n:>3} reports  range {lo:.1f} -> {hi:.1f}  (spread {spread:.1f})")

    # pi0 / LIBERO specifically (the claim from due diligence)
    for key in [("pi0", "libero"), ("openvla", "libero"), ("smolvla", "libero")]:
        matches = [k for k in cell if k[0] == key[0] and key[1] in k[1]]
        for m in matches:
            v = cell[m]
            lo, hi = min(s for s, _ in v), max(s for s, _ in v)
            print(f"  CHECK {m[0]} on {m[1]}: n={len(v)} range {lo:.1f} -> {hi:.1f}")

    # D. per-task coverage
    with_tasks = sum(1 for r in rows if r.get("task_scores"))
    print(f"\nrows with per-task scores: {with_tasks} / {len(rows)}")

    # E. normalization mess: raw name variants per normalized name
    variants = defaultdict(set)
    for r in rows:
        raw_n = r.get("name_in_paper") or r["display_name"]
        variants[norm_name(raw_n)].add(raw_n)
    messy = sorted(((p, v) for p, v in variants.items() if len(v) > 3), key=lambda kv: -len(kv[1]))[:8]
    print("names needing alias curation (raw variants per policy):")
    for p, v in messy:
        print(f"  {p:<20} {len(v)} variants e.g. {sorted(v)[:4]}")


if __name__ == "__main__":
    main()
