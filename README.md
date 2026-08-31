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
    python analysis/03d_independence.py # are cross-paper reports independent?
    python analysis/03e_dispersion_sensitivity.py # dispersion-statistic sensitivity
    python analysis/04_concordance.py # cross-benchmark concordance (slow-ish)
    python analysis/05_figures.py     # paper figures
    (cd robostats && python -m pytest tests/) # stats library tests

All analyses are deterministic (seeded). Data: AI2 vla-evaluation-harness
leaderboard corpus, pulled 2026-08-28 (data/raw/leaderboard.json).

## Key results (Aug 28 2026)

Median claimed improvement: 1.9 pts [1.6, 2.2]. Of every score reported
for a popular cell, 26% differ from that cell's own median by more than
the median claimed improvement (19% by >5 pts, 7% by >10). That is the
headline: it does not depend on how many papers happen to report a cell.

Cross-paper reports are largely quotations, not measurements: 301
paper-reports of the 25 popular cells carry only 161 distinct values
(47% redundancy), the modal value holds a median 43% of a cell, and in
10 of 58 cells with >=3 reporting papers every paper gives the identical
score (analysis/03d_independence.py).

Dispersion is therefore reported several ways, because the range inflates
with the number of reporting papers: median range 14.2 [4.5, 21.5] (7.1x
the claimed margin), SD 5.3 [1.9, 7.0] (2.7x), IQR 1.3 [0.1, 4.0] (0.6x).
Only SD is stable in n. The earlier "spread grows with popularity"
correlation (Spearman 0.57) sits inside a null with no popularity effect
at all and is not evidence; the SD version (0.46 vs null 0.15) survives
(analysis/03e_dispersion_sensitivity.py).

Source audit of the extremes behind the ten widest cells: 10/20 invalid
for same-protocol comparison, taking the median range 14.2 -> 6.9
[4.3, 14.2] over the same 25 cells (analysis/03c_audited_layer.py).
Cross-benchmark rank concordance 0.49 vs 0.72 within-benchmark;
perturbation suites nearly orthogonal to clean scores. Extraction audit
of the LLM-curated corpus: 25/30 exact, ~7% serious errors. Paper
target: CoRL 2026 workshop (Oct 9).
