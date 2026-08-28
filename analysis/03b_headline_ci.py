"""Phase 3a': bootstrap CIs + robustness for the paper's headline numbers.

Headline: median claimed improvement vs median reporting spread of popular
baseline cells. Robustness: margins recomputed against the best score of a
DIFFERENT policy (so a paper's own ablations can't shrink the margin).
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    df = pd.read_parquet(ROOT / "data" / "processed" / "results_clean.parquet")
    df = df[~df.suspect & df.score.notna()]
    rng = np.random.default_rng(7)

    m1, m2 = [], []
    for (_, _), g in df[df.benchmark != "calvin"].groupby(["paper", "benchmark"]):
        if len(g) < 2:
            continue
        s = g.sort_values("score", ascending=False)
        m1.append(s.score.iloc[0] - s.score.iloc[1])
        others = s[s.policy_id != s.policy_id.iloc[0]]
        if len(others):
            m2.append(s.score.iloc[0] - others.score.iloc[0])
    m1, m2 = np.array(m1), np.array(m2)

    base = df[df.is_base & (df.benchmark != "calvin")]
    pp = (
        base.groupby(["policy_id", "benchmark", "paper"], dropna=False)["score"]
        .median()
        .reset_index()
    )
    g = pp.groupby(["policy_id", "benchmark"])["score"].agg(n="count", lo="min", hi="max")
    spreads = (g[g.n >= 5].hi - g[g.n >= 5].lo).values

    def med_ci(x, n=20000):
        meds = np.median(rng.choice(x, (n, len(x))), axis=1)
        return np.median(x), *np.percentile(meds, [2.5, 97.5])

    rows = []
    for name, arr in [
        ("margin_top1_top2", m1),
        ("margin_vs_other_policy", m2),
        ("popular_cell_spread_ge5", spreads),
    ]:
        m, lo, hi = med_ci(arr)
        rows.append({"stat": name, "n": len(arr), "median": round(m, 2),
                     "ci_lo": round(lo, 2), "ci_hi": round(hi, 2)})
        print(f"{name}: n={len(arr)} median={m:.1f} [{lo:.1f}, {hi:.1f}]")
    pd.DataFrame(rows).to_csv(ROOT / "data" / "processed" / "headline_stats.csv", index=False)
    print(f"ratio spread/robust-margin: {np.median(spreads)/np.median(m2):.1f}x")


if __name__ == "__main__":
    main()
