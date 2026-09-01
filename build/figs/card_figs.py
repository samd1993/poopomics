"""The three home-page card graphics — real figures, miniaturised.

  GMToL — a zoom into the recoloured host phylogeny: silhouettes, tip bars, branches
  HMToL — the studies-per-country map on an orthographic globe
  MMC   — the reusability waffle, shrunk to a card-sized block

Run after hmtol_web_figs.py and gmtol_web_figs.py.
"""
import os, sys, math
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.abspath(os.path.join(HERE, "..", "work"))
OUT = os.path.join(HERE, "cards")
PIPE = ("/Users/samde/Library/CloudStorage/OneDrive-UniversityofCalifornia,SanDiegoHealth/"
        "AGP/Report/hmtol/pipeline")
GSRC = ("/Users/samde/Library/CloudStorage/OneDrive-UniversityofCalifornia,SanDiegoHealth/"
        "TOL2024/figs/Final Figures")

sys.path.insert(0, PIPE)
import hmtol_lib as H                                     # noqa: E402
H.SW = WORK
H.CACHE = os.path.join(WORK, "table_cache.pkl")
import figassets as FA                                    # noqa: E402

import matplotlib; matplotlib.use("Agg")                  # noqa: E402
import matplotlib.pyplot as plt, matplotlib.colors as mcolors  # noqa: E402

sys.path.insert(0, HERE)
from gmtol_web_figs import darkify                        # noqa: E402

INK3, LAND, OCEAN = "#86868b", "#22252b", "#0f1114"
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Work Sans", "DejaVu Sans"],
    "svg.fonttype": "none", "savefig.transparent": True, "savefig.bbox": None,
    "figure.facecolor": "none", "axes.facecolor": "none",
})
os.makedirs(OUT, exist_ok=True)


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, format="svg"); plt.close(fig)
    print("wrote %-22s %6.0f KB" % (name, os.path.getsize(p) / 1024))


# ---------------------------------------------------- GMToL: zoom into the tree ----
# A slice of the ring where the silhouettes, the phylum bars and the branches are all visible.
im = Image.open(os.path.join(GSRC, "GMTOL_Figure_1_wNewTree_300dpi.png")).crop((250, 1000, 1120, 1480))
im = darkify(im)
im.thumbnail((880, 880), Image.LANCZOS)
p = os.path.join(OUT, "gmtol-card.webp")
im.save(p, "WEBP", quality=86, method=6)
print("wrote %-22s %s  %6.0f KB" % ("gmtol-card.webp", im.size, os.path.getsize(p) / 1024))


# --------------------------------------------------- HMToL: studies on a globe ----
meta = H.load_meta()
cty = meta[["country_c", "study_c"]].dropna()
per_country = cty.groupby("country_c")["study_c"].nunique()
feats = FA.load_geo(os.path.join(WORK, "ne110.geojson"))
nmm = {f["name"].lower(): f for f in feats}
ALIAS = {"United States": "United States of America"}
studies = {}
for c, v in per_country.items():
    f = nmm.get(ALIAS.get(c, c).lower())
    if f and f["iso"]:
        studies[f["iso"]] = studies.get(f["iso"], 0) + int(v)

LON0, LAT0 = 44.0, 22.0          # centred so the collection's dense half faces the viewer
la0, lo0 = math.radians(LAT0), math.radians(LON0)


def ortho(ring):
    """Orthographic projection; vertices on the far side of the globe are dropped."""
    lon = np.radians(ring[:, 0]); lat = np.radians(ring[:, 1])
    cosc = np.sin(la0) * np.sin(lat) + np.cos(la0) * np.cos(lat) * np.cos(lon - lo0)
    x = np.cos(lat) * np.sin(lon - lo0)
    y = np.cos(la0) * np.sin(lat) - np.sin(la0) * np.cos(lat) * np.cos(lon - lo0)
    keep = cosc > 0
    return x[keep], y[keep]


vmax = max(studies.values())
cmap = mcolors.LinearSegmentedColormap.from_list(
    "studies", plt.colormaps["viridis"](np.linspace(0.30, 1.0, 256)))
norm = mcolors.LogNorm(vmin=1, vmax=vmax)

fig, ax = plt.subplots(figsize=(3.4, 3.4))
ax.add_patch(plt.Circle((0, 0), 1.0, facecolor="#12161b", edgecolor="#ffffff26", lw=0.9, zorder=0))
for f in feats:
    col = LAND if f["iso"] not in studies else cmap(norm(studies[f["iso"]]))
    for ring in f["rings"]:
        x, y = ortho(ring)
        if len(x) >= 3:
            ax.fill(x, y, facecolor=col, edgecolor=OCEAN, linewidth=0.22, zorder=1)
for lat in range(-60, 90, 30):                       # graticule, drawn over the land
    t = np.linspace(-180, 180, 240)
    x, y = ortho(np.column_stack([t, np.full_like(t, lat)]))
    ax.plot(x, y, color="#ffffff1c", lw=0.5, zorder=2)
for lon in range(-180, 180, 30):
    t = np.linspace(-89, 89, 180)
    x, y = ortho(np.column_stack([np.full_like(t, lon), t]))
    ax.plot(x, y, color="#ffffff1c", lw=0.5, zorder=2)
ax.set_xlim(-1.06, 1.06); ax.set_ylim(-1.06, 1.06)
ax.set_aspect("equal"); ax.axis("off")
fig.subplots_adjust(0, 0, 1, 1)
save(fig, "hmtol-card.svg")


# ---------------------------------------------------------- MMC: mini waffle ----
TIER_COLORS = {1: "#91bfdb", 2: "#fee090", 3: "#fc8d59", 4: "#d73027"}
# sample counts per tier, so the card reads the same way as the full waffle on the page
counts = {1: 39782, 2: 77093, 3: 198987, 4: 697260}
total = sum(counts.values())
COLS, ROWS = 46, 10
cells = COLS * ROWS
seq = []
for t in (1, 2, 3, 4):
    seq += [t] * int(round(cells * counts[t] / total))
seq = (seq + [4] * cells)[:cells]

fig, ax = plt.subplots(figsize=(4.6, 1.05))
for i, t in enumerate(seq):
    ax.add_patch(plt.Rectangle((i // ROWS, i % ROWS), 0.82, 0.82,
                               facecolor=TIER_COLORS[t], edgecolor="none"))
ax.set_xlim(-0.4, COLS + 0.4); ax.set_ylim(-0.4, ROWS + 0.4)
ax.set_aspect("equal"); ax.axis("off")
fig.subplots_adjust(0, 0, 1, 1)
save(fig, "mmc-card.svg")
