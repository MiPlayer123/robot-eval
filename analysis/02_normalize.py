"""Phase 2: policy-name normalization and cleaning.

Produces data/processed/results_clean.parquet with columns:
  policy_id      canonical policy (alias table below)
  variant        fine-tune / quantization / ablation tag, '' for base
  benchmark      harness benchmark id
  score          overall_score
  paper          reporting paper URL
  is_base        True when the row is the unmodified base policy
  n_task_scores  count of per-task scores present

Every cleaning decision gets a line in data/processed/CLEANING_LOG.md.
"""
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# Curated alias table: seed set from 01_audit findings. Grows during the
# manual pass; keep sorted; keys are post-mechanical-normalization strings.
ALIASES = {
    "pi₀": "pi0",
    "pi₀.₅": "pi0.5",
    "pizero": "pi0",
    "pi0base": "pi0",
    "openvla7b": "openvla",
    "diffusionpolicycnn": "diffusionpolicy",
    # ... extend during manual audit
}

# Variant markers that must NOT be merged into the base policy: the
# variance decomposition treats these as artifact variants.
VARIANT_PATTERNS = [
    (re.compile(r"\b(fp16|int8|int4|awq|gptq|quant)", re.I), "quantized"),
    (re.compile(r"\b(\d+)\s*(demos|traj)", re.I), "data-budget"),
    (re.compile(r"\b(lora|oft|ft|finetuned|fine-tuned)\b", re.I), "finetune"),
    (re.compile(r"\b(w/o|without|ablat)", re.I), "ablation"),
]


def mechanical_norm(name: str) -> str:
    s = name.lower().strip()
    s = s.replace("π", "pi").replace("₀", "0").replace("₅", "5")
    s = re.sub(r"\$|\\pi|\\_|[{}\\]", "", s)
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[_\-\s]+", "", s)
    return s


def classify_variant(raw_name: str) -> str:
    for pat, tag in VARIANT_PATTERNS:
        if pat.search(raw_name):
            return tag
    return ""


def main() -> None:
    with open(ROOT / "data" / "raw" / "leaderboard.json") as f:
        rows = json.load(f)["results"]
    recs = []
    for r in rows:
        raw_name = r.get("name_in_paper") or r["display_name"]
        norm = mechanical_norm(raw_name)
        recs.append(
            {
                "policy_id": ALIASES.get(norm, norm),
                "variant": classify_variant(raw_name),
                "raw_name": raw_name,
                "benchmark": r["benchmark"],
                "score": r.get("overall_score"),
                "paper": r.get("reported_paper"),
                "n_task_scores": len(r.get("task_scores") or {}),
            }
        )
    df = pd.DataFrame(recs)
    df["is_base"] = df["variant"] == ""
    out = ROOT / "data" / "processed"
    out.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out / "results_clean.parquet")
    print(df.groupby("variant").size())
    print(f"wrote {len(df)} rows -> {out/'results_clean.parquet'}")


if __name__ == "__main__":
    main()
