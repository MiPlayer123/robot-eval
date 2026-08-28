"""Phase 3b: cross-benchmark concordance with honest uncertainty.

Unit of comparison is (benchmark, suite) from results_suites.parquet —
suites are genuinely different eval tracks (SimplerEnv WidowX vs Google
Robot), and several benchmarks publish no overall score at all.

Outputs:
  concordance_all_pairs.csv  point-estimate Spearman rho for every unit
                             pair sharing >= 8 base policies
  concordance_cross.csv      cross-benchmark pairs with bootstrap CIs
Headline statistics printed: median within-benchmark vs cross-benchmark
rho, and the perturbation-suite result.
"""
import itertools
import sys
from pathlib import Path

import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "robostats"))
from robostats import spearman_ci  # noqa: E402

MIN_SHARED = 8


def main() -> None:
    df = pd.read_parquet(ROOT / "data" / "processed" / "results_suites.parquet")
    d = df[~df.suspect & df.is_base]
    # calvin suites (1_task..5_tasks) are chain-lengths of one metric; keep
    # only its overall to avoid five near-duplicate units
    d = d[~((d.benchmark == "calvin") & (d.suite != "__overall__"))].copy()
    d["unit"] = d.benchmark + "/" + d.suite
    med = d.groupby(["policy_id", "unit"])["score"].median().unstack()
    notna = med.notna()

    rows = []
    for a, b in itertools.combinations(med.columns, 2):
        mask = notna[a] & notna[b]
        n = int(mask.sum())
        if n < MIN_SHARED:
            continue
        x, y = med.loc[mask, a].values, med.loc[mask, b].values
        rows.append(
            {"a": a, "b": b, "n": n,
             "cross_benchmark": a.split("/")[0] != b.split("/")[0],
             "rho": round(float(stats.spearmanr(x, y).statistic), 2)}
        )
    res = pd.DataFrame(rows)
    res.to_csv(ROOT / "data" / "processed" / "concordance_all_pairs.csv", index=False)

    cis = []
    for _, r in res[res.cross_benchmark].iterrows():
        mask = notna[r.a] & notna[r.b]
        x, y = med.loc[mask, r.a].values, med.loc[mask, r.b].values
        rho, lo, hi = spearman_ci(x, y, n_boot=1500)
        cis.append({"a": r.a, "b": r.b, "n": r.n, "rho": round(rho, 2),
                    "lo": round(lo, 2), "hi": round(hi, 2)})
    cross = pd.DataFrame(cis).sort_values("n", ascending=False)
    cross.to_csv(ROOT / "data" / "processed" / "concordance_cross.csv", index=False)

    within = res[~res.cross_benchmark]
    print(f"unit pairs >= {MIN_SHARED} shared: {len(res)} "
          f"(cross-benchmark: {res.cross_benchmark.sum()})")
    print(f"median rho within-benchmark: {within.rho.median():.2f} | "
          f"cross-benchmark: {res[res.cross_benchmark].rho.median():.2f}")
    informative = ((cross.lo > 0) | (cross.hi < 0)).sum()
    print(f"cross pairs with CI excluding zero: {informative}/{len(cross)}")
    pert = cross[cross.b.str.contains("noise|camera") | cross.a.str.contains("noise|camera")]
    print(f"perturbation-suite (noise/camera) pairs: median rho {pert.rho.median():.2f} "
          f"({((pert.lo <= 0) & (pert.hi >= 0)).sum()}/{len(pert)} CIs span zero)")


if __name__ == "__main__":
    main()
