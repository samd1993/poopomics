"""Dark, web-shaped HMToL figures for poopomics.com.

Draws from the pipeline's precomputed .npz intermediates only — no genus matrix, so it does
not need gg2_taxonomy.tsv (absent on this machine; see STATUS.md). Emits SVG with
svg.fonttype='none' so the page's own Mulish webfont renders the labels.

Run:  python3 hmtol_web_figs.py
"""
import os, sys, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.abspath(os.path.join(HERE, "..", "work"))
OUT  = os.path.join(HERE, "hmtol")
PIPE = "/Users/samde/Library/CloudStorage/OneDrive-UniversityofCalifornia,SanDiegoHealth/AGP/Report/hmtol/pipeline"

# patch the pipeline's scratch pointer before anything reads it
sys.path.insert(0, PIPE)
import hmtol_lib as H
H.SW = WORK
H.CACHE = os.path.join(WORK, "table_cache.pkl")
import figassets as FA

import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.cm as cm, matplotlib.colors as mcolors
from scipy.stats import spearmanr

# ---- page tokens (from agp-report-prototype-wild-v2-dark.html :root) ----
INK, INK2, INK3 = "#f5f5f7", "#a1a1a6", "#86868b"
HAIR, LAND, OCEAN = "#ffffff29", "#22252b", "#0f1114"
ACCENT, YOU = "#2997ff", "#f0b429"
CS, CN = "#E69F00", "#0072B2"          # Global South / North, as in the paper
CONT = {"Africa": "#E69F00", "Asia": "#56B4E9", "Australia": "#009E73",
        "Europe": "#CC79A7", "North America": "#0072B2", "South America": "#D55E00"}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Work Sans", "DejaVu Sans"],
    "svg.fonttype": "none",            # keep text as text -> page font applies
    "savefig.transparent": True,
    "savefig.bbox": None,
    "figure.constrained_layout.use": True,
    "figure.constrained_layout.w_pad": 0.10,
    "figure.constrained_layout.h_pad": 0.10,
    "figure.facecolor": "none", "axes.facecolor": "none",
    "text.color": INK, "axes.labelcolor": INK2, "axes.edgecolor": HAIR,
    "xtick.color": INK3, "ytick.color": INK3,
    "axes.linewidth": 0.8, "axes.titlesize": 12, "axes.labelsize": 10.5,
    "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "legend.fontsize": 9.5,
})

def bare(ax, keep=("left", "bottom")):
    for s, sp in ax.spines.items():
        sp.set_visible(s in keep)

def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, format="svg"); plt.close(fig)
    print("wrote %-34s %6.0f KB" % (name, os.path.getsize(p) / 1024))

os.makedirs(OUT, exist_ok=True)
Z = np.load(os.path.join(WORK, "country_var_full.npz"), allow_pickle=True)
feats = FA.load_geo(os.path.join(WORK, "ne110.geojson"))
nmm = {f["name"].lower(): f for f in feats}
ALIAS = {"United States": "United States of America"}
def find(c): return nmm.get(ALIAS.get(c, c).lower())

def iso_vals(tag, metric):
    out = {}
    for c, v in zip(Z["%s_countries" % tag], Z["%s_%s" % (tag, metric)]):
        f = find(c)
        if f and f["iso"]: out[f["iso"]] = float(v)
    return out

# ============ 0. how many studies each country contributed ============
# Straight from the collection metadata rather than an intermediate: distinct studies per country.
meta = H.load_meta()
cty = meta[["country_c", "study_c"]].dropna()
per_country = cty.groupby("country_c")["study_c"].nunique().sort_values(ascending=False)
n_studies = cty["study_c"].nunique()
studies_by_iso = {}
for c, v in per_country.items():
    f = find(c)
    if f and f["iso"]:
        studies_by_iso[f["iso"]] = studies_by_iso.get(f["iso"], 0) + int(v)

