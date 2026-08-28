# Execution Plan

Goal: valid, publishable results on robot policy evaluation reliability.
Strategy: own repo is home; PRs into vla-evaluation-harness / lerobot-eval
are distribution later, never a dependency for the paper.

## Timeline (deadline: Oct 9, CoRL 2026 workshop "Everything Beneath the Policy")

Week of Sep 1   Phase 2: name normalization + data cleaning
                - curated alias table (pi0/pi₀/$\pi_0$/... -> one id),
                  fine-tune-variant vs base-model tagging, quantization
                  variants separated (qvla/awq/gptq 0.0 rows are suspect)
                - audit 30 random entries against source papers (LLM-curated
                  corpus; error rate is itself a paper finding)
                GATE: cleaned table reviewed before analysis starts

Weeks of Sep 8 + 15   Phase 3: the two analyses
                - variance decomposition on cells with >=3 independent
                  reports (134 cells pre-cleaning, more after alias merge):
                  model vs benchmark vs reporting-paper vs artifact-variant
                - cross-benchmark concordance (Spearman/Kendall with
                  bootstrap CIs via robostats) on the 140+ policies
                  appearing on >=3 benchmarks
                - pre-registered hypothesis (written before running Phase 3):
                  within-benchmark cross-paper variance exceeds
                  between-benchmark disagreement
                GATE: numbers reviewed + robustness-checked before writing

Weeks of Sep 22 + 29   Phase 4: paper
                - 4 pages excl. refs, double-blind, OpenReview
                - figures: spread-per-cell plot, variance decomposition,
                  concordance matrix with CIs
                Submit by Oct 9, 11:59pm CT

Parallel (low priority until after Oct 9): robostats hardening, then
integration PRs. Spring: part 3 (SO-101 study) per brief, needs advisor.

## Validity rules (how we avoid fooling ourselves)

1. Hypotheses written down before the analysis that tests them runs.
2. Every claim in the paper carries an interval computed by robostats.
3. Data-cleaning decisions logged in data/processed/CLEANING_LOG.md;
   analyses re-run with and without each contested decision (sensitivity).
4. The 30-entry manual audit happens before trusting any aggregate.
5. Code deterministic (seeded), one command reproduces every figure.

## Repo layout

data/raw/          leaderboard.json (AI2 harness, pulled 2026-08-28)
data/processed/    cleaned tables + CLEANING_LOG.md
analysis/          01_audit.py (done) 02_normalize.py 03_decompose.py
                   04_concordance.py 05_figures.py
robostats/         MIT-licensed stats package (12 tests passing)
paper/             outline.md -> LaTeX later
