#!/usr/bin/env python3
"""Re-create the legacy Google Sites archive under reference/legacy-site/.

Idempotent and dependency-free (stdlib only). Reproduces:
  raw/*.html      the five pages as served
  content/*.md    extracted copy
  assets/         images at original resolution + _manifest.csv

11 assets served from /sitesv/ URLs return 403 to anonymous requests and can only
be retrieved via Google Takeout; they are recorded as ERROR rows in the manifest.
"""
import csv, html, os, re, urllib.request

BASE = "http://www.poopomics.com/"
PAGES = {"": "home", "mmc": "mmc", "research": "research",
         "people": "people", "publications": "publications"}
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "reference", "legacy-site")


def get(url, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()


def to_markdown(s):
    s = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", s)
    s = re.sub(r"(?i)<h([1-6])[^>]*>", lambda m: "\n\n" + "#" * int(m.group(1)) + " ", s)
    s = re.sub(r"(?i)</h[1-6]>", "\n\n", s)
    s = re.sub(r"(?i)<(br|/p|/div|/li|/tr)[^>]*>", "\n", s)
    s = re.sub(r"(?i)<li[^>]*>", "- ", s)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    s = re.sub(r"[ \t\xa0]+", " ", s)
    out, prev = [], None
    for line in (l.strip() for l in s.split("\n")):
        if not line:
            if out and out[-1] == "":
                continue
            out.append("")
            continue
        if line == prev or (len(line) < 2 and not line.isdigit()):
            continue
        out.append(line)
        prev = line
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


def main():
    for d in ("raw", "content", "assets"):
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)

    urls = {}
    img_re = re.compile(r"https://lh[0-9]\.googleusercontent\.com/[^\s\"'\\)]+")
    for path, name in PAGES.items():
        raw = get(BASE + path).decode("utf-8", "replace")
        open(f"{ROOT}/raw/{name}.html", "w").write(raw)
        open(f"{ROOT}/content/{name}.md", "w").write(to_markdown(raw))
        for u in dict.fromkeys(img_re.findall(raw)):
            urls.setdefault(u, name)
        print(f"  {name:14} page + copy")

    rows, per_page = [], {}
    for url, page in urls.items():
        per_page[page] = per_page.get(page, 0) + 1
        name = f"{page}-{per_page[page]:02d}"
        # =s0 asks for the upload rather than the downscaled render
        target = re.sub(r"=[sw]\d+.*$", "=s0", url) if re.search(r"=[sw]\d+", url) else url
        for cand in (target, url):
            try:
                d = get(cand)
            except Exception as e:
                err = str(e)[:60]
                continue
            ext = "png" if d[:4] == b"\x89PNG" else "jpg" if d[:3] == b"\xff\xd8\xff" else "bin"
            open(f"{ROOT}/assets/{name}.{ext}", "wb").write(d)
            rows.append([name, page, ext, f"{len(d)/1024:.0f}KB", url])
            break
        else:
            rows.append([name, page, "ERROR", err, url])

    with open(f"{ROOT}/assets/_manifest.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "page", "type", "size", "source_url"])
        w.writerows(rows)
    ok = sum(1 for r in rows if r[2] != "ERROR")
    print(f"\n  assets: {ok}/{len(rows)} downloaded; {len(rows)-ok} need Google Takeout")


if __name__ == "__main__":
    main()
