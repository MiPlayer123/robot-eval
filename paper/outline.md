# Paper outline (4 pages excl. refs, CoRL 2026 "Everything Beneath the Policy")

Working title: "The Reporting Noise Floor: What VLA Benchmark Scores
Actually Measure"

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
