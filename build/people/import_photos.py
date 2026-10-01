"""Unpack photos.zip (a Google Forms file-upload export) into named portrait files.

Google Forms names each upload "<what they uploaded> - <their account name>.<ext>". Neither half
is reliable on its own: some people followed the "FirstName_LastName" instruction and have a junk
account name, others uploaded IMG_6976 from a phone and have a good account name. So both halves
are scored and the better one wins; anything that scores as junk is kept but left unnamed, to be
caught on the contact sheet.

HEIC, PDF and CR3 are converted with sips, which ships with macOS.
Run: python3 import_photos.py
"""
import json, os, re, subprocess, sys, unicodedata, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
# the newest form export wins; earlier ones are kept beside it as received
ZIPS = [os.path.join(HERE, "..", "..", "photos_Sep30_26", "photos.zip"),
        os.path.join(HERE, "..", "..", "photos.zip")]
ZIP = os.path.abspath(next((z for z in ZIPS if os.path.exists(z)), ZIPS[-1]))
# the consortium sheet, read only for names: an upload's two halves are checked against it, so
# "Yue_Fan - Roger Fan" is filed under the member rather than the nickname on the account
SHEET = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "MMC",
                                     "MMC Consortium Members - Clean.xlsx"))
OUT = os.path.join(HERE, "src", "photos")

# account names that are handles, jokes or placeholders rather than a person
JUNK = {"sycamorexstreet", "cassketch", "learner know", "ms rg",
        "i_ll eat brownies for life", "i'll eat brownies for life", "image", "headshot",
        "photo", "me", "user", "unknown"}
CONVERT = {".heic", ".pdf", ".cr3", ""}


def looks_like_name(s):
    s = " ".join(s.replace("_", " ").split())
    if not s or s.lower() in JUNK:
        return None
    if re.search(r"[0-9@]", s):
        return None
    toks = s.split()
    if not (1 <= len(toks) <= 4):
        return None
    for t in toks:
        core = "".join(c for c in unicodedata.normalize("NFC", t) if c.isalpha() or c in "-'.")
        if len(core) != len(t):
            return None
        if len(core.rstrip(".")) < 2 and len(toks) == 1:
            return None          # a lone initial is not a name; a middle initial is fine
    return " ".join(t if t[:1].isupper() and not t.isupper() else t.capitalize() for t in toks)


def member_keys():
    if not os.path.exists(SHEET):
        return set()
    import openpyxl
    from member_key import key
    rows = openpyxl.load_workbook(SHEET, read_only=True).worksheets[0].iter_rows(values_only=True)
    head = next(rows)
    i = head.index("Full Name (as listed in consortium)")
    return {key(r[i]) for r in rows if r[i]}


MEMBERS = None

# uploads whose name is a nickname, initial or script the sheet does not carry; each matched to the
# only member it can be (Staleny is in Yvenica's address). Felix Liang is left unmatched: Xiang
# Feng Liang is plausible but nothing on the sheet confirms it.
UPLOAD_NAMES = {
    "Staleny Calixte": "Yvenica Calixte",
    "Trisha D": "Trisha Dutta",
    "Jake A": "Jake Albert",
    "Savio Stephan Ms": "Savio Stephan",
    "Andrea Ortiz": "Andrea Ortiz Iglesias",
    "Mariana Hurutado": "Mariana Hurutado-Rodriguez",
    "\u6e29\u535a\u680b": "Bodong Wen",
    "Eve": "Evelina Iskhakova",
    "Ritvik V": "Ritvik Vudatha",
    "Mohak": "Mohak Prakash",
}


def parse(entry):
    """(name or '', extension) for one zip entry."""
    base = os.path.basename(entry)
    stem, ext = os.path.splitext(base)
    ext = ext.lower()
    if " - " in stem:
        uploaded, account = stem.rsplit(" - ", 1)
    else:
        uploaded, account = stem, ""
    global MEMBERS
    if MEMBERS is None:
        MEMBERS = member_keys()
    # a half that names a consortium member wins outright
    if MEMBERS:
        from member_key import key
        for cand in (uploaded, account):
            n = looks_like_name(re.sub(r"\(\d+\)$", "", cand))
            if n and key(n) in MEMBERS:
                return n, ext
    # the account name is a real person's name more often than the uploaded filename is
    for cand in (account, uploaded):
        n = looks_like_name(cand)
        if n:
            # "Lastname Firstname" from the upload half reads wrong; the account half never is
            return n, ext
    return "", ext


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    z = zipfile.ZipFile(ZIP)
    index, unnamed, converted = [], 0, 0
    for i, entry in enumerate(sorted(n for n in z.namelist() if not n.endswith("/"))):
        name, ext = parse(entry)
        name = UPLOAD_NAMES.get(name, name)
        stem = "photo-%03d" % (i + 1)
        raw = os.path.join(OUT, stem + (ext or ".bin"))
        with open(raw, "wb") as fh:
            fh.write(z.read(entry))
        if ext in CONVERT:
            png = os.path.join(OUT, stem + ".png")
            r = subprocess.run(["sips", "-s", "format", "png", raw, "--out", png],
                               capture_output=True)
            os.remove(raw)
            if r.returncode != 0 or not os.path.exists(png):
                print("  !! could not convert %s (%s)" % (os.path.basename(entry), ext))
                continue
            raw = png; converted += 1
        index.append({"file": os.path.basename(raw), "name": name, "source_entry": entry})
        if not name:
            unnamed += 1
            print("  no name from: %s" % os.path.basename(entry))
    json.dump(index, open(os.path.join(HERE, "photos_names.json"), "w"), indent=1,
              ensure_ascii=False)
    print("\n%d photos, %d named, %d unnamed, %d converted with sips"
          % (len(index), len(index) - unnamed, unnamed, converted))


if __name__ == "__main__":
    main()