vmax = max(studies_by_iso.values())
# Truncate the dark end of the ramp: a one-study country has to be obviously coloured rather
# than fading into the grey used for countries the collection never reached.
STUDY_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "studies", plt.colormaps["viridis"](np.linspace(0.30, 1.0, 256)))
fig, ax = plt.subplots(figsize=(11.5, 5.2))
norm = mcolors.LogNorm(vmin=1, vmax=vmax)
FA.draw_choropleth(ax, feats, studies_by_iso, STUDY_CMAP, norm,
                   missing=LAND, edge=OCEAN, lw=0.35, aspect="auto", facecolor="none")
cb = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=STUDY_CMAP),
                  ax=ax, orientation="horizontal", fraction=0.045, pad=0.02, shrink=0.42,
                  aspect=34, anchor=(0.0, 1.0))
cb.set_label("studies contributed  ·  grey = not reached", fontsize=9.5, color=INK2)
cb.ax.tick_params(labelsize=8.5, color=INK3, labelcolor=INK3)
cb.ax.minorticks_off()
cb.outline.set_edgecolor(HAIR)
save(fig, "hmtol-studies-map.svg")
print("   studies %d across %d countries; top: %s"
      % (n_studies, len(per_country), dict(per_country.head(6))))

# ============ 1. westernization choropleth (adults) ============
vbi = iso_vals("adult", "west")
vv = np.array(list(vbi.values()))
fig, ax = plt.subplots(figsize=(11.5, 5.2))
norm = mcolors.Normalize(vv.min(), vv.max())
FA.draw_choropleth(ax, feats, vbi, plt.colormaps["viridis_r"], norm,
                   missing=LAND, edge=OCEAN, lw=0.35, aspect="auto", facecolor="none")
cb = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=plt.colormaps["viridis_r"]),
                  ax=ax, orientation="horizontal", fraction=0.045, pad=0.02, shrink=0.42,
                  aspect=34, anchor=(0.0, 1.0))
cb.set_label("mean UniFrac to the Global-North reference", fontsize=9.5, color=INK2)
cb.ax.tick_params(labelsize=8.5, color=INK3, labelcolor=INK3)
cb.outline.set_edgecolor(HAIR)
save(fig, "hmtol-westernization-map.svg")

# ============ 2. westernization vs HDI (adults) ============
c, h = Z["adult_countries"], Z["adult_hemi"]
w, hd = Z["adult_west"], Z["adult_hdi"]
fig, ax = plt.subplots(figsize=(8.6, 5.0)); bare(ax)
for hh, col in (("South", CS), ("North", CN)):
    m = h == hh
    ax.scatter(hd[m], w[m], c=col, s=54, edgecolor=OCEAN, lw=0.6,
               label="Global " + hh, zorder=3)
mm = np.isfinite(hd)
b1, b0 = np.polyfit(hd[mm], w[mm], 1)
xs = np.linspace(np.nanmin(hd), np.nanmax(hd), 50)
ax.plot(xs, b1 * xs + b0, color=INK3, lw=1.4, ls="--", zorder=2)
rho, p = spearmanr(hd[mm], w[mm])
ax.text(0.015, 0.955, "Spearman ρ = %.2f,  p = %.1e" % (rho, p), transform=ax.transAxes,
        ha="left", va="top", fontsize=10, color=INK2)
for ci, xi, yi in zip(c, hd, w):
    if ci in ("Bolivia", "Ethiopia", "Mali", "Netherlands", "Sweden", "Japan",
              "Peru", "United States", "France"):
        ax.annotate(ci, (xi, yi), fontsize=8.5, ha="center", va="bottom",
                    color=INK3, xytext=(0, 5), textcoords="offset points")
ax.set_xlabel("country HDI"); ax.set_ylabel("westernization distance")
ax.legend(frameon=False, labelcolor=INK2, loc="lower left")
save(fig, "hmtol-westernization-hdi.svg")

# ============ 3. succession trajectories (precomputed traj) ============
S = np.load(os.path.join(WORK, "succession.npz"), allow_pickle=True)
traj, bc = S["traj"], S["bincenters"]
conts = [str(x) for x in S["conts"]]
names = [str(x) for x in S["uni_names"]]
dirs = S["uni_dir"]
def coverage(gi):
    return sum(1 for ci in range(traj.shape[1])
               if (np.isfinite(traj[gi, ci, :]) & (traj[gi, ci, :] > 0)).sum() >= 5)
