"""Pull the chosen Wikimedia Commons photos and record their licence and author.

Only files whose licence is public domain, CC0 or CC BY are taken — nothing share-alike, so
nothing on the page inherits a licence obligation of its own. Every credit is written to
news/credits.json and shown under the photo it belongs to.
"""
import json, os, re, urllib.parse, urllib.request
from PIL import Image
import io

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "poopomics-site-build/1.0 (research group site; sdegregori@health.ucsd.edu)"}
ALLOWED = ("public domain", "cc0", "cc by 2.0", "cc by 3.0", "cc by 4.0", "no restrictions")

WANT = {
    "unc": 'File:The "Old Well", center of campus, University of North Carolina, Chapel Hill.jpg',
    "ucsd": "File:Geisel Library, UCSD - Noviembre 2023.jpg",
    "cambridge": "File:Renaissance (English) - Cambridge, UK - Cambridge University "
                 "(Trinity College, Nevile's Court).jpg",
    "asm-venue": "File:Walter E. Washington Convention Center 122.jpg",
}


def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def main():
    credits = {}
    for stem, title in WANT.items():
        url = API + "?" + urllib.parse.urlencode(
            {"action": "query", "format": "json", "titles": title,
             "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1100})
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            d = json.load(r)
        page = list(d["query"]["pages"].values())[0]
        ii = (page.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata", {})
        lic = strip((em.get("LicenseShortName") or {}).get("value"))
        artist = strip((em.get("Artist") or {}).get("value"))
        if not any(a in lic.lower() for a in ALLOWED):
            print("  !! skipping %s — licence %r is not on the allowed list" % (stem, lic))
            continue
        thumb = ii.get("thumburl")
        with urllib.request.urlopen(urllib.request.Request(thumb, headers=UA), timeout=60) as r:
            raw = r.read()
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        im.thumbnail((1000, 1000), Image.LANCZOS)
        out = os.path.join(HERE, stem + ".jpg")
        im.save(out, quality=82, optimize=True, progressive=True)
        credits[stem] = {"title": page["title"], "licence": lic, "artist": artist,
                         "source": "https://commons.wikimedia.org/wiki/" +
                                   urllib.parse.quote(page["title"].replace(" ", "_"))}
        print("  %-10s %-16s %-28s %5.0f KB" % (stem, lic, artist[:28],
                                                os.path.getsize(out) / 1024))
    json.dump(credits, open(os.path.join(HERE, "credits.json"), "w"), indent=1)
    print("\n%d photos, credits written to news/credits.json" % len(credits))


if __name__ == "__main__":
    main()
