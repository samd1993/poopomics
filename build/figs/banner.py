"""The header banner: a scatter arranged along a stylised gut.

This is **decorative** — a generated point field, not data. Colour runs along the tract rather
than encoding anything measured, and the anatomy is a drawing, not a sampling scheme.
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cards", "banner-pcoa.svg")

import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Cool and complementary to the page's blue accent, and deliberately not the MMC waffle's warm
# tier ramp, which the banner used to borrow.
RAMP = ["#2dd4bf", "#38bdf8", "#818cf8", "#c084fc", "#f472b6"]
N = 620
FIG_W, FIG_H = 16.0, 1.333          # 12:1, the shape of the slot in the masthead
SEED = 5


def tract(t):
    """The centreline of a stylised gut running left to right across the slot, and the tube's
    half-thickness along it: a wide stomach, a coiled small intestine, a wider colon at the end.

    The slot is roughly twelve times wider than it is tall, so the coils read as switchbacks
    rather than as the loops you would draw with room to spare.
    """
    loops = 4.6
    # the coil tightens through the middle and relaxes at both ends
    swing = 0.30 * np.sin(np.pi * np.clip((t - 0.06) / 0.88, 0, 1)) ** 0.7
    mid = 0.50 + swing * np.sin(2 * np.pi * loops * t - 0.6)

    # stomach at the head, small intestine through the body, colon at the tail
    r = np.full_like(t, 0.115)
    head = t < 0.11
    r[head] = 0.115 + 0.20 * np.cos(np.pi * t[head] / 0.22)
    tail = t > 0.86
    r[tail] = 0.115 + 0.13 * np.sin(np.pi * (t[tail] - 0.86) / 0.30)
    return mid, r


def main():
    rng = np.random.default_rng(SEED)
    t = np.sort(rng.random(N))
    mid, r = tract(t)

    # across the tube: dense through the middle, fading at the wall, plus a few points sitting
    # just outside it so the edge stays soft rather than drawn
    u = rng.beta(1.6, 1.6, N) * 2 - 1
    stray = rng.random(N) < 0.06
    u[stray] = rng.normal(0, 1.5, stray.sum())
    y = mid + r * u + rng.normal(0, 0.012, N)

    x = t
    # the field is mapped into the slot's own proportions so it fills the band
    yspan = FIG_H / FIG_W
    y = yspan * np.clip(y, -0.02, 1.02)

    cmap = LinearSegmentedColormap.from_list("banner", RAMP)

    # Both ends fade out, so the field can run on behind the wordmark and the tabs without
    # competing with them. Per-point alpha, baked into the colours rather than set for the whole
    # collection, which is what lets it ramp across the width.
    f = np.clip(np.minimum(x, 1 - x) / 0.22, 0, 1)
    fade = 0.10 + 0.90 * (f * f * (3 - 2 * f))         # smoothstep, so there is no visible seam
    rgba = cmap(x)
    rgba[:, 3] = fade

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    # two fixed sizes rather than a continuous spread: it still reads as depth, and each group
    # shares one marker definition, which keeps the inlined SVG small
    big = rng.random(N) < 0.3
    ax.scatter(x[~big], y[~big], s=26, c=rgba[~big], linewidths=0)
    ax.scatter(x[big], y[big], s=58, c=rgba[big], linewidths=0)
    ax.set_xlim(-0.005, 1.005)
    ax.set_ylim(-0.02 * yspan, 1.02 * yspan)
    ax.axis("off")
    fig.patch.set_alpha(0)
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(OUT, format="svg", transparent=True)
    plt.close(fig)
    print("wrote %-24s %d points  %5.0f KB"
          % (os.path.basename(OUT), N, os.path.getsize(OUT) / 1024))


if __name__ == "__main__":
    main()
