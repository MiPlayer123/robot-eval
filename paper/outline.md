# Paper outline (4 pages excl. refs, CoRL 2026 "Everything Beneath the Policy")

Working title: "The Reporting Noise Floor: What VLA Benchmark Scores
Actually Measure"

## REFRAME (Aug 28, after extreme-value audit) — this is the paper now

The 20 extreme values driving the top-10 spread cells were audited against
source papers. 10/20 were invalid for same-protocol comparison: 5 are one
paper's 1-shot data-starvation ablation recorded as plain LIBERO scores
(NS-VLA 2603.09542), 2 are citation errors (a GR00T row duplicating
OpenVLA's numbers digit-for-digit; a since-deleted LIBERO-PRO v1
compilation), 1 is a misattribution (a "SmolVLA" row that is pi0.5 with
async decoding), 2 are secondhand-derived averages papers never printed.
3 more had value errors (0.1-0.9 pts). Only 7/20 were clean.

Three-layer story:
1. AS-MINED: what any consumer of paper-mined numbers sees — median
   popular-cell spread 14.2 pts vs median claimed improvement 1.9 pts (7x).
2. AUDITED: after dropping invalid extremes and correcting values, the
   top-10 cells' median spread falls 32.8 -> 13.8 and the overall
   >=5-paper-cell median 14.2 -> 6.9 [4.3, 14.2]. So roughly HALF the apparent
   reporting noise is protocol confounds and citation/extraction error.
3. RESIDUAL: the remaining same-protocol spread (6.9, still 3.5x the
   median claimed margin) is real reproduction variance - e.g. two labs
   ran the same pi0.5 checkpoint zero-shot on LIBERO-Plus and got 65.0 vs
   85.7; seven other papers cluster 81-86.5.
Meta-point: none of the three layers is distinguishable in any current
leaderboard, because papers publish numbers without machine-readable
protocol metadata. Prescription: protocol-condition tags + audited
leaderboards + CIs (robostats).
Limitation to state: only extremes were audited; unaudited interior
values (and new post-correction extremes, e.g. pi0/libero's 61.1 min)
may contain further confounds - 6.9 is an upper bound on same-protocol
variance from this procedure, not a floor.

## RESULTS STATUS (Aug 28): all three analyses run on cleaned data

- Headline: median claimed improvement (top1-top2 margin per
  paper-benchmark, n=353) is 1.9 points; the median cross-paper spread of
  popular cells (>=5 reporting papers, n=25) is 14.2 points, i.e. ~7.5x.
  Tail: OpenVLA/LIBERO spans 61.4 pts across 18 papers; pi0/LIBERO 59.4
  across 48. Spread grows with popularity (Spearman 0.57).
- Pre-registered hypothesis AS STATED not supported (median cell spread
  3.9 < raw between-benchmark spread 67) - but raw between-benchmark
  spread is a difficulty artifact; report honestly and pivot to ranks.
- Concordance (suite-level units, n>=8 shared): within-benchmark median
  rho 0.72 vs cross-benchmark 0.49; only 85/173 cross pairs have CIs
  excluding zero. Perturbation suites (noise/camera) are nearly
  orthogonal to clean scores: median rho 0.25, 22/24 CIs span zero.
- Extraction audit: 25/30 exact, ~7% serious error rate in the
  LLM-curated corpus (wrong-paper citation; a score not in its paper);
  aggregates appear LLM-recomputed (two 0.1-pt slips). 5 escalations
  pending human adjudication.

## 1. Introduction (0.5 pg)
Claim: before asking which benchmark to trust, ask whether the same
model's score on the same benchmark is stable across reporting papers.
It is not. Preview headline numbers (pi-0 on LIBERO: ~37 to ~95 across
47+ reports pre-alias-merge).

## 2. Data (0.5 pg)
AI2 vla-evaluation-harness corpus: 3,971 results, 16 benchmarks, ~1,900
models, extracted from ~1,755 papers. Our cleaning: alias curation,
variant tagging, 30-entry manual audit with measured extraction error
rate (a finding, not a footnote: corpus is LLM-curated).

## 3. Reporting variance anatomy (1.25 pg)
Variance decomposition over cells with >=3 independent reports:
score = model + benchmark + reporting-paper + artifact-variant + noise.
Pre-registered hypothesis: reporting-paper variance >= between-benchmark
disagreement for shared policies. Sensitivity analysis: with/without
contested cleaning decisions.

## 4. Cross-benchmark concordance, with intervals (0.75 pg)
Spearman/Kendall over 140+ policies on >=3 benchmarks, bootstrap CIs
(robostats). Expectation: concordance exists but is weaker than the
reporting noise floor, i.e., "which benchmark" matters less than "which
paper's number you copied."

## 5. Implications + tooling (0.5 pg)
What honest reporting requires (CIs, protocol disclosure, variant
tagging); robostats as the reference implementation; what harnesses
should enforce. Limitations: corpus is sim-only, LLM-curated, English-
language papers.

## Figures
F1 spread-per-cell dot plot (the money figure)
F2 variance decomposition stacked bars
F3 benchmark-by-benchmark concordance matrix with CI shading

## Pre-registration note
Hypotheses in PLAN.md committed before Phase 3 runs; deviations logged.
