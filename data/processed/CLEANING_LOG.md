# Cleaning log

Every identity decision applied by analysis/02_normalize.py, with rationale.
Sensitivity rule: any analysis result quoted in the paper is re-run with the
contested merges (marked ⚠) disabled, and both numbers are reported if they
differ materially.

## Mechanical rules

- R1 NFKC + lowercase; unicode pi -> "pi"; LaTeX stripped keeping digits and
  dots, so `$\pi_{0.5}$` -> `pi0.5`. Verified: the 31 LaTeX rows merged into
  pi0 (14) and pi0.5 (17); zero bare-`pi` rows exist in the corpus.
- R2 parenthetical text is a variant tag, never identity. `pi0 (30 demos)` is
  policy pi0, variant "data-budget", is_base=False.
- R3 separators [-_ space, unicode dashes] removed; '.' kept (pi0 vs pi0.5).

## Curated merges

| merge | rationale | risk |
|---|---|---|
| $\pi_0$-family -> pi0 | LaTeX spellings of the same Physical Intelligence model | none |
| $\pi_{0.5}$-family -> pi0.5 | same | none |
| pi0+FAST -> pi0fast | "pi0 + FAST" and "pi0-FAST" are the same FAST-tokenizer variant | low |
| DP -> diffusionpolicy ⚠ | DP is the standard abbreviation in this literature; occurrences on libero(5)/maniskill2(2)/robotwin_v2(9), all benchmarks where Diffusion Policy is the stock baseline | a paper could use DP for something else; sensitivity-checked |
| 3D Diffusion Policy -> dp3 | same paper (Ze et al.), DP3 is its own acronym | none |
| RoboVLMs -> robovlm ⚠ | singular/plural of one paper's framework | low |
| pizero -> pi0 | spelling variant | none |

## Deliberate non-merges

openvla-oft stays separate from openvla (different method). pi0fast separate
from pi0 (different decoder). octo-base / octo-small / octo separate
(different checkpoints; bare "octo" ambiguous). rdt separate from rdt1b
(version ambiguity). Unversioned gr00t separate from gr00tn1/n1.5/n1.6/n1.7.
dp3 separate from diffusionpolicy. Wrapper methods (ContextVLA, T2VLA,
DivPrune+X, VLA-IAP+X) keep wrapper identity; backbone is the variant.

## Generic names

ours, baseline, bc, vanilla, base, scratch, sft, oracle, human, expert,
random carry no cross-paper identity: policy_id becomes `<name>::<paper-hash>`.
Effect: 12 "Ours" rows split into 8 per-paper identities.

## Known collisions (flagged, unresolved)

univla: at least two distinct 2025 papers use the name UniVLA. All 40 rows
are marked suspect=True and excluded from headline concordance until resolved
by paper-level disambiguation.

## Score-level suspects

Rows with overall_score == 0.0 or >= 99.95 are marked suspect (n included in
suspects.csv): exact-zero entries on quantization ablations (qvla/awq/gptq)
look like extraction errors or degenerate ablations and must be checked
against source papers before any variance figure includes them.

## Adversarial review pass (completed, agent-verified against literature)

All curated merges CONFIRMED against sources: DP = Diffusion Policy on
RoboTwin/ManiSkill/LIBERO (robotwin-platform.github.io docs); DP3 = 3D
Diffusion Policy (Ze et al., RSS 2024); pi0+FAST = pi0-FAST (PI FAST paper);
RoboVLMs = one framework (arXiv 2412.14058). Non-merges confirmed: RDT-2
exists (HF robotics-diffusion-transformer/RDT2-VQ) so bare rdt stays
ambiguous; GR00T N1..N1.7 all exist; bare Octo genuinely varies between
Base and Small across papers. UniVLA collision confirmed real (Bu et al.
arXiv 2505.06111 vs Wang et al. 2506.19850; both ~95 on LIBERO, so score
fingerprints don't separate them there; use CALVIN ABC->D 4.63 /
SimplerEnv-Bridge 69.8 to identify Wang et al.).

Fixes applied after review: (1) LaTeX-orphan trap "$\pi_0$-Fast" -> was
"0fast", now aliased to pi0fast (1 row); (2) fasterwam added to collisions
(two Aug 2026 papers, arXiv 2608.02365 and 2608.04404, share the name);
(3) bare "FAST" row flagged ambiguous; (4) generic set extended with mlp,
gpt4o, gpt4v, gpt4, rl, grpo. Reviewer caveat adopted for the paper: DP/ACT
rows are per-paper REIMPLEMENTATIONS of one method, so their cross-paper
variance mixes protocol and implementation; this is a finding, not noise.

