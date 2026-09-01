"""Build the homepage face band: three long horizontal strips of snug square portraits.

Each strip is one image; the page shows it twice side by side and drifts it, so the band reads
as an endless wall of people. Faces are interleaved across sources so the strips mix cohorts
rather than showing all of one meeting together.

Run: python3 make_collage.py
"""
import json, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "strips")
ROWS = 3
FACE = 76          # css px
GAP = 2
SCALE = 2          # retina


def main():
    idx = json.load(open(os.path.join(HERE, "faces_index.json")))
    # round-robin the sources so each strip is a mix, and keep it deterministic
    by_src = {}
    for e in idx:
        by_src.setdefault(e["source"], []).append(e["file"])
    order, pools = [], [list(v) for v in by_src.values()]
    while any(pools):
        for pl in pools:
            if pl:
                order.append(pl.pop(0))
    per = -(-len(order) // ROWS)
    os.makedirs(OUT, exist_ok=True)

    cell = (FACE + GAP) * SCALE
    for r in range(ROWS):
        chunk = order[r * per:(r + 1) * per]
        if not chunk:
            continue
        w = cell * len(chunk)
        strip = Image.new("RGB", (w, cell), "#0b0c0e")
        for i, f in enumerate(chunk):
            im = Image.open(os.path.join(HERE, "faces", f)).convert("RGB")
            im = im.resize((FACE * SCALE, FACE * SCALE), Image.LANCZOS)
            strip.paste(im, (i * cell + GAP * SCALE // 2, GAP * SCALE // 2))
        p = os.path.join(OUT, "band-%d.jpg" % (r + 1))
        strip.save(p, quality=68, optimize=True, progressive=True)
        print("band-%d  %d faces  %dx%d  %.0f KB"
              % (r + 1, len(chunk), strip.width, strip.height, os.path.getsize(p) / 1024))
    # per-face tiles for the labelled grid on the people page (named first, unnamed last)
    tiles = os.path.join(HERE, "tiles")
    os.makedirs(tiles, exist_ok=True)
    for f in os.listdir(tiles):
        os.remove(os.path.join(tiles, f))
    TILE = 184
    for e in idx:
        im = Image.open(os.path.join(HERE, "faces", e["file"])).convert("RGB")
        im = im.resize((TILE, TILE), Image.LANCZOS)
        im.save(os.path.join(tiles, e["file"]), quality=78, optimize=True)
    kb = sum(os.path.getsize(os.path.join(tiles, f)) for f in os.listdir(tiles)) / 1024
    print("tiles    %d files  %dpx  %.0f KB total" % (len(idx), TILE, kb))

    print("\ntotal faces: %d  ·  css cell %dpx" % (len(order), FACE + GAP))


if __name__ == "__main__":
    main()
