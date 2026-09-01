"""Dark, web-shaped MMC figures for poopomics.com.

Study-level, from MMC/MMC1_study_data_final.tsv (n=2,046) — the same file the paper's
Figure 2 notebook uses. The waffle notebook's sample-level source
(MMC1_data_merged_v9_May23_26.tsv) is not on this machine, so the waffle is rebuilt at
study level, which is also the level the abstract's percentages are quoted at.

Tier palette and tier order follow scripts/'MMC1 final figure2.ipynb'.
"""
import os, numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "mmc")
MMC  = "/Users/samde/Library/CloudStorage/OneDrive-UniversityofCalifornia,SanDiegoHealth/MMC"

import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch

INK, INK2, INK3, HAIR = "#f5f5f7", "#a1a1a6", "#86868b", "#ffffff29"
PANEL = "#0f1114"
TIER_COLORS = {1: "#91bfdb", 2: "#fee090", 3: "#fc8d59", 4: "#d73027"}
TIER_SHORT  = {1: "Tier 1", 2: "Tier 2", 3: "Tier 3", 4: "Tier 4"}
TIER_LONG   = {1: "repository\nbiological annotation", 2: "informative\nsample names",
               3: "unique sample IDs,\nno biology", 4: "not reusable"}
STACK_ORDER = [4, 3, 2, 1]

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Work Sans", "DejaVu Sans"],
    "svg.fonttype": "none", "savefig.transparent": True, "savefig.bbox": None,
    "figure.constrained_layout.use": True,
    "figure.constrained_layout.w_pad": 0.10, "figure.constrained_layout.h_pad": 0.10,
    "figure.facecolor": "none", "axes.facecolor": "none",
    "text.color": INK, "axes.labelcolor": INK2, "axes.edgecolor": HAIR,
    "xtick.color": INK3, "ytick.color": INK3, "axes.linewidth": 0.8,
    "axes.labelsize": 10.5, "xtick.labelsize": 9.5, "ytick.labelsize": 9.5,
    "legend.fontsize": 9.5,
})

def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, format="svg"); plt.close(fig)
    print("wrote %-30s %6.0f KB" % (name, os.path.getsize(p) / 1024))

os.makedirs(OUT, exist_ok=True)
df = pd.read_csv(os.path.join(MMC, "MMC1_study_data_final.tsv"), sep="\t",
                 low_memory=False, keep_default_na=False, na_values=[])
df["Year"] = df["Year"].astype(int); df["Tier"] = df["Tier"].astype(int)
# Tier totals supplied directly on 31 Aug 2026, superseding the export for the waffle only.
# The two yearly panels below still come off the TSV, because nothing per-year came with these.
TIER_TOTALS = {1: 183, 2: 380, 3: 607, 4: 1975}

counts_t = dict(TIER_TOTALS) if TIER_TOTALS else {t: int((df.Tier == t).sum())
                                                 for t in (1, 2, 3, 4)}
N = sum(counts_t.values())
reusable = counts_t[1] + counts_t[2]

