"""Cut every face we have into a uniform square portrait for the homepage collage.

Three kinds of source:
  portrait  — one person, already framed (legacy site people-01..26, MMC slide headshots)
  group     — several people in one frame (the UCSD 2025 team photo)
  grid      — a Zoom gallery screenshot (the MMC meeting snapshots)

Faces are found with OpenCV's Haar cascades (frontal, then profile as a second pass), then the
box is expanded to include hair and chin and squared off. A portrait with no detection falls
back to an upper-centre square, which is where a face sits in a headshot anyway.

Run with the isolated venv:  ../.venv-faces/bin/python make_faces.py
"""
import os, glob, json, sys
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import namekey

HERE = os.path.dirname(os.path.abspath(__file__))
LEG  = os.path.abspath(os.path.join(HERE, "..", "..", "reference", "legacy-site", "assets"))
OUT  = os.path.join(HERE, "faces")
SIZE = 288
# the three studio portraits are also shown large in the news section, where 288 px is
# visibly soft on a retina screen; only a handful of files, so the extra weight is small
SIZE_BETTER = 640
MARGIN = 0.62            # box expansion; Haar boxes are tight on the face

# Haar finds a few things that are not people, and the two Zoom screenshots are of the same
# meeting, so some attendees appear twice. Numbers are stable for a given set of inputs — they
# were read off faces/_sheet.jpg. Rerun the sheet after changing any source.
# 72 and 80 are attendees the correlation pass missed — same person, second screenshot
# Crops to throw away, read off faces/_named.jpg: two landscape submissions where the person is a
# speck, a photo of a banner, a near-black frame, a PDF that converted to a tiny figure, and three
# mis-cropped Zoom tiles (a jar on the team-photo table, a nested gallery, a two-name fragment).
# Keyed by (source, file, which detection) rather than by output number — adding a source used to
# shift every number and silently drop the wrong faces.
DROP = {
    ("photos", "photo-007.png", 0),        # Akshobya Pant — near-black frame
    ("photos", "photo-032.jpg", 0),        # a Hopkins banner, no face
    ("photos", "photo-089.jpeg", 0),       # landscape, person is a speck
    ("photos", "photo-090.jpeg", 0),       # the same, second submission
    ("photos", "photo-122.png", 0),        # a PDF that converted to a tiny figure
    ("photos", "photo-134.jpg", 0),        # near-black outdoor frame
    ("ucsd-team", "home-04.jpg", 0),       # a jar on the table
    ("mmc-zoom-1", "mmc-04.jpg", 0),       # tile fragment carrying two names
    ("mmc-zoom-2", "mmc-07.jpg", 0),       # a nested gallery inside one tile
}

# Zoom writes each attendee's display name into their tile, so the gallery screenshots carry
# their own key. Both screenshots are the same 5x5 gallery, scrolled — zoom-2's first two rows
# repeat zoom-1's last two — so naming the cells also does the de-duplication exactly, by name,
# instead of by image similarity. Read off the screenshots by eye.
GRID = (5, 5)
GRID_BOX = (73, 70, 369.4, 207.0)      # x0, y0, cell width, cell height, in source pixels
ZOOM_NAMES = {
    "mmc-zoom-1": [
        ["Fnu Babita", "Luz Letona", "Samuel Degregori", "Claudio Franc", "Khanh Nguyen"],
        ["Lia Lucas", "Christine Woo", "Akshaya Mohan", "Alex Nath", "Ritvik Vudatha"],
        ["Isabelle Li", "rama", "Noah Hebdon", "Ellen Tang", "Saketh Nallapaty"],
        ["Annie Huang", "Victor Ceballos", "Aniqa Ahmed", "Ariadne Garcia Reyes", "Shloka Lakka"],
        ["Micah", "Nathalia Franco", "Sarah Tan", "David Zhao", "Vyasa Hari"],
    ],
    "mmc-zoom-2": [
        ["Aniqa Ahmed", "Ariadne Garcia Reyes", "Shloka Lakka", "Micah", "Nathalia Franco"],
        ["Sarah Tan", "David Zhao", "Vyasa Hari", "Alan Li", "Ben Alfinito"],
        ["Emily Lam", "Ana-Laura Tamez", "Rohan Raj Butani", "Hubert's iPhone", "Andre Fortes"],
        ["Noah O'Connor", "Laya Devulapalli", "Derek Wang", "Nicolas Rodrigo", "Nidhi Iyengar"],
        ["Tomisin Adebari", "Roger's iPhone", "Sonija Lam", "Maya Balakumaran", "Benjamin Lam"],
    ],
}

