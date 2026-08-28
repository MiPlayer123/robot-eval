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

## Open items

- Manual 30-entry audit (Mikul) pending: data/processed/audit_sample_30.csv.
- univla + fasterwam disambiguation by reading the reporting papers.
