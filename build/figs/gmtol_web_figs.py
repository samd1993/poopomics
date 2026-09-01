"""Crop single panels out of the GMToL journal figures and recolour them for a dark page.

No plotting source for these exists on this machine — they are finished Illustrator-era art —
so the web versions are crops of the 300 dpi PNG masters. Crop boxes are in the master's own
pixel coordinates and were set by eye against the manuscript legends.

The recolour only touches the achromatic ink: black words and lines become white, the white
paper becomes transparent, greys travel smoothly between the two, and anything with colour in
it is left exactly as it was. Output is WebP with alpha so it drops onto the page background.

NOTE on naming: the FILE names do not match the manuscript figure numbers.
  GMTOL_Figure_1_wNewTree_300dpi.png  ==  manuscript Figure 2  (host phylogeny + phylum bars)
  PCOA_Final_PNG_300dpi.png           ==  manuscript Figure 3  (PCoA, diversity, heatmap)
  GMTOL_Intro_Fig.svg                 ==  manuscript Figure 1  (workflow) — vector, see below
"""
import os
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "gmtol")
SRC = ("/Users/samde/Library/CloudStorage/OneDrive-UniversityofCalifornia,SanDiegoHealth/"
       "TOL2024/figs/Final Figures")

# Relative saturation (max-min)/max, not absolute: a dark navy like Bacillota_A has a small
# absolute spread but is unmistakably a colour, and must not be repainted as grey ink.
SAT_LO, SAT_HI = 0.06, 0.16

PANELS = [
    ("GMTOL_Figure_1_wNewTree_300dpi.png", (130, 170, 1560, 1500), "gmtol-host-phylogeny", 1200),
    ("PCOA_Final_PNG_300dpi.png",          (0,    85, 1840, 1500), "gmtol-pcoa-host-class", 1200),
    ("PCOA_Final_PNG_300dpi.png",          (95, 1600, 1620, 2680), "gmtol-diversity-host-class", 1200),
]


def darkify(im):
    """White paper -> transparent, black ink -> white, colour untouched."""
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    mx = a.max(2)
    sat = (mx - a.min(2)) / np.maximum(mx, 1.0)

    # how "coloured" each pixel is, 0 = pure grey, 1 = clearly coloured
    t = np.clip((sat - SAT_LO) / (SAT_HI - SAT_LO), 0.0, 1.0)[..., None]

    ink_rgb = np.full_like(a, 255.0)               # grey pixels all become white...
    ink_a = 255.0 - mx                             # ...at the opacity of how dark they were
    col_a = np.full_like(mx, 255.0)

    rgb = ink_rgb * (1 - t) + a * t
    alpha = ink_a * (1 - t[..., 0]) + col_a * t[..., 0]
    out = np.dstack([rgb, alpha[..., None]]).astype(np.uint8)
    return Image.fromarray(out)


def main():
    os.makedirs(OUT, exist_ok=True)
    for src, box, stem, w in PANELS:
        im = Image.open(os.path.join(SRC, src)).crop(box)
        im = darkify(im)
        im.thumbnail((w, w * 4), Image.LANCZOS)
        p = os.path.join(OUT, stem + ".webp")
        im.save(p, "WEBP", quality=84, method=6)
        print("wrote %-34s %s  %6.0f KB" % (os.path.basename(p), im.size,
                                            os.path.getsize(p) / 1024))


if __name__ == "__main__":
    main()