## 30-entry extraction audit (agent-assisted, completed Aug 28 2026)

Method: three independent agents fetched each entry's source paper (arXiv
HTML) and compared the corpus numbers to the paper's tables. Human
adjudication of the 5 non-exact entries pending (audit_escalations.csv).

Result: 25/30 EXACT, 3 PARTIAL, 1 MISMATCH, 1 wrong-paper citation.
- Serious errors (2/30 ~= 6.7%): simpler_env RT-2-X score 60.53 appears
  nowhere in its cited paper (2607.07076: VM avg 46.3, VA 54.4); calvin
  RoboUniview cites 2505.07817, which never mentions the model (correct
  source is 2406.18977).
- Minor errors (3/30 = 10%): a goal/object column swap (MolmoAct entry,
  overall 86.8 vs 86.6); two aggregate slips of 0.1 (UniVLA 94.0 vs 93.9;
  pi0-FAST VLABench "overall" 49.6 vs recomputable 49.5 — aggregates
  appear LLM-recomputed rather than read).
Implications adopted: (a) prefer suite-level scores over "overall" fields
where both exist; (b) the 0.1-0.2-point slip scale is far below the
tens-of-points reporting variance we measure, so the headline analysis is
robust to it; (c) the ~7% serious-error rate is itself a paper finding
about LLM-curated corpora and is reported as such.

## Extreme-value audit of top-10 spread cells (Aug 28)

The min and max of each top-10 spread cell (20 values) were verified
against source papers with eval-condition characterization. Verdicts and
per-entry evidence: extreme_audit_targets.csv + extreme_audit_corrections.csv;
recomputed effect: extreme_audit_effect.csv. Result: 10 dropped (5
protocol-1shot from NS-VLA 2603.09542, 2 citation errors, 1 misattribution,
2 secondhand-derived), 3 corrected (35.6->35.7 n/a after drop, 98.4->98.5,
95.8->95.9, 86.5->85.7 for 2601.11404), 7 kept. Effect (scripted in
analysis/03c_audited_layer.py, which recomputes these from the corrections
file): top-10 median spread 32.7->13.8 [6.1, 23.4]; all >=5-paper cells
14.2->6.9 [4.3, 14.2], over an identical set of 25 cells. Name-based cleaning
cannot catch these - the confound lives in table headers and per-paper
protocols, which is itself a paper finding.

## Independence and dispersion checks (Aug 31)

Two assumptions behind the as-mined headline were tested rather than
assumed (analysis/03d_independence.py, 03e_dispersion_sensitivity.py).

1. Reports are NOT independent measurements. Across the 25 popular cells,
   301 paper-reports carry 161 distinct values (47% redundancy); the modal
   value holds a median 43% of a cell; in 10 of 58 cells with >=3 reporting
   papers every paper gives the identical score to 0.1 pt (e.g. tracevla /
   libero, six papers all at 74.8; pi0fast / libero_plus, six all at 62.5).
   Independent evaluations do not agree to a tenth of a point six times
   over, so these are quotations of a source number. This is ordinary
   citation practice, not misconduct, but it means "n reporting papers" is
   not "n independent measurements" and bootstrap CIs over papers are
   correspondingly overconfident. Treat cross-paper counts as citation
   counts throughout.

2. Range is the wrong dispersion statistic. The range of n draws grows
   with n at fixed dispersion, so the previously reported "spread grows
   with popularity" (Spearman 0.57) was compared against a null in which
   every cell shares one distribution and no popularity effect exists: the
   null gives 0.59 [0.41, 0.73] and the observed value sits inside it.
   That claim is withdrawn. The same null run on SD gives 0.15
   [-0.11, 0.38] against an observed 0.46, so the SD version survives and
   is what the paper now states. IQR and MAD also drift upward with n
   (their small-sample estimates are biased low) and are likewise inside
   their nulls. Only SD is comparable across cells of different
   popularity. Dispersion is therefore reported four ways, and the
   headline moved to a statistic that does not depend on the choice: the
   share of reports differing from their own cell median by more than the
   median claimed improvement (26%; 19% by >5 pts, 7% by >10 pts).

## Open items

- Mikul: adjudicate the 5 rows in audit_escalations.csv (~15 min).
- univla + fasterwam disambiguation by reading the reporting papers.
