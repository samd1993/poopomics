"""Search Wikimedia Commons for a freely licensed photo per news item and report its licence.

Nothing is downloaded here — this only lists candidates with their licence, artist and credit so
the choice can be made deliberately. `fetch_photos.py` then pulls the ones chosen.
"""
import json, sys, urllib.parse, urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "poopomics-site-build/1.0 (research group site; contact sdegregori@health.ucsd.edu)"}
OK = ("cc0", "public domain", "cc by", "cc-by", "attribution")   # share-alike flagged separately


def api(params):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def search(term, limit=6):
    d = api({"action": "query", "generator": "search", "gsrsearch": term,
             "gsrnamespace": 6, "gsrlimit": limit,
             "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 1000})
    out = []
    for p in (d.get("query", {}).get("pages") or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata", {})
        g = lambda k: (em.get(k) or {}).get("value", "")
        out.append(dict(title=p.get("title"), lic=g("LicenseShortName"),
                        artist=g("Artist"), credit=g("Credit"),
                        thumb=ii.get("thumburl", ""), w=ii.get("width"), h=ii.get("height")))
    return out


if __name__ == "__main__":
    for term in sys.argv[1:]:
        print("\n=== %s" % term)
        for c in search(term):
            import re
            clean = lambda s: re.sub(r"<[^>]+>", "", s or "")[:70]
            print("  %-58s %-18s %s" % (c["title"][5:63], c["lic"][:18], clean(c["artist"])))
            print("      %dx%d  %s" % (c["w"] or 0, c["h"] or 0, c["thumb"][:100]))
