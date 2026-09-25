"""Assemble the MMC Consortium site — the Microbiome Metadata Crisis on its own.

Reuses build_site.py's styling, figures and helpers so the two sites stay one design, but carries
only MMC material, and its People page is driven by the consortium's own member sheet rather than
by everyone who has ever worked on poopomics.

    python3 build_mmc.py            # mmc-v1.html + mmc-v1-artifact.html, everything inlined
    python3 build_mmc.py --site     # ../mmc-site/, with real asset files, for a host

The member sheet holds personal and university email addresses. Only names are read from it
into the page; nothing else in the sheet is published.
"""
import os, sys, json, random, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.abspath(os.path.join(
    HERE, "..", "..", "..", "MMC", "MMC Consortium Members - Clean.xlsx"))

SITE_MODE = "--site" in sys.argv
if SITE_MODE:
    # build_site.py writes assets wherever this points; keep them out of the main site's folder
    os.environ["POOP_ASSET_DIR"] = os.path.join(HERE, "..", "mmc-site", "assets")
    sys.argv.remove("--site")

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "people"))
import build_site as bs                         # noqa: E402
import namekey                                  # noqa: E402

# build_site assembles its own views on import, which copies their images into the asset folder.
# None of those are used here, so start the folder clean and write only what this page needs.
if SITE_MODE:
    shutil.rmtree(bs.ASSET_DIR, ignore_errors=True)
    os.makedirs(bs.ASSET_DIR, exist_ok=True)

OUT = os.path.join(HERE, "mmc-v1.html")
ART = os.path.join(HERE, "mmc-v1-artifact.html")
MEMBERS_CLAIM = "246"

# Nicknames and full names that are plainly the same person. Kept here rather than in namekey.py
# so the main site's matching is untouched.
ALIASES = {
    "alexander nath": "alex nath",
    "maxwell hong": "max hong",
    "linden stadtlander": "lindy stadtlander",
    "sai malleboyina": "sahithi malleboyina",
    "qin(amy) xia": "amy xia",
    "yuxuan xie": "bree xie",
    "randima dona": "randima bellana",      # listed in full as Randima Hasanthi Bellana Vidanelage Dona
}


def key(name):
    k = namekey.key(name)
    return ALIASES.get(k, k)


# ------------------------------------------------------------------- members ----
def load_members():
    import openpyxl
    wb = openpyxl.load_workbook(SHEET, read_only=True, data_only=True)
    rows = list(wb.worksheets[0].iter_rows(values_only=True))
    head = rows[0]
    col = {h: i for i, h in enumerate(head)}
    name_c = col["Full Name (as listed in consortium)"]
    uni_c, role_c = col["Current University"], col["Roles"]
    out, seen = [], set()
    for r in rows[1:]:
        if not r or not r[name_c]:
            continue
        name = " ".join(str(r[name_c]).split())
        # the sheet has a few people signed up twice; the first row, which carries their roles,
        # is the one kept
        if key(name) in seen:
            continue
        seen.add(key(name))
        out.append({"name": name,
                    "university": (r[uni_c] or "").strip(),
                    "lead": "Project Lead" in (r[role_c] or "")})
    return out


MEMBERS = load_members()
INSTITUTIONS = sorted({m["university"] for m in MEMBERS if m["university"]})

faces = json.load(open(os.path.join(HERE, "people", "faces_index.json")))
face_by_key = {key(e["name"]): e for e in faces if e["name"]}

# the director and the advisor get cards of their own at the top, so they are not repeated below
AT_TOP = {"Sam Degregori": ("Consortium lead", "Postdoctoral fellow, UC San Diego"),
          "Rob Knight": ("Consortium advisor", "Professor, UC San Diego")}
top_keys = {key(n) for n in AT_TOP}

members = [m for m in MEMBERS if key(m["name"]) not in top_keys]
surname = lambda m: m["name"].split()[-1].lower()
# project leads first, then everyone else alphabetically by surname
members.sort(key=lambda m: (not m["lead"], surname(m)))

with_photo = [m for m in members if key(m["name"]) in face_by_key]
without_photo = sorted((m for m in members if key(m["name"]) not in face_by_key), key=surname)

# local face index: the page's own f0..fN classes, pointing at the consortium's portraits only
INDEX = [{"name": m["name"], "file": face_by_key[key(m["name"])]["file"]} for m in with_photo]
bs.FACE_CLASS = {key(e["name"]): i for i, e in enumerate(INDEX)}
bs.FACE_NAME = {key(e["name"]): e["name"] for e in INDEX}


def face_css():
    return "\n".join(".f%d{background-image:url(%s)}"
                     % (i, bs.data_uri("people/tiles/" + e["file"], "image/jpeg"))
                     for i, e in enumerate(INDEX))


