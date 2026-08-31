"""Paper figures. Print-oriented (light surface), palette per dataviz method:
categorical blue #2a78d6 / orange #eb6834; text in ink tokens, not series
colors; thin marks; direct labels where they matter.

F1 fig_spreads.pdf/.png   range plot: reported-score span of every cell with
                          >=5 reporting papers, vs the median claimed margin
F2 fig_ecdf.pdf/.png      ECDFs: claimed margins vs multi-report cell spreads
F3 fig_concordance.pdf/.png  benchmark-level median cross-benchmark rho matrix
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIGS = ROOT / "paper" / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

BLUE, ORANGE, INK, MUTED = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e"
SURFACE = "#fcfcfb"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "text.color": INK, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "font.size": 9, "axes.titlesize": 10, "axes.spines.top": False,
    "axes.spines.right": False, "savefig.dpi": 200,
})


def load_cells():
    df = pd.read_parquet(ROOT / "data" / "processed" / "results_clean.parquet")
    df = df[~df.suspect & df.score.notna()]
    base = df[df.is_base & (df.benchmark != "calvin")]
    pp = (base.groupby(["policy_id", "benchmark", "paper"], dropna=False)["score"]
          .median().reset_index())
    g = pp.groupby(["policy_id", "benchmark"])["score"].agg(n="count", lo="min", hi="max")
    g["spread"] = g.hi - g.lo
    margins = []
    for (_, _), grp in df[df.benchmark != "calvin"].groupby(["paper", "benchmark"]):
        if len(grp) < 2:
            continue
        s = grp.sort_values("score", ascending=False)
        others = s[s.policy_id != s.policy_id.iloc[0]]
        if len(others):
            margins.append(s.score.iloc[0] - others.score.iloc[0])
    return g, np.array(margins)


def f1(cells, med_margin):
    """Raw span in gray; audited span (invalid extremes removed, values
    corrected) overlaid in blue for the cells the audit covered."""
    import importlib
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    aud_mod = importlib.import_module("03c_audited_layer")
    pp_aud, _ = aud_mod.apply_audit(aud_mod.per_paper_cells())
    aud = pp_aud.groupby("cell")["score"].agg(lo="min", hi="max")
    corr = pd.read_csv(ROOT / "data" / "processed" / "extreme_audit_corrections.csv")
    aud = aud.loc[aud.index.intersection(corr.cell.unique())]  # audited cells only

    top = cells[cells.n >= 5].sort_values("spread").reset_index()
    top["label"] = top.policy_id + " / " + top.benchmark.str.replace("_", "-")
    top["cell"] = top.policy_id + "/" + top.benchmark
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    y = np.arange(len(top))
    for i, r in top.iterrows():
        ax.plot([r.lo, r.hi], [i, i], color="#c9c8c2", lw=2,
                solid_capstyle="round", zorder=2)
        if r.cell in aud.index:
            a = aud.loc[r.cell]
            ax.plot([a.lo, a.hi], [i, i], color=BLUE, lw=2.4,
                    solid_capstyle="round", zorder=3)
            ax.scatter([a.lo, a.hi], [i, i], s=14, color=BLUE, zorder=4)
    ax.plot([], [], color="#c9c8c2", lw=2, label="as mined")
    ax.plot([], [], color=BLUE, lw=2.4, label="after source audit")
    ax.legend(loc="lower left", frameon=False, fontsize=8)
    ax.axvline(med_margin, color=ORANGE, lw=1.4, ls="--", zorder=1)
    ax.annotate(f"median claimed\nimprovement ({med_margin:.1f} pts)",
                xy=(med_margin, 9.5), fontsize=8, color=MUTED,
                xytext=(med_margin + 5, 7.0),
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    # Numeric gutter: two aligned columns so the as-mined and audited spans
    # are never read as the same quantity. Audited column is blank (dash)
    # where the audit did not cover the cell.
    X_MINED, X_AUD = 112.0, 124.0
    for i, r in top.iterrows():
        ax.annotate(f"{r.spread:.0f}", xy=(X_MINED, i), va="center",
                    ha="right", fontsize=7.5, color=MUTED)
        if r.cell in aud.index:
            a = aud.loc[r.cell]
            ax.annotate(f"{a.hi - a.lo:.0f}", xy=(X_AUD, i), va="center",
                        ha="right", fontsize=7.5, color=BLUE)
        else:
            ax.annotate("-", xy=(X_AUD, i), va="center", ha="right",
                        fontsize=7.5, color="#c9c8c2")
    hy = len(top) - 0.4
    ax.annotate("mined", xy=(X_MINED, hy), va="center", ha="right",
                fontsize=7, color=MUTED)
    ax.annotate("audited", xy=(X_AUD, hy), va="center", ha="right",
                fontsize=7, color=BLUE)
    ax.set_yticks(y, top.label, fontsize=8)
    ax.set_xlabel("reported success rate across papers (%)")
    ax.set_title("Reported-score span per model-benchmark cell\n"
                 "(≥5 reporting papers)", loc="left")
    ax.set_xlim(0, 126)
    ax.set_xticks([0, 20, 40, 60, 80, 100])  # gutter space is not data
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIGS / f"fig_spreads.{ext}")
    plt.close(fig)


def f2(cells, margins):
    spreads = cells[cells.n >= 3].spread.values
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    specs = [(margins, BLUE, "claimed improvement\nmargins", (13, 0.97)),
             (spreads, ORANGE, "multi-report\ncell spreads", (33, 0.80))]
    for arr, color, label, (tx, ty) in specs:
        x = np.sort(arr)
        yy = np.arange(1, len(x) + 1) / len(x)
        ax.step(x, yy, where="post", color=color, lw=2)
        ax.annotate(f"{label} (median {np.median(arr):.1f})", xy=(tx, ty),
                    fontsize=8, color=INK, va="top")
    ax.set_xlabel("points")
    ax.set_ylabel("cumulative fraction")
    ax.set_title("Claimed improvements vs reporting noise", loc="left")
    ax.set_xlim(0, 65)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIGS / f"fig_ecdf.{ext}")
    plt.close(fig)


def f3():
    res = pd.read_csv(ROOT / "data" / "processed" / "concordance_all_pairs.csv")
    res["ba"] = res.a.str.split("/").str[0]
    res["bb"] = res.b.str.split("/").str[0]
    agg = res.groupby(["ba", "bb"])["rho"].median().reset_index()
    benches = sorted(set(agg.ba) | set(agg.bb))
    mat = pd.DataFrame(np.nan, index=benches, columns=benches)
    for _, r in agg.iterrows():
        mat.loc[r.ba, r.bb] = r.rho
        mat.loc[r.bb, r.ba] = r.rho
    fig, ax = plt.subplots(figsize=(4.8, 4.2))
    im = ax.imshow(mat.values, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(benches)), [b.replace("_", "-") for b in benches],
                  rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(benches)), [b.replace("_", "-") for b in benches],
                  fontsize=8)
    for i in range(len(benches)):
        for j in range(len(benches)):
            v = mat.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7.5,
                        color=INK if v < 0.6 else "#ffffff")
    ax.set_title("Median rank correlation between benchmarks\n"
                 "(suite-level units, ≥8 shared policies)", loc="left")
    fig.colorbar(im, ax=ax, shrink=0.75, label="Spearman ρ")
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIGS / f"fig_concordance.{ext}")
    plt.close(fig)


def main() -> None:
    cells, margins = load_cells()
    f1(cells, float(np.median(margins)))
    f2(cells, margins)
    f3()
    print("wrote figures:", sorted(p.name for p in FIGS.iterdir()))


if __name__ == "__main__":
    main()