# The MMC headshot slide labels every portrait; read out of ppt/slides/slide1.xml by matching
# each picture to the caption centred beneath it.
SLIDE_NAMES = {
    "image1.jpeg": "Harrison Gu", "image2.jpeg": "Harrison Martel",
    "image3.jpeg": "Ariadne Reyes", "image4.png": "David Kobobel",
    "image5.jpeg": "Emily Song", "image6.jpeg": "Daniel Hutcherson",
    "image7.png": "Dmitry Kisselev", "image8.jpeg": "Jeffrey Bohrer",
    "image9.png": "Weil Chu", "image10.png": "Isabella Huang",
    "image11.png": "Jack Anderson",
}

# Haar picks the LARGEST detection, which on a couple of wide studio shots is a bright rectangle
# of wall rather than the person. Boxes here (x, y, w, h in source pixels) override it.
FORCE_BOX = {
    "photo-079.jpg": (1200, 540, 540, 630),      # Malleeka Suy — wall beat the face
}

# Zoom display names that are a device, not a person
NOT_A_NAME = ("iphone", "ipad", "'s phone", "android")

FRONT = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
ALT   = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml")
PROF  = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")

# Replacements sent in after the fact come first of all, so they beat every earlier crop of the
# same person. The file name is the person's name.
SOURCES = (
    [("portrait", p, "better")
     for p in sorted(glob.glob(os.path.join(HERE, "src", "better", "*")))
     if not os.path.basename(p).startswith(".")] +
    [("portrait", p, "photos")
     for p in sorted(glob.glob(os.path.join(HERE, "src", "photos", "photo-*")))] +
    [("portrait", os.path.join(LEG, os.path.basename(p)), "legacy")
     for p in sorted(glob.glob(os.path.join(LEG, "people-*")))] +
    [("portrait", p, "mmcslide")
     for p in sorted(glob.glob(os.path.join(HERE, "src", "mmcslide", "image*")))
     if not os.path.basename(p).startswith("_")] +
    [("group", os.path.join(LEG, "home-04.jpg"), "ucsd-team"),
     ("grid",  os.path.join(LEG, "mmc-04.jpg"),  "mmc-zoom-1"),
     ("grid",  os.path.join(LEG, "mmc-07.jpg"),  "mmc-zoom-2")]
)


def detect(gray, min_frac):
    """Union of the three cascades, de-duplicated by overlap."""
    h, w = gray.shape
    mn = int(min(h, w) * min_frac)
    boxes = []
    for cc, scale, nb in ((FRONT, 1.08, 6), (ALT, 1.06, 6), (PROF, 1.08, 7)):
        for (x, y, bw, bh) in cc.detectMultiScale(gray, scale, nb, minSize=(mn, mn)):
            boxes.append([int(x), int(y), int(bw), int(bh)])
    keep = []
    for b in sorted(boxes, key=lambda b: -b[2] * b[3]):
        if all(iou(b, k) < 0.28 for k in keep):
            keep.append(b)
    return keep


