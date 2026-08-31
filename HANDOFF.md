# Handoff / project state

Last updated: 2026-08-31. Read this first when picking the project back up.

## Where things are

- All analysis code, cleaned data, audit trails, and figures are on `main`
  and reproduce with the commands in README.md. Every number in
  paper/outline.md comes from those scripts.
- The paper draft (paper/main.tex, LaTeX, compiles with pdflatex) is kept
  OUT of the public history until it is final; the working copy lives at
  ~/CodeProjects/robot-eval-paper/ on Mikul's Mac. When final, add it as a
  single commit.
- Target: CoRL 2026 workshop "Everything Beneath the Policy", 4 pages
  excl. refs, double-blind, OpenReview, deadline Oct 9 2026 11:59pm CT.
  Backup: RSS 2027 full paper (~Jan/Feb deadline) for the spring hardware
  study.

## Key results (all reproducible from main)

- Median claimed improvement 1.9 pts [1.6, 2.2]; robust variant 2.0.
- Median cross-paper spread of popular cells (>=5 papers) 14.2 [4.5, 21.5]
  as mined; 6.9 [4.3, 14.2] after the extreme-value audit removed protocol
  confounds and citation/extraction errors (10/20 extremes invalid), over
  the same 25 cells. Scripted in analysis/03c_audited_layer.py, which also
  flags which surviving extremes were not themselves audited (9 of 10).
- Cross-benchmark rank concordance 0.49 vs 0.72 within-benchmark;
  perturbation suites nearly orthogonal (median rho 0.25, 22/24 CIs
  span zero).
- Extraction audit of the LLM-curated corpus: 25/30 exact, ~7% serious.

## Pending human items

1. Adjudicate data/processed/audit_escalations.csv (5 rows) and confirm
   the 20 verdicts in data/processed/extreme_audit_corrections.csv.
2. Rotate the GitHub token to a fine-grained one scoped to this repo.
3. Order Seeed SO-ARM101 kit (spring study); join LeRobot Discord.
4. Read the paper abstract; approve voice before full prose is written.

## Next work items

1. Full prose pass replacing every TODO in main.tex; real bibliography
   from the source list in PLAN.md / outline.md.
2. Figure 1 upgrade: gray out audited-invalid extremes so the figure
   tells the three-layer story.
3. Fit to the workshop template (download from workshop site), 4 pages.
4. After submission: blog post + LeRobot Discord post; PRs adding CI
   reporting into vla-evaluation-harness and lerobot-eval (distribution).

## Conventions

- Commit author: Mikul Saravanan <mikulsaravanan@gmail.com> (repo-local
  config set).
- No em dashes in any written prose. Plain, active, problem-first voice.
- Pre-registered hypotheses are frozen in PLAN.md before analyses run;
  deviations are reported, not hidden (see outline.md REFRAME section).
- Every cleaning decision goes in data/processed/CLEANING_LOG.md.