# ------------------------------------------------------------------ the band ----
def build_strips():
    """Three rolling strips of consortium members only, in the main site's strip format."""
    from PIL import Image
    tiles = [os.path.join(HERE, "people", "tiles", e["file"]) for e in INDEX]
    order = list(range(len(tiles)))
    random.Random(7).shuffle(order)             # fixed seed: the band does not reshuffle per build
    rows = [order[i::3] for i in range(3)]
    size = 156                                  # strips are drawn at 2x the 78px row height
    out_dir = os.path.join(HERE, "people", "strips-mmc")
    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    for i, row in enumerate(rows, 1):
        strip = Image.new("RGB", (size * len(row), size))
        for j, t in enumerate(row):
            strip.paste(Image.open(tiles[t]).convert("RGB").resize((size, size), Image.LANCZOS),
                        (j * size, 0))
        p = os.path.join(out_dir, "band-%d.jpg" % i)
        strip.save(p, quality=68, optimize=True, progressive=True)
        paths[i] = os.path.relpath(p, HERE)
    return paths


# --------------------------------------------------------------------- views ----
def home_view():
    nums = [(MEMBERS_CLAIM, "members"), (str(len(INSTITUTIONS)), "institutions"),
            ("3,145", "studies surveyed"), ("1M+", "samples")]
    bignums = "".join('<div><b>%s</b><span>%s</span></div>' % n for n in nums)
    # News here is the consortium's own: its paper, and acceptances of people who are members.
    # An acceptance whose person is not on the member sheet is left off, for the same reason the
    # medical-school ones are: they are not part of the consortium.
    member_keys = {key(m["name"]) for m in MEMBERS}
    keep = []
    for heading, items in bs.NEWS:
        if heading == "Publications":
            items = [it for it in items if "Sample Size" in it["title"]]
        elif heading in ("PhD Program Acceptances!", "Masters Program Acceptances!"):
            items = [it for it in items if key(it.get("portrait") or "") in member_keys]
        else:
            continue
        if items:
            keep.append((heading, items))
    bs.NEWS = keep
    return f'''<section class="p-hero">
  <div class="p-eyebrow">Microbiome Metadata Crisis</div>
  <h1>The MMC Consortium</h1>
  <p class="p-lead">Most published microbiome data is public, but not reusable. The consortium is
  {MEMBERS_CLAIM} undergraduates, graduate students, postdocs and professors across
  {len(INSTITUTIONS)} institutions, reading the clinical human microbiome literature by hand to
  find out how much of it can actually be reused.</p>
  <div class="p-bignums">{bignums}</div>
</section>

<div class="p-people">{bs.band()}</div>

<p class="p-cap p-wide p-after-nums"><a href="#findings">See the findings</a> &nbsp;·&nbsp;
<a href="#people">Meet the members</a> &nbsp;·&nbsp; <a href="#policies">Consortium policies</a></p>

{bs.news_view()}'''


def people_view():
    legacy = json.load(open(os.path.join(HERE, "people", "legacy_people.json")))
    by_name = {p["name"]: p for p in legacy}
    cards = "".join(
        '<div class="p-lead-card">%s<div><b>%s</b><i>%s</i><span>%s</span></div></div>'
        % (bs.img("../reference/legacy-site/assets/" + by_name[n]["asset"], n,
                  "image/png" if by_name[n]["asset"].endswith("png") else "image/jpeg"),
           n, role, where)
        for n, (role, where) in AT_TOP.items() if n in by_name)
    tiles = "".join(bs.face_tile(i, e, "Project lead" if with_photo[i]["lead"] else None)
                    for i, e in enumerate(INDEX))
    names = "".join('<li>%s</li>' % m["name"] for m in without_photo)
    return f'''<section class="p-intro">
  <h1 class="p-title-accent">Consortium members</h1>
</section>

<div class="p-leads p-leads-top p-leads-two">{cards}</div>

<h2 class="p-sec-h">Members</h2>
<div class="p-grid">{tiles}</div>

<ul class="p-names p-names-after">{names}</ul>'''


POLICIES = '''<section class="p-intro">
  <h1 class="p-title-accent">Consortium policies</h1>
  <p class="p-lead">Please find below our Consortium policies. We will notify members if there are
  any changes to what is listed here.</p>
</section>

<div class="p-policy">
  <section>
    <h2>Joining</h2>
    <p>You join the consortium by joining any of the MMC projects coordinated by Sam Degregori, Rob
    Knight, and Project Leads. Contact Sam and he will send you the membership form.</p>
  </section>

  <section>
    <h2>Criteria for membership</h2>
    <p>You become an official member by completing the minimum required data-curation effort for
    an MMC project, a threshold set at the start of each project, and/or by contributing to an MMC
    manuscript.</p>
  </section>

  <section>
    <h2>Authorship</h2>
    <p>Unless stated otherwise, consortium members are listed as co-authors under the MMC
    Consortium name. Once you are a member, you are considered a co-author on every MMC paper
    submitted after you joined, as long as we are able to reach you with manuscript drafts.</p>
  </section>

  <section>
    <h2>What you will be sent</h2>
    <p>Every member is sent the manuscript at three points:</p>
    <ul>
      <li>before it is first submitted;</li>
      <li>before any resubmission; and</li>
      <li>when it is published, with its citation and DOI.</li>
    </ul>
    <p class="p-policy-after">If we cannot reach you at the email address you gave us, we will take
    it that you no longer wish to be part of the consortium. If your university address may expire,
    please give us an alternative address when you sign up.</p>
  </section>

  <section>
    <h2>Leaving</h2>
    <p>To leave the consortium, contact Sam Degregori. You will be removed from our tracking list,
    this website and the mailing list.</p>
  </section>
</div>'''