def iou(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    x1, y1 = max(ax, bx), max(ay, by)
    x2, y2 = min(ax + aw, bx + bw), min(ay + ah, by + bh)
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    return inter / float(aw * ah + bw * bh - inter or 1)


def square_crop(img, box):
    """Expand a face box by MARGIN, square it, and keep it inside the frame."""
    h, w = img.shape[:2]
    x, y, bw, bh = box
    cx, cy = x + bw / 2, y + bh / 2 - bh * 0.06        # sit slightly high: hair reads better
    side = max(bw, bh) * (1 + MARGIN)
    side = min(side, h, w)
    x0 = int(round(min(max(cx - side / 2, 0), w - side)))
    y0 = int(round(min(max(cy - side / 2, 0), h - side)))
    s = int(round(side))
    return img[y0:y0 + s, x0:x0 + s]


def upper_centre(img):
    h, w = img.shape[:2]
    s = min(h, w)
    x0 = (w - s) // 2
    y0 = 0 if h <= w else int((h - s) * 0.18)
    return img[y0:y0 + s, x0:x0 + s]


def signature(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, (32, 32), interpolation=cv2.INTER_AREA).astype(np.float32).ravel()
    g -= g.mean()
    nrm = np.linalg.norm(g)
    return g / nrm if nrm else g


def corr(a, b):
    return float(np.dot(a, b))


def name_for(kind, tag, path, box, legacy_names, photo_names):
    """Whatever name the source knows for this face, or '' if it does not know one."""
    base = os.path.basename(path)
    if tag == "better":
        return os.path.splitext(base)[0]
    if tag == "photos":
        return photo_names.get(base, "")
    if tag == "legacy":
        return legacy_names.get(base, "")
    if tag == "mmcslide":
        return SLIDE_NAMES.get(base, "")
    grid = ZOOM_NAMES.get(tag)
    if grid and box:
        x0, y0, cw, ch = GRID_BOX
        x, y, bw, bh = box
        col = int(min(max((x + bw / 2 - x0) // cw, 0), GRID[1] - 1))
        row = int(min(max((y + bh / 2 - y0) // ch, 0), GRID[0] - 1))
        n = grid[row][col]
        return "" if any(t in n.lower() for t in NOT_A_NAME) else n
    return ""


def norm(n):
    return namekey.key(n)


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, "*.jpg")):
        os.remove(f)
    index, n = [], 0
    named, dupes = set(), []
    legacy_names = {p["asset"]: p["name"]
                    for p in json.load(open(os.path.join(HERE, "legacy_people.json")))}
    photo_names = {p["file"]: p["name"]
                   for p in json.load(open(os.path.join(HERE, "photos_names.json")))}
    for kind, path, tag in SOURCES:
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None:
            print("  !! unreadable:", path); continue
        plain = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(plain)
        if kind == "portrait":
            # equalising helps dim phone photos and hurts bright studio ones, so try both before
            # falling back to a blind crop — a missed face here is a shoulder on the people page
            forced = FORCE_BOX.get(os.path.basename(path))
            boxes = ([list(forced)] if forced else
                     detect(gray, 0.16)[:1] or detect(plain, 0.16)[:1] or detect(plain, 0.09)[:1])
            crops = [(square_crop(img, boxes[0]), boxes[0])] if boxes else [(upper_centre(img), None)]
            how = "face" if boxes else "fallback"
        else:
            # a group photo or Zoom gallery: every face in the frame, smallest first threshold
            boxes = detect(gray, 0.035 if kind == "grid" else 0.05)
            crops = [(square_crop(img, b), b) for b in boxes]
            how = "faces"
        kept_here = 0
        for k, (c, box) in enumerate(crops):
            if c.size == 0 or min(c.shape[:2]) < 40:
                continue
            # never upsample: a small source gains nothing from being written large, and the
            # crop of a 512 px selfie is well under 640
            px = min(SIZE_BETTER, max(SIZE, min(c.shape[:2]))) if tag == "better" else SIZE
            c = cv2.resize(c, (px, px), interpolation=cv2.INTER_AREA)
            n += 1
            if (tag, os.path.basename(path), k) in DROP:
                continue
            who = name_for(kind, tag, path, box, legacy_names, photo_names)
            if who and norm(who) in named:
                dupes.append((n, who))       # same person, already have a better crop
                continue
            if who:
                named.add(norm(who))
            fn = "face-%03d.jpg" % n
            cv2.imwrite(os.path.join(OUT, fn), c, [cv2.IMWRITE_JPEG_QUALITY, 90])
            index.append({"file": fn, "source": tag, "kind": kind,
                          "name": namekey.PREFERRED.get(namekey.key(who), who) if who else ""})
            kept_here += 1
        print("  %-12s %-22s %s -> %d found, %d kept"
              % (tag, os.path.basename(path), how, len(crops), kept_here))
    json.dump(index, open(os.path.join(HERE, "faces_index.json"), "w"), indent=1)
    have = sum(1 for e in index if e["name"])
    print("\n%d faces kept of %d cut · %d named, %d unnamed · %d dropped by hand"
          % (len(index), n, have, len(index) - have, len(DROP)))
    print("repeat attendees skipped: %s" % ", ".join(w for _, w in dupes))


if __name__ == "__main__":
    main()
