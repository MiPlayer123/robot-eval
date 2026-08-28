"""Phase 2b: suite-level table.

Several benchmarks (simpler_env, robotwin_v2, libero_plus, robocasa,
libero_pro) report only suite-level scores with no overall_score, so any
analysis keyed on overall_score silently drops them. This explodes every
result into (benchmark, suite) units; '__overall__' is a unit when present.
Output: data/processed/results_suites.parquet
"""
import json
import sys
from importlib import import_module
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
norm = import_module("02_normalize")


def main() -> None:
    with open(ROOT / "data" / "raw" / "leaderboard.json") as f:
        rows = json.load(f)["results"]
    recs = []
    for r in rows:
        raw_name = r.get("name_in_paper") or r["display_name"]
        pid, variant, name_sus = norm.canonicalize(raw_name, r.get("reported_paper"))
        units = {}
        if r.get("overall_score") is not None:
            units["__overall__"] = r["overall_score"]
        for k, v in (r.get("suite_scores") or {}).items():
            if isinstance(v, (int, float)):
                units[k] = v
        for suite, sc in units.items():
            recs.append(
                {"policy_id": pid, "variant": variant, "is_base": variant == "",
                 "benchmark": r["benchmark"], "suite": suite, "score": sc,
                 "paper": r.get("reported_paper"),
                 "suspect": name_sus or sc == 0.0 or sc >= 99.95}
            )
    df = pd.DataFrame(recs)
    df.to_parquet(ROOT / "data" / "processed" / "results_suites.parquet")
    print(f"suite-level rows: {len(df)} | units: {df.groupby(['benchmark','suite']).ngroups}")


if __name__ == "__main__":
    main()
