# robot-eval

Honest measurement for robot policy evaluation. See PLAN.md for the plan
and data/processed/CLEANING_LOG.md for every data decision.

## Reproduce everything

    pip install -e robostats/ && pip install pandas pyarrow matplotlib
    python analysis/01_audit.py       # corpus audit
    python analysis/02_normalize.py   # cleaning -> results_clean.parquet
    python analysis/02b_suites.py     # suite-level table
    python analysis/03_decompose.py   # reporting-variance anatomy
    python analysis/03b_headline_ci.py # headline stats + bootstrap CIs
    python analysis/03c_audited_layer.py # audited-layer spreads + CIs
    python analysis/04_concordance.py # cross-benchmark concordance (slow-ish)
    python analysis/05_figures.py     # paper figures
    (cd robostats && python -m pytest tests/) # stats library tests

All analyses are deterministic (seeded). Data: AI2 vla-evaluation-harness
leaderboard corpus, pulled 2026-08-28 (data/raw/leaderboard.json).

## Key results (Aug 28 2026)

Median claimed improvement: 1.9 pts [1.6, 2.2]. Median reported-score
spread of popular cells (>=5 papers): 14.2 pts [4.5, 21.5] as mined, ~7x
the claimed margins, falling to 6.9 [4.3, 14.2] over the same 25 cells
once audited extremes are dropped or corrected. So about half the
apparent spread is protocol confound and citation/extraction error
rather than reproduction variance (analysis/03c_audited_layer.py).
Cross-benchmark rank concordance 0.49 vs 0.72 within-benchmark;
perturbation suites nearly orthogonal to clean scores. Extraction audit
of the LLM-curated corpus: 25/30 exact, ~7% serious errors. Paper
target: CoRL 2026 workshop (Oct 9).