order = sorted(range(traj.shape[0]), key=lambda gi: (-coverage(gi), -abs(int(dirs[gi]))))[:4]
fig, axs = plt.subplots(2, 2, figsize=(9.6, 5.6), sharex=True)
for k, gi in enumerate(order):
    ax = axs[k // 2, k % 2]; bare(ax)
    for ci, cname in enumerate(conts):
        y = traj[gi, ci, :]
        m = np.isfinite(y) & (y > 0)
        if m.sum() >= 3:
            ax.plot(bc[m], y[m], color=CONT.get(cname, INK3), lw=1.5,
                    marker="o", ms=2.6, mew=0)
    ax.set_yscale("log")
    ax.set_title(names[gi], fontsize=11, color=INK, pad=4)
    ax.set_xticks([0, 20, 40, 60, 80]); ax.tick_params(length=3)
    if k % 2 == 0: ax.set_ylabel("rel. abundance")
    if k // 2 == 1: ax.set_xlabel("age (years)")
handles = [plt.Line2D([], [], color=CONT[c], lw=2, label=c) for c in conts if c in CONT]
fig.legend(handles=handles, frameon=False, labelcolor=INK2, ncol=len(handles),
           loc="outside lower center", fontsize=9.5)
save(fig, "hmtol-succession.svg")

# ============ 4. core microbiome across continents ============
C = np.load(os.path.join(WORK, "core_prev.npz"), allow_pickle=True)
cont_groups = [str(x) for x in C["cont_groups"]]
cont_prev, tax = C["cont_prev"], C["tax_short"]
THR = 0.50
core_sets = [set(np.where(cont_prev[:, i] >= THR)[0]) for i in range(len(cont_groups))]
shared = set.intersection(*core_sets) if core_sets else set()
counts = [len(s) for s in core_sets]

fig, (axA, axB) = plt.subplots(1, 2, figsize=(11.5, 3.9),
                               gridspec_kw={"width_ratios": [1, 1.35]})
bare(axA)
xs_ = np.arange(len(cont_groups))
axA.bar(xs_, counts, color=[CONT.get(c, INK3) for c in cont_groups], width=0.66)
axA.axhline(len(shared), color=YOU, lw=1.2, ls="--")
axA.set_ylim(0, max(counts) * 1.22)
axA.text(-0.42, max(counts) * 1.19, "dashed line: only %d shared by all six" % len(shared),
         color=YOU, fontsize=10, va="top", ha="left")
axA.set_xticks(xs_); axA.set_xticklabels(cont_groups, rotation=30, ha="right", fontsize=9)
axA.set_ylabel("taxa present in ≥%d%% of samples" % int(THR * 100))

def nice(t):
    t = str(t)
    return t.split("__", 1)[1] if "__" in t else t
top = sorted(shared, key=lambda i: -cont_prev[i].mean())
M = cont_prev[np.array(top)][:, :]
im = axB.imshow(M, aspect="auto", cmap="magma", vmin=0.4, vmax=1.0)
axB.set_xticks(range(len(cont_groups)))
axB.set_xticklabels(cont_groups, rotation=30, ha="right", fontsize=9)
axB.set_yticks(range(len(top)))
axB.set_yticklabels([nice(tax[i]) for i in top], fontsize=10)
for s in axB.spines.values(): s.set_visible(False)
axB.tick_params(length=0)
cb = fig.colorbar(im, ax=axB, fraction=0.026, pad=0.015)
cb.set_label("prevalence", fontsize=9.5, color=INK2)
cb.ax.tick_params(labelsize=8.5, color=INK3, labelcolor=INK3); cb.outline.set_edgecolor(HAIR)
save(fig, "hmtol-core.svg")

print("\nfacts for captions:")
print("  countries (all ages): %d   adults: %d" % (len(Z["all_countries"]), len(Z["adult_countries"])))
print("  studies total: %d" % int(Z["all_n_studies"].sum()))
print("  core: per-continent %s ; shared by all %d ; features scanned %d"
      % (dict(zip(cont_groups, counts)), len(shared), cont_prev.shape[0]))
print("  succession genera shown: %s" % [names[i] for i in order])