# ============ 1. one square per study, banded by tier ============
ROWS = 22
cols = int(np.ceil(N / ROWS))
fig, ax = plt.subplots(figsize=(11.5, 4.4))
i = 0; edges = []
for t in (1, 2, 3, 4):
    for _ in range(counts_t[t]):
        ax.add_patch(Rectangle((i // ROWS, i % ROWS), 0.86, 0.86,
                               facecolor=TIER_COLORS[t], edgecolor="none"))
        i += 1
    edges.append(i / ROWS)
# Tier 1 and 2 are narrow bands, so labels stagger between two heights with leader lines
# rather than colliding above them. Everything else about the run is caption text in the page.
prev = 0
for k, (t, edge) in enumerate(zip((1, 2, 3, 4), edges)):
    xm = (prev + edge) / 2
    y = ROWS + 2.6 + 4.2 * (k % 2 == 0)
    ax.plot([xm, xm], [ROWS + 0.6, y - 0.4], color=TIER_COLORS[t], lw=0.8, alpha=0.6)
    ax.text(xm, y, "%s · %s%%" % (TIER_SHORT[t], round(counts_t[t] / N * 100, 1)),
            ha="center", va="bottom", fontsize=10.5, color=TIER_COLORS[t], fontweight="bold")
    ax.text(xm, y - 1.5, "%d studies" % counts_t[t], ha="center", va="bottom",
            fontsize=9.5, color=INK3)
    prev = edge
ax.plot([edges[1], edges[1]], [-0.8, ROWS + 0.6], color=INK, lw=1.0, ls=":")
ax.text(0, -2.6, "%d of %d studies reusable — %.1f%%" % (reusable, N, reusable / N * 100),
        fontsize=11, color=INK, va="bottom", ha="left", fontweight="bold")
ax.set_xlim(-1, cols + 1); ax.set_ylim(-4.0, ROWS + 9.0)
ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_visible(False)
save(fig, "mmc-reusability-waffle.svg")

# ============ 2. studies per year, stacked by tier ============
counts = df.groupby(["Year", "Tier"]).size().unstack(fill_value=0)
for t in (1, 2, 3, 4):
    if t not in counts.columns: counts[t] = 0
counts = counts[STACK_ORDER]
fig, ax = plt.subplots(figsize=(9.8, 4.6))
bottom = np.zeros(len(counts))
for t in STACK_ORDER:
    v = counts[t].values
    ax.bar(counts.index, v, bottom=bottom, color=TIER_COLORS[t], width=0.72,
           edgecolor=PANEL, linewidth=0.4, label=TIER_SHORT[t])
    bottom += v
for s, sp in ax.spines.items(): sp.set_visible(s in ("left", "bottom"))
ax.set_xlabel("year of publication"); ax.set_ylabel("studies reviewed")
ax.set_xticks(list(counts.index)); ax.tick_params(length=3)
plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
handles = [Patch(facecolor=TIER_COLORS[t], label="%s — %s" % (TIER_SHORT[t],
           TIER_LONG[t].replace("\n", " "))) for t in (1, 2, 3, 4)]
ax.legend(handles=handles, frameon=False, labelcolor=INK2, loc="upper left", fontsize=9.5)
save(fig, "mmc-tier-by-year.svg")

# ============ 3. sequencing type over time (16S persists) ============
st = df[df.SequencingType.isin(["16S", "Shotgun", "Both"])]
piv = st.groupby(["Year", "SequencingType"]).size().unstack(fill_value=0)
share = piv.div(piv.sum(axis=1), axis=0) * 100
COL = {"16S": "#2997ff", "Shotgun": "#f0b429", "Both": "#7fb069"}
fig, ax = plt.subplots(figsize=(9.8, 3.9))
for k in ("16S", "Shotgun", "Both"):
    if k in share:
        ax.plot(share.index, share[k], color=COL[k], lw=2.0, marker="o", ms=3.2,
                mew=0, label=k)
for s, sp in ax.spines.items(): sp.set_visible(s in ("left", "bottom"))
ax.set_ylim(0, 100); ax.set_xlabel("year of publication")
ax.set_ylabel("share of studies (%)"); ax.tick_params(length=3)
ax.legend(frameon=False, labelcolor=INK2, loc="center right", bbox_to_anchor=(0.995, 0.52))
save(fig, "mmc-sequencing-type.svg")

print("\nfacts for captions:")
print("  waffle studies: %d   export rows: %d   years %d-%d"
      % (N, len(df), df.Year.min(), df.Year.max()))
print("  tiers: %s" % {TIER_SHORT[t]: counts_t[t] for t in (1, 2, 3, 4)})
print("  reusable (T1+T2): %d = %.1f%%" % (reusable, reusable / N * 100))
acc = (~df["AccessionCode"].astype(str).str.strip().str.upper().isin(["", "N/A", "NA"]))
print("  accession present: %d = %.1f%%" % (acc.sum(), acc.mean() * 100))
print("  sequencing: %s" % df.SequencingType.value_counts().to_dict())