EXTRA_CSS = """
.p-leads-two{grid-template-columns:repeat(2,minmax(0,1fr));max-width:760px}
.p-names-after{margin-top:28px}
.p-policy{display:flex;flex-direction:column;gap:30px;margin:26px 0 0;max-width:68ch}
.p-policy h2{font-family:var(--display);margin:0 0 8px;font-size:22px;font-weight:700;
  letter-spacing:-.015em;line-height:1.25}
.p-policy p,.p-policy li{margin:0;font-size:16px;line-height:1.65;color:var(--lead)}
.p-policy-after{margin-top:14px !important}
.p-policy ul{margin:10px 0 0;padding-left:1.2em;display:flex;flex-direction:column;gap:4px}
@media (max-width:900px){.p-leads-two{grid-template-columns:1fr}}
"""

JS = """
const VIEWS = ['home','findings','people','policies'];
const TITLES = {findings:'Findings', people:'Members', policies:'Policies'};
function show(id){
  if(!VIEWS.includes(id)) id = 'home';
  VIEWS.forEach(v => document.getElementById('view-'+v).classList.toggle('on', v === id));
  document.querySelectorAll('[data-nav]').forEach(a => a.classList.toggle('on', a.dataset.nav === id));
  document.title = id === 'home' ? 'MMC Consortium' : TITLES[id] + ' · MMC Consortium';
  window.scrollTo(0, 0);
}
window.addEventListener('hashchange', () => show(location.hash.slice(1)));
show(location.hash.slice(1));
"""


def build():
    strips = build_strips()
    css = bs.CSS.replace("__BANNER__", bs.data_uri("figs/cards/banner-pcoa.svg", "image/svg+xml"))
    nav = "".join('<a href="#%s" data-nav="%s">%s</a>' % (v, v, lbl) for v, lbl in
                  [("home", "Home"), ("findings", "Findings"), ("people", "Members"),
                   ("policies", "Policies")])
    fonts = ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
             'family=Work+Sans:ital,wght@0,300..800;1,300..600'
             '&family=Literata:ital,opsz,wght@0,7..72,300..800;1,7..72,300..700'
             '&display=swap">')
    home = home_view()
    people = people_view()
    body = f"""<header class="p-top">
  <div class="p-top-in">
    <a href="#home" class="p-mark">MMC Consortium</a>
    <div class="p-banner" aria-hidden="true"></div>
    <nav class="p-nav">{nav}</nav>
  </div>
</header>

<main>
  <div class="p-wrap">
    <div class="p-view" id="view-home">{home}</div>
    <div class="p-view" id="view-findings">{bs.MMC}</div>
    <div class="p-view" id="view-people">{people}</div>
    <div class="p-view" id="view-policies">{POLICIES}</div>
  </div>
</main>

<div class="p-wrap"><footer class="p-foot">
  <div>The Microbiome Metadata Crisis Consortium</div>
</footer></div>

<script>{JS}</script>"""
    styles = (f"<style>{css}</style>\n<style>{bs.band_css(strips)}</style>\n"
              f"<style>{face_css()}</style>\n<style>{EXTRA_CSS}</style>")
    head = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MMC Consortium</title>
{fonts}
{styles}"""
    page = f"<!doctype html>\n<html lang=\"en\">\n<head>\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>"

    if SITE_MODE:
        dest = os.path.join(os.path.dirname(bs.ASSET_DIR), "index.html")
        open(dest, "w").write(page)
        n = len(os.listdir(bs.ASSET_DIR))
        print("wrote mmc-site/index.html  %.2f MB  + %d files in mmc-site/assets"
              % (os.path.getsize(dest) / 1e6, n))
    else:
        open(OUT, "w").write(page)
        open(ART, "w").write(f"<title>MMC Consortium</title>\n{fonts}\n{styles}\n{body}")
        print("wrote mmc-v1.html  %.2f MB" % (os.path.getsize(OUT) / 1e6))

    print("members %d: %d with a photo, %d listed by name; %d institutions"
          % (len(MEMBERS), len(with_photo), len(without_photo), len(INSTITUTIONS)))


if __name__ == "__main__":
    build()
