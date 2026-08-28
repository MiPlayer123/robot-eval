"""Phase 2: policy-name normalization and cleaning (curated v1).

Outputs data/processed/results_clean.parquet with columns:
  policy_id   canonical policy identity (curation rules below)
  variant     parenthetical/pattern variant tag ('' = base row)
  raw_name    name as extracted from the source paper
  benchmark, score, paper, n_task_scores, is_base, suspect

Curation rules (full rationale in data/processed/CLEANING_LOG.md):
  R1 NFKC + lowercase + LaTeX cleanup keeps dots/digits: $\\pi_{0.5}$ -> pi0.5
  R2 parentheticals become the variant tag, never part of identity
  R3 separators [-_ space] removed; '.' kept (pi0 vs pi0.5 differ)
  R4 curated ALIASES applied after mechanical normalization
  R5 GENERIC names (ours, baseline, bc, ...) get per-paper identities
     ("ours::<paper>") so different papers' models never merge
  R6 wrapper methods (contextvla, t2vla, ...) keep wrapper identity;
     backbone recorded as variant
  R7 known name collisions (univla) are flagged, not resolved
"""
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# R4: curated aliases, keys are post-mechanical strings. Every entry is a
# judgment call logged in CLEANING_LOG.md.
ALIASES = {
    # LaTeX orphans of the pi family
    "0": "pi0",
    "0.5": "pi0.5",
    "pi": "pi0",            # bare $\pi$ rows: all inspected rows are pi0
    "pi05": "pi0.5",
    "pizero": "pi0",
    # pi0 + FAST reported under multiple spellings, incl. LaTeX orphan
    "pi0+fast": "pi0fast",
    "0fast": "pi0fast",
    "0+fast": "pi0fast",
    # DP is the standard abbreviation for Diffusion Policy in this literature
    "dp": "diffusionpolicy",
    # DP3 == 3D Diffusion Policy (same paper, Ze et al. 2024)
    "3ddiffusionpolicy": "dp3",
    # RoboVLMs is the paper; RoboVLM appears as its singular
    "robovlms": "robovlm",
    # capitalization/hyphen variants the mechanical pass already collapses are
    # not listed; only true respellings are
    "octobase": "octo-base",
    "octosmall": "octo-small",
    "3ddiffuseractor": "3d-diffuser-actor",
    "bctransformer": "bc-transformer",
}

# Deliberate NON-merges (documented so the review pass can check them):
#   openvlaoft != openvla        (different method, OFT paper)
#   pi0fast != pi0               (different tokenizer/decoder)
#   octo-base != octo-small != octo (different checkpoints)
#   rdt != rdt1b                 (RDT ambiguous across versions)
#   gr00t != gr00tn1/n1.5/n1.6/n1.7 (unversioned GR00T is ambiguous)
#   dp3 != diffusionpolicy       (3D variant is a different method)

# R5: names that carry no cross-paper identity
GENERIC = {
    "ours", "baseline", "bc", "vanilla", "base", "scratch", "sft",
    "oracle", "human", "expert", "random", "mlp", "gpt4o", "gpt4v",
    "gpt4", "rl", "grpo",
}

# R7: known cross-paper name collisions or ambiguous names -> flag suspect
# univla: two distinct 2025 papers (Bu et al. 2505.06111; Wang et al.
#   2506.19850) share the name; disambiguate later by source paper
# fasterwam: two distinct Aug 2026 papers (2608.02365, 2608.04404)
# fast: a bare "FAST" row cannot be attributed without reading the paper
KNOWN_COLLISIONS = {"univla", "fasterwam", "fast"}

VARIANT_PATTERNS = [
    (re.compile(r"\b(fp16|bf16|int8|int4|w4a4|awq|gptq|quant)", re.I), "quantized"),
    (re.compile(r"\b(\d+)\s*(%|demos?|traj)", re.I), "data-budget"),
    (re.compile(r"\b(lora|finetun|fine-tun|ft\b)", re.I), "finetune"),
    (re.compile(r"(w/o|without|ablat|no |frozen)", re.I), "ablation"),
    (re.compile(r"\b(repro|reproduc|3rd|third[- ]party)", re.I), "reproduction"),
    (re.compile(r"\b(zero-?shot)", re.I), "zero-shot"),
]

LATEX_JUNK = re.compile(r"\$|\\pi|\\text|\\mathrm|\\_|[{}\\]")
PARENS = re.compile(r"\((.*?)\)")
SEPARATORS = re.compile(r"[_\s‐-―-]+")


def mechanical_norm(name: str) -> tuple[str, str]:
    """Returns (normalized_identity, parenthetical_text)."""
    s = unicodedata.normalize("NFKC", name).strip()
    parens = " ".join(PARENS.findall(s))
    s = PARENS.sub("", s)
    s = s.lower().replace("π", "pi")  # unicode pi
    s = LATEX_JUNK.sub("", s)
    s = SEPARATORS.sub("", s)
    s = s.strip(".")
    return s, parens


def classify_variant(raw_name: str, parens: str) -> str:
    hay = f"{raw_name} {parens}"
    for pat, tag in VARIANT_PATTERNS:
        if pat.search(hay):
            return tag
    return parens.strip().lower()[:40] if parens.strip() else ""


def paper_slug(url: str | None) -> str:
    return hashlib.sha1((url or "unknown").encode()).hexdigest()[:8]


def canonicalize(raw_name: str, paper: str | None) -> tuple[str, str, bool]:
    """Returns (policy_id, variant, suspect_name)."""
    ident, parens = mechanical_norm(raw_name)
    ident = ALIASES.get(ident, ident)
    variant = classify_variant(raw_name, parens)
    if ident in GENERIC:
        return f"{ident}::{paper_slug(paper)}", variant, False
    return ident, variant, ident in KNOWN_COLLISIONS


def main() -> None:
    with open(ROOT / "data" / "raw" / "leaderboard.json") as f:
        rows = json.load(f)["results"]
    recs = []
    for r in rows:
        raw_name = r.get("name_in_paper") or r["display_name"]
        pid, variant, name_suspect = canonicalize(raw_name, r.get("reported_paper"))
        score = r.get("overall_score")
        # score-level suspects: exact 0.0 or 100.0 with a named variant often
        # signals extraction error or degenerate ablation; flag, don't drop
        score_suspect = score is not None and (score == 0.0 or score >= 99.95)
        recs.append(
            {
                "policy_id": pid,
                "variant": variant,
                "raw_name": raw_name,
                "benchmark": r["benchmark"],
                "score": score,
                "paper": r.get("reported_paper"),
                "n_task_scores": len(r.get("task_scores") or {}),
                "suspect": name_suspect or score_suspect,
            }
        )
    df = pd.DataFrame(recs)
    df["is_base"] = df["variant"] == ""
    out = ROOT / "data" / "processed"
    out.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out / "results_clean.parquet")

    n_multi = (
        df[df.is_base].groupby("policy_id")["benchmark"].nunique().ge(3).sum()
    )
    print(f"rows: {len(df)}  policies: {df.policy_id.nunique()}")
    print(f"base rows: {df.is_base.sum()}  suspect rows: {df.suspect.sum()}")
    print(f"base policies on >=3 benchmarks: {n_multi}")
    for pid in ["pi0", "pi0.5", "openvla", "gr00tn1.6"]:
        sub = df[(df.policy_id == pid)]
        print(f"  {pid}: rows={len(sub)} benchmarks={sub.benchmark.nunique()}")


if __name__ == "__main__":
    main()
