"""Assemble poopomics-v1.html — one self-contained file, five views.

Everything is inlined: the figure SVGs as markup (so the page's Mulish webfont renders their
labels), the GMToL panels and the face collage as data URIs, and the two ported lenses.
Run the scripts in figs/ and people/ first; this only assembles.
"""
import base64, hashlib, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Everything that changes week to week — the news, the roster, the institutions — lives in
# content.yaml so it can be edited without opening this file.
import yaml
CONTENT = yaml.safe_load(open(os.path.join(HERE, "content.yaml"), encoding="utf-8"))

OUT = os.path.join(HERE, "poopomics-v1.html")
ART = os.path.join(HERE, "poopomics-v1-artifact.html")

# Nineteen institutions, the three leading the projects first.
INSTITUTIONS = CONTENT["institutions"]
PEOPLE = CONTENT["people_total"]


# ---------------------------------------------------------------- helpers ----
def svg(path, cls="p-fig-svg"):
    """Inline an .svg as markup, dropping its fixed width/height so it scales to the column."""
    s = open(os.path.join(HERE, path)).read()
    s = "<svg" + s.split("<svg", 1)[1]
    for _ in range(2):
        s = re.sub(r'<svg([^>]*?)\s(?:width|height)="[^"]*"', r"<svg\1", s)
    return '<div class="%s">%s</div>' % (cls, s)


# Two builds come out of this script. The artifact has to be one self-contained file, so every
# asset is inlined as base64. The hosted site does not: writing the images out as real files drops
# a third of their weight (base64 costs 33%), lets the browser cache them, and — because a
# background image on a hidden view is never fetched — means a phone opening the home page does
# not download the 185 portraits behind the People sheet.
ASSET_DIR = None                       # set to a path to switch to file assets
if "--site" in sys.argv:               # must be decided before the views are assembled below
    ASSET_DIR = os.path.abspath(os.path.join(HERE, "..", "site", "assets"))
    # assets are content-hashed, so a stale one is never referenced but would sit there for ever
    if os.path.isdir(ASSET_DIR):
        shutil.rmtree(ASSET_DIR)
    os.makedirs(ASSET_DIR, exist_ok=True)


def data_uri(path, mime):
    src = os.path.join(HERE, path)
    if ASSET_DIR is None:
        b = base64.b64encode(open(src, "rb").read()).decode()
        return "data:%s;base64,%s" % (mime, b)
    name = os.path.basename(path)
    digest = hashlib.sha1(open(src, "rb").read()).hexdigest()[:8]
    stem, ext = os.path.splitext(name)
    out = "%s.%s%s" % (stem.replace(" ", "-"), digest, ext)
    dest = os.path.join(ASSET_DIR, out)
    if not os.path.exists(dest):
        shutil.copyfile(src, dest)
    return "assets/" + out


def img(path, alt, mime="image/webp", cls=""):
    c = ' class="%s"' % cls if cls else ""
    return '<img%s src="%s" alt="%s" loading="lazy" decoding="async">' % (
        c, data_uri(path, mime), alt)


def figure(body, heading, caption, kicker=None, span="half"):
    """span: 'full' for a figure that needs the whole width, 'half' to sit two-up.

    heading may be None for a figure that stands on its caption alone."""
    k = '<div class="p-fig-kicker">%s</div>' % kicker if kicker else ""
    h = '<h3 class="p-fig-h">%s</h3>' % heading if heading else ""
    return f'''<figure class="p-fig p-{span}">
  {k}{h}
  <div class="p-fig-body">{body}</div>
  <figcaption class="p-cap">{caption}</figcaption>
</figure>'''


def figs(*items):
    return '<div class="p-figs">%s</div>' % "\n".join(items)


def note(text):
    return '<div class="p-note">%s</div>' % text


def papers(*items):
    """The papers behind a project. Each item is (title, venue, url); url may be None for work
    that has nowhere to point yet, which is worth saying rather than omitting."""
    rows = []
    for title, venue, url in items:
        head = ('<a href="%s" target="_blank" rel="noopener">%s</a>' % (url, title)) if url \
            else '<span>%s</span>' % title
        rows.append('<li><div class="p-paper-t">%s</div><div class="p-paper-v">%s</div></li>'
                    % (head, venue))
    return ('<section class="p-papers"><h2 class="p-sec-h">Papers</h2><ul>%s</ul></section>'
            % "".join(rows))


BIORXIV = "https://www.biorxiv.org/content/10.64898/2026.04.29.721755v2"


# ------------------------------------------------------------------- home ----
def card(vid, abbr, title, desc, motif, stats):
    st = "".join('<div class="p-stat"><b>%s</b><span>%s</span></div>' % (v, l) for v, l in stats)
    arrow = ('<span class="p-go">See more'
             '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" '
             'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
             'stroke-linejoin="round"><path d="M5 12h13"/><path d="M12.5 5.5 19 12l-6.5 6.5"/>'
             "</svg></span>")
    return f'''    <a href="#{vid}" class="p-card" data-card="{vid}">
      <div class="p-motif">{motif}</div>
      <div class="p-abbr">{abbr}</div>
      <div class="p-card-h">{title}</div>
      <p class="p-card-p">{desc}</p>
      <div class="p-stats">{st}</div>
      {arrow}
      <span class="p-rule"></span>
    </a>'''


def band():
    rows = "".join('<div class="p-row p-row-%d"></div>' % i for i in (1, 2, 3))
    return '<div class="p-band" aria-label="Researchers on the projects">%s</div>' % rows


def band_css():
    """Each strip is drawn twice its own width by repeat-x, then scrolled by exactly one width."""
    from PIL import Image
    out, secs = [], {1: 96, 2: 112, 3: 104}
    for i in (1, 2, 3):
        path = "people/strips/band-%d.jpg" % i
        w = Image.open(os.path.join(HERE, path)).width // 2      # sources are 2x
        rev = " reverse" if i == 2 else ""
        out.append(".p-row-%d{background-image:url(%s);animation:drift%d %ds linear infinite%s}"
                   % (i, data_uri(path, "image/jpeg"), i, secs[i], rev))
        out.append("@keyframes drift%d{from{background-position-x:0}"
                   "to{background-position-x:-%dpx}}" % (i, w))
    return "\n".join(out)


INST_BAND = '<div class="p-inst-band">%s</div>' % "".join(
    '<span>%s</span>' % i.replace(" ", "&nbsp;") for i in INSTITUTIONS)

ARROW_L = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
           'stroke-linecap="round" stroke-linejoin="round"><path d="M15 5 8 12l7 7"/></svg>')
ARROW_R = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
           'stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg>')


def home_view():
    """Cards as a three-up carousel; the people below follow whichever card is centred."""
    return f'''<section class="p-carousel">
  <button class="p-arrow" data-dir="-1" aria-label="Previous project">{ARROW_L}</button>
  <div class="p-track"><div class="p-table" aria-hidden="true"></div>
{card("gmtol", "2021&ndash;present", "Gut Microbiome Tree of Life (GMToL)",
      "Gut microbiomes across the animal kingdom, curated for even coverage of host phylogeny, "
      "diet, ecology and geography.",
      img("figs/cards/gmtol-card.webp", "Zoom into the host phylogeny"),
      [("17,000", "samples"), ("828", "host species")])}
{card("mmc", "2025&ndash;present", "Microbiome Metadata Crisis (MMC)",
      "A decade-scale audit of the field's own record-keeping: most published microbiome data is "
      "public, but not reusable.",
      svg("figs/cards/mmc-card.svg", "p-motif-svg"),
      [("3,300", "studies"), ("600k+", "samples"),
       ("450", "students, 19 institutions")])}
{card("hmtol", "2024&ndash;present", "Human Microbiome Tree of Life (HMToL)",
      "The human-focused successor: a global collection that deliberately reaches the populations "
      "the literature has left out.",
      svg("figs/cards/hmtol-card.svg", "p-motif-svg"),
      [("16,956", "samples"), ("70", "countries")])}
  </div>
  <button class="p-arrow" data-dir="1" aria-label="Next project">{ARROW_R}</button>
</section>

<h2 class="p-built">{TEAM_LABEL["mmc"]}</h2>

<div class="p-people">
{band()}
{TEAM_PANELS}
</div>

{INST_BAND}

<section class="p-cohort p-cohort-after">
  <p class="p-lead p-lead-big">A large-scale citizen science effort</p>
  <div class="p-bignums">
    <div><b>{PEOPLE}</b><span>undergraduates, grads, postdocs &amp; professors</span></div>
    <div><b>{len(INSTITUTIONS)}</b><span>institutions</span></div>
    <div><b>3</b><span>main projects</span></div>
    <div><b>8</b><span>undergraduate-led subprojects</span></div>
    <div><b>1</b><span>publication</span></div>
    <div><b>2</b><span>preprints</span></div>
    <div><b>2</b><span>submissions under review</span></div>
  </div>
  <p class="p-cap p-wide p-after-nums"><a href="#people">See the People page</a></p>
</section>

{news_view()}'''



# ---------------------------------------------------------------------- news ----
# Both publications were checked against Crossref/PMC rather than typed from memory; the poster
# details come off the photograph of the board.
def _news_item(d):
    """content.yaml carries only what an item has; the renderers expect every key present."""
    pic = d.get("pic") or {}
    return dict(title=d["title"], note=d["note"], url=d.get("url"), meta=d.get("meta"),
                date=d.get("date"), people=d.get("people"), portrait=d.get("portrait"),
                photo=d.get("photo"), flip=d.get("flip", False),
                pic=(pic.get("kind"), pic.get("ref")))


NEWS = [(g["heading"], [_news_item(i) for i in g["items"]]) for g in CONTENT["news"]]


CREDITS = json.load(open(os.path.join(HERE, "news", "credits.json")))


def news_pic(it):
    """The picture beside a news item: its own photo, a Commons photo, or a project graphic."""
    kind, ref = it.get("pic", (None, None))
    if it.get("photo"):                       # a photograph of our own takes precedence
        for ext, mime in ((".jpg", "image/jpeg"), (".jpeg", "image/jpeg"),
                          (".png", "image/png"), (".webp", "image/webp")):
            path = os.path.join("news", it["photo"] + ext)
            if os.path.exists(os.path.join(HERE, path)):
                return '<div class="p-news-pic">%s</div>' % img(path, "", mime)
        kind, ref = "photo", "asm-venue"      # stand in with the venue until that photo arrives
    if kind == "photo":
        c = CREDITS.get(ref)
        if not c:
            return ""
        # public-domain and CC0 photographs carry no attribution condition, so they run clean;
        # a CC BY photograph must name its author wherever it appears
        needs_credit = "cc by" in c["licence"].lower()
        cap = ('<figcaption>%s &middot; %s</figcaption>' % (c["artist"], c["licence"])
               if needs_credit else "")
        return ('<figure class="p-news-pic">%s%s</figure>'
                % (img(os.path.join("news", ref + ".jpg"), "", "image/jpeg"), cap))
    if kind == "svg":
        return '<div class="p-news-pic p-news-mark">%s</div>' % svg(ref, "p-mark-svg")
    if kind == "img":
        return '<div class="p-news-pic">%s</div>' % img(ref, "")
    return ""


def news_faces(names):
    """Portraits for the people a news item is about; anyone without one is simply left out."""
    import sys as _sys
    _sys.path.insert(0, os.path.join(HERE, "people"))
    import namekey
    out = []
    for n in names or []:
        k = namekey.key(n)
        if k in FACE_CLASS:
            out.append('<span class="p-news-face f%d" title="%s"></span>'
                       % (FACE_CLASS[k], FACE_NAME[k]))
    return '<div class="p-news-faces">%s</div>' % "".join(out) if out else ""


def news_portrait(name):
    """One person, shown as large as the institution photo beside them."""
    import sys as _sys
    _sys.path.insert(0, os.path.join(HERE, "people"))
    import namekey
    k = namekey.key(name)
    if k not in FACE_CLASS:
        return ""
    return ('<figure class="p-news-portrait"><div class="f%d" role="img" aria-label="%s"></div>'
            '<figcaption>%s</figcaption></figure>' % (FACE_CLASS[k], FACE_NAME[k], FACE_NAME[k]))


def news_view():
    out = []
    offers = [0]                       # counted across the whole section, not per group
    for heading, items in NEWS:
        rows = []
        for it in items:
            title = ('<a href="%s">%s</a>' % (it["url"], it["title"])) if it["url"] else it["title"]
            meta = '<div class="p-news-meta">%s</div>' % it["meta"] if it["meta"] else ""
            pic = news_pic(it)
            faces = news_faces(it.get("people"))
            date = ('<div class="p-news-date">%s</div>' % it["date"]) if it.get("date") else ""
            if it.get("portrait"):
                # no institution picture: the portrait alone, and the row itself sits off centre,
                # alternating side to side down the whole section
                side = "is-right" if offers[0] % 2 == 0 else "is-left"
                offers[0] += 1
                face = news_portrait(it["portrait"])
                # nobody has sent a photograph of everyone; without one the row runs full width
                # rather than leaving a portrait-sized hole beside the text
                solo = "" if face else " p-offer-solo"
                rows.append('<li class="p-news-item p-offer %s%s">%s<div class="p-news-body">%s'
                            '<h4>%s</h4>%s<p>%s</p></div></li>'
                            % (side, solo, face, date, title, meta, it["note"]))
                continue
            # a flipped row puts the picture on the right, so the section does not read as one
            # unbroken left column of images
            cls = "p-news-item p-news-flip" if it.get("flip") else "p-news-item"
            rows.append('<li class="%s">%s<div class="p-news-body">%s<h4>%s</h4>%s'
                        '<p>%s</p>%s</div></li>'
                        % (cls, pic, date, title, meta, it["note"], faces))
        out.append('<div class="p-news-group"><h3>%s</h3><ul>%s</ul></div>'
                   % (heading, "".join(rows)))
    return ('<section class="p-news"><h2 class="p-sec-h">News</h2>%s</section>'
            % "".join(out))


# ----------------------------------------------------------------- people ----
# The project leads, in the order Sam listed them; second item is a role, where there is one.
PROJECT_LEADS = [(d["name"], d.get("role")) for d in CONTENT["project_leads"]]

TEAM_LABEL = CONTENT["team_labels"]

# already shown as cards at the top of the page, so they are not repeated in the grids
AT_TOP = CONTENT["at_top"]


def face_css(index):
    """One rule per portrait. Both the people page and the MMC view point at these.

    Tiles are 184 px, which is right for a 104 px grid cell but soft where the news section shows
    a portrait at 250 px on a retina screen. Anyone shown at that size — the studio photographs,
    and whoever a news item names — gets the full crop instead, so the list drives the sizes
    rather than the sizes being maintained by hand."""
    import sys as _sys
    _sys.path.insert(0, os.path.join(HERE, "people"))
    import namekey
    shown_big = {namekey.key(it["portrait"])
                 for _, items in NEWS for it in items if it.get("portrait")}
    out = []
    for i, e in enumerate(index):
        big = e.get("source") == "better" or namekey.key(e["name"]) in shown_big
        path = ("people/faces/" if big else "people/tiles/") + e["file"]
        out.append(".f%d{background-image:url(%s)}" % (i, data_uri(path, "image/jpeg")))
    return "\n".join(out)


def face_tile(i, e, role=None):
    r = '<span class="p-face-role">%s</span>' % role if role else ""
    return ('<figure class="p-face%s"><div class="p-face-img f%d" role="img" aria-label="%s"></div>'
            '<figcaption>%s%s</figcaption></figure>'
            % ("" if e["name"] else " p-face-anon", i,
               e["name"] or "Researcher on the projects", e["name"] or "&nbsp;", r))


def people_view():
    sys.path.insert(0, os.path.join(HERE, "people"))
    import namekey
    legacy = json.load(open(os.path.join(HERE, "people", "legacy_people.json")))
    authors = json.load(open(os.path.join(HERE, "people", "author_names.json")))

    leads = {"Sam Degregori": ("Director", "Postdoctoral fellow, UC San Diego"),
             "Katherine Amato": ("Advisor", "Associate professor, Northwestern University"),
             "Rob Knight": ("Advisor", "Professor, UC San Diego")}
    order = ["Sam Degregori", "Katherine Amato", "Rob Knight"]
    by_name = {p["name"]: p for p in legacy}
    lead_cards = "".join(
        '<div class="p-lead-card">%s<div><b>%s</b><i>%s</i><span>%s</span></div></div>'
        % (img("../reference/legacy-site/assets/" + by_name[n]["asset"], n,
               "image/png" if by_name[n]["asset"].endswith("png") else "image/jpeg"),
           n, leads[n][0], leads[n][1])
        for n in order if n in by_name)

    faces_all = json.load(open(os.path.join(HERE, "people", "faces_index.json")))
    _, everyone = namekey.canonicalise(
        [p["name"] for p in legacy] + authors["gmtol"] + authors["mmc"]
        + [f["name"] for f in faces_all if f["name"]])
    everyone.sort(key=lambda n: n.split()[-1].lower())
    names_html = "".join('<li>%s</li>' % n for n in everyone)

    # portraits: everyone we can name first, the unlabelled team-photo faces after
    index = list(faces_all)
    index.sort(key=lambda e: (e["name"] == "", e["name"].split()[-1].lower() if e["name"] else ""))
    unnamed = sum(1 for e in index if not e["name"])
    teams = json.load(open(os.path.join(HERE, "people", "teams.json")))
    lead_keys = [namekey.key(n) for n, _ in PROJECT_LEADS]
    role_of = {namekey.key(n): r for n, r in PROJECT_LEADS if r}
    top_keys = {namekey.key(n) for n in AT_TOP}
    by_key = {}
    for e in index:
        by_key.setdefault(namekey.key(e["name"] or ""), e)

    core = [by_key[k] for k in lead_keys if k in by_key]
    placed = set(lead_keys) | top_keys
    groups = []
    for team, heading in (("gmtol", "GMToL interns"), ("hmtol", "HMToL interns")):
        keys = [namekey.key(n) for n in teams[team]]
        members = [by_key[k] for k in keys if k in by_key and k not in placed]
        placed |= set(keys)
        groups.append((heading, members))
    rest = [e for e in index if namekey.key(e["name"] or "") not in placed]
    groups.append(("MMC interns", rest))
    pos = {id(e): i for i, e in enumerate(index)}
    core_tiles = "".join(
        face_tile(pos[id(e)], e, role_of.get(namekey.key(e["name"] or ""))) for e in core)
    group_html = "".join(
        '''<h2 class="p-sec-h">%s</h2>\n<div class="p-grid">%s</div>\n'''
        % (heading, "".join(face_tile(pos[id(e)], e) for e in members))
        for heading, members in groups)

    # the MMC view shows the same portraits as one block, in the same order
    at_top = [e for k in [namekey.key(n) for n in AT_TOP]
              for e in index if namekey.key(e["name"] or "") == k]
    everyone_tiles = "".join(face_tile(pos[id(e)], e) for e in at_top + core + rest)
    globals()["MMC_CONSORTIUM"] = (
        '''<h2 class="p-sec-h">Led by the MMC Consortium</h2>
<div class="p-grid">%s</div>''' % everyone_tiles)
    globals()["FACE_CSS"] = face_css(index)
    globals()["FACE_CLASS"] = {namekey.key(e["name"]): i
                               for i, e in enumerate(index) if e["name"]}
    globals()["FACE_NAME"] = {namekey.key(e["name"]): e["name"]
                              for e in index if e["name"]}

    # front-page team rows. Luis Xu appears on every team there, at Sam's request.
    panels = []
    for team in ("gmtol", "hmtol"):
        keys = [namekey.key(n) for n in teams[team]]
        for extra in ("Luis Xu",):
            if namekey.key(extra) not in keys:
                keys.append(namekey.key(extra))
        row = "".join(face_tile(pos[id(by_key[k])], by_key[k]) for k in keys if k in by_key)
        panels.append('<div class="p-team" data-team="%s" hidden>%s</div>' % (team, row))
    globals()["TEAM_PANELS"] = "\n".join(panels)

    return f'''<section class="p-intro">
  <h1 class="p-title-accent">People</h1>
</section>

<div class="p-leads p-leads-top">{lead_cards}</div>

<h2 class="p-sec-h">Project leads</h2>
<div class="p-grid p-grid-center">{core_tiles}</div>

{group_html}

<h2 class="p-sec-h">Institutions</h2>
{INST_BAND}

<h2 class="p-sec-h">MMC Consortium</h2>
<ul class="p-names">{names_html}</ul>'''


# --------------------------------------------------------------- projects ----
GMTOL = f'''<section class="p-intro">
  <h1>The Gut Microbiome Tree of Life</h1>
</section>

{figs(figure(img("figs/gmtol/gmtol-pcoa-host-class.webp",
                 "Principal coordinates analysis coloured by host class"),
             "The Gut Microbiome Tree of Life visualized across multi-dimensional space",
             "Unweighted UniFrac ordination of the whole dataset, coloured by host class, with "
             "marginal densities for the dominant phyla. Mammals occupy one end of PC1 and insects "
             "the other, with birds, fishes, reptiles and amphibians filling the space between. "
             "<a class='p-src' href='" + BIORXIV + "' target='_blank' rel='noopener'>Manuscript Fig. 3A</a>",
             span="full"))}

{figs(
    figure(img("figs/gmtol/gmtol-host-phylogeny.webp",
               "Circular time-calibrated host phylogeny with stacked bacterial phylum bars"),
           "Composition across the host tree",
           "Samples merged by host species (n=828, matched to NCBI). Stacked bars at the tips give "
           "the relative abundance of the major bacterial phyla; the host phylogeny is "
           "time-calibrated. <a class='p-src' href='" + BIORXIV + "' target='_blank' rel='noopener'>Manuscript Fig. 2A</a>",
           kicker="Host phylogeny"),
    figure(img("figs/gmtol/gmtol-diversity-host-class.webp",
               "Diversity boxplots across host classes under a host phylogeny"),
           "How diversity varies across host classes",
           "Faith's phylogenetic diversity and Shannon diversity per host class, under the "
           "time-calibrated host phylogeny. Chordates carry the highest diversity on average — with "
           "exceptions. <a class='p-src' href='" + BIORXIV + "' target='_blank' rel='noopener'>Manuscript Fig. 3C</a>",
           kicker="Diversity"))}

{papers(("An expansive animal gut microbiome dataset elucidates major compositional shifts "
        "across bilaterian evolution",
        "Preprint &middot; <em>bioRxiv</em>, 8 May 2026 &middot; under review at <em>Science</em>",
        BIORXIV),
       ("Comparative gut microbiome research through the lens of ecology: theoretical "
        "considerations and best practices",
        "<em>Biological Reviews</em> 100(2):748&ndash;763, 2024",
        "https://doi.org/10.1111/brv.13161"))}
'''

HMTOL = f'''<section class="p-intro">
  <h1>The Human Microbiome Tree of Life</h1>
  <p class="p-lead">European and North American subjects still dominate the human gut microbiome
  literature. HMToL is the human-focused successor to GMToL: 16,956 gut microbiomes drawn from
  public data spanning 124 studies and 70 countries, harmonised onto one phylogeny so that geography, development and
  age can be compared without the study-to-study noise that usually swamps them.</p>
</section>

{figs(figure(svg("figs/hmtol/hmtol-studies-map.svg"),
             "What has been collected, and from where",
             "Studies contributed per country across the whole collection — 124 studies from 70 "
             "countries. The scale is logarithmic because a handful of countries contribute several "
             "studies each while most contribute one. Countries in grey are ones the collection has "
             "not reached.",
             kicker="Summary", span="full"))}

<div class="p-lens" id="lens-ordination"></div>

{figs(figure(svg("figs/hmtol/hmtol-succession.svg"),
             "Genus trajectories across the lifespan",
             "Relative abundance of four genera against age, one line per continent, log scale. Age "
             "bins with fewer than eight samples are dropped, so some continents stop early.",
             kicker="Succession", span="full"))}

{figs(
    figure(svg("figs/hmtol/hmtol-westernization-map.svg"),
           "Distance from the industrialised gut",
           "Adult samples only, 26 countries. Colour is mean unweighted UniFrac distance to a "
           "Global-North reference set — darker means farther.",
           kicker="Westernization"),
    figure(svg("figs/hmtol/hmtol-westernization-hdi.svg"),
           "That distance tracks development, not age",
           "Each point is a country. The gradient holds against the Human Development Index and, "
           "unlike between-country spread, survives restricting the data to adults.",
           kicker="HDI gradient"))}

{figs(figure(svg("figs/hmtol/hmtol-core.svg"),
             "There is barely a global core microbiome",
             "Left: taxa present in at least half the samples of each continent, out of 14,461 "
             "features. North America has 66; Australia has 11. Right: the five taxa that clear that "
             "bar on every continent. The imbalance is partly biology and partly how unevenly the "
             "world has been sampled.",
             kicker="Core microbiome", span="full"))}

<div class="p-lens" id="lens-tree"></div>

{papers(("A dataset paper is in preparation", "No preprint yet &mdash; nothing to link", None))}

{note("<b>Status.</b> HMToL is unpublished. The ordination, the maps and the trajectories above are "
      "real HMToL results; the tree component's two ring encodings are placeholder values carried "
      "over from the report prototype it came from, kept only to show the interaction.")}'''

MMC = f'''{figs(figure(svg("figs/mmc/mmc-study-overview.svg"),
             None,
             "From 33,564 candidate articles down to the 3,300 human-health articles read in full, "
             "with roughly 70 variables recorded per article — 143,220 data entries, curated by a "
             "consortium of about 300 professors, postdocs, graduate and undergraduate students.",
             span="full"))}

{figs(figure(svg("figs/mmc/mmc-reusability-waffle.svg"),
             "Every study we read, sorted by how far you can get with its data",
             "One square per study. Tier 1 carries biological annotation in the repository itself; "
             "Tier 2 has sample names informative enough to recover the biology; Tier 3 has unique "
             "sample IDs but no biology; Tier 4 cannot be reused at all. Only Tiers 1 and 2 support "
             "reuse without going back to the manuscript &mdash; 563 studies of 3,145.",
             kicker="Reusability", span="full"))}

{figs(
    figure(svg("figs/mmc/mmc-tier-by-year.svg"),
           "Volume climbs; reusability does not follow",
           "Studies reviewed per year, stacked by reusability tier. 2025 is a partial year — the "
           "review closed mid-year.",
           kicker="Over time"),
    figure(svg("figs/mmc/mmc-sequencing-type.svg"),
           "16S is still how most of the literature was sequenced",
           "Share of studies per year by sequencing approach, among the 2,045 studies where it was "
           "recorded.",
           kicker="Method"))}

{papers(("Sample Size Reporting in Human Cancer Microbiome Research is Inconsistent and "
        "Unstandardized",
        "Preprint &middot; in revision at <em>Access Microbiology</em>, 18 February 2026",
        "https://doi.org/10.1099/acmi.0.001187.v1"))}

{note("<b>About the figures.</b> The waffle is drawn from the current tier totals: 3,145 "
      "studies across the four tiers. The funnel and the two yearly panels are still computed "
      "from an earlier export, <code>MMC1_study_data_final.tsv</code> at n=2,046, so their "
      "counts and percentages are proportions of that subset until a per-year table replaces "
      "it.")}'''


# ---------------------------------------------------------------- styling ----
CSS = """
:root{
  --bg:radial-gradient(130% 120% at 50% -8%, #16181c 0%, #0b0c0e 60%);
  --surface:#141619; --elev:#1d2024; --panel:#0f1114;
  --hair:#ffffff14; --hair2:#ffffff29;
  --ink:#f5f5f7; --ink2:#a1a1a6; --ink3:#86868b; --lead:#c7c7cc;
  --accent:#2997ff; --accent-h:#47a6ff; --you:#f0b429;
  /* Card palette — ink. The fills are near-neutral with only a whisper of hue, the way paper
     stocks differ; what tells the projects apart is the edge and the rule, not the ground. The
     quietest of the three sets, and the one that lets the figures carry the colour.
     Earlier sets, one paste away —
       cool:      gm #0d211f/#143029/#3fd2b0  mm #101c30/#17263f/#6aa8ff  hm #1a1730/#272041/#a78bfa
       herbarium: gm #152018/#1e2d22/#84c496  mm #241519/#331e23/#e08494  hm #231b12/#33281b/#e0ad63 */
  --gm:#141917; --gm-hi:#1b2220; --gm-edge:#5fbf9b;
  --mm:#14171d; --mm-hi:#1c2029; --mm-edge:#6f9fe8;
  --hm:#181519; --hm-hi:#211d24; --hm-edge:#b98fd0;
  /* the disc under the cards: neutral graphite, so it belongs to the stage, not a project */
  --card:#16181b; --card-hi:#1d2024; --glow:#c8d2de;
  --shadow:0 1px 2px #00000066, 0 12px 34px -14px #000000cc;
  --r:18px;
  --sans:'Work Sans',-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  /* Literata was drawn for reading on screens rather than adapted from a book face, which is
     what keeps it legible down at figure-caption size */
  --display:Literata,Georgia,'Times New Roman',serif;
  /* labels were monospaced, which read as a data dashboard; letterspaced small caps in the
     text sans is the academic equivalent and carries the same hierarchy */
  --mono:'Work Sans',-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
  --code:ui-monospace,SFMono-Regular,Menlo,monospace;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);background-attachment:fixed;color:var(--ink);
  font-family:var(--sans);-webkit-font-smoothing:antialiased;line-height:1.5}
a{color:var(--accent);text-decoration:none} a:hover{color:var(--accent-h)}
.p-wrap{max-width:1180px;margin:0 auto;padding:0 32px}

/* header */
/* the masthead carries the page's own background, fixed like the body's, so the two line up
   pixel for pixel and there is no seam where the header ends */
.p-top{position:sticky;top:0;z-index:40;overflow:hidden;
  background:var(--bg);background-attachment:fixed}
/* The dot field is a flex item sitting between the wordmark and the tabs rather than a layer
   behind them, so it fills whatever space is left and can never run under either. Nothing
   overlaps, so it runs at full strength with no mask and no dimming. */
/* capped and centred: the hexagons are drawn for a 12:1 slot, and letting the element stretch
   to whatever gap is left would crop rows off the top and bottom on a wide screen */
.p-banner{flex:1;min-width:0;max-width:640px;height:46px;align-self:center;margin:0 -30px;
  position:relative;z-index:0;
  background-image:url(__BANNER__);background-size:100% auto;background-position:center;
  background-repeat:no-repeat;pointer-events:none}
.p-top-in,.p-inst-row{position:relative;z-index:1}
/* the field runs on under the wordmark and the tabs; its ends are faded, and these two
   paint above it */
.p-mark,.p-nav{position:relative;z-index:1}
.p-top-in{max-width:1180px;margin:0 auto;padding:13px 32px;display:flex;
  justify-content:space-between;align-items:center;gap:24px}
.p-mark{font-family:var(--display);font-weight:800;font-size:24px;letter-spacing:-.02em;color:var(--ink)}
.p-inst-row{border-top:1px solid var(--hair)}
.p-inst{max-width:1180px;margin:0 auto;padding:9px 32px;font:600 12.5px/1.65 var(--mono);
  color:var(--ink2);letter-spacing:.06em;text-transform:uppercase}
.p-nav{display:flex;gap:4px;flex-wrap:wrap}
.p-nav a{font-size:13.5px;font-weight:700;color:var(--ink);padding:7px 13px;border-radius:999px;
  /* the wedge is at its widest under the nav, so the labels get a dark halo rather than a
     plate, which would break the seamless masthead */
  white-space:nowrap;background:transparent;border:1px solid transparent;
  transition:background .2s,border-color .2s,color .2s}
.p-nav a:hover{color:var(--ink);background:#ffffff1c;border-color:#ffffff3d}
.p-nav a.on{color:var(--ink);background:var(--elev);border-color:var(--hair2)}

/* a project view opens as a sheet standing over the home page rather than replacing it */
.p-locked{overflow:hidden}
main{transition:transform .45s cubic-bezier(.2,.7,.2,1),filter .45s ease}
main.p-behind{transform:scale(.965);filter:brightness(.42) saturate(.85)}
.p-modal{position:fixed;inset:0;z-index:60;display:flex;justify-content:center;
  align-items:flex-start;padding:30px 20px}
.p-modal[hidden]{display:none}
.p-modal-back{position:absolute;inset:0;background:#04050799;backdrop-filter:blur(2px)}
/* the top strip is the close button's own space: the body starts below it, so content scrolls
   past underneath rather than sliding behind the X */
.p-sheet{position:relative;display:flex;flex-direction:column;width:min(1180px,100%);
  max-height:calc(100vh - 60px);padding-top:56px;background:var(--panel);
  border:1px solid var(--hair2);border-radius:22px;
  box-shadow:0 60px 130px -34px #000,0 0 0 1px #ffffff0d}
.p-sheet.is-in{animation:p-sheet-in .42s cubic-bezier(.2,.8,.2,1) both}
@keyframes p-sheet-in{from{opacity:0;transform:translateY(30px) scale(.94)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){
  .p-sheet.is-in{animation:none}
  main{transition:none}
}
/* the body scrolls, so the close button stays put at the corner */
.p-sheet-body{overflow:auto;overscroll-behavior:contain;padding:0 34px 6px}
.p-x{position:absolute;top:14px;right:16px;z-index:2;width:36px;height:36px;padding:8px;
  border-radius:50%;cursor:pointer;background:var(--elev);border:1px solid var(--hair2);
  color:var(--ink2);transition:background .2s,color .2s,border-color .2s}
.p-x:hover{background:#2a2e34;color:var(--ink);border-color:#ffffff4d}
.p-x svg{width:100%;height:100%;display:block}

/* views */
.p-view{display:none;padding:0 0 72px}
.p-view.on{display:block;animation:pfade .3s ease both}
@keyframes pfade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}

/* the face band: three strips of portraits, drifting */
.p-band{overflow:hidden;display:flex;flex-direction:column;gap:2px;border-radius:var(--r)}
.p-row{height:78px;background-repeat:repeat-x;background-size:auto 100%;will-change:background-position}
@media (prefers-reduced-motion:reduce){.p-row{animation:none !important}}

/* hero + intros */
.p-hero{padding:70px 0 44px}
.p-hero-tight{padding:40px 0 30px}
.p-eyebrow{font:700 11.5px/1 var(--mono);color:var(--you);letter-spacing:.16em;
  text-transform:uppercase;margin-bottom:18px}
.p-hero h1{font-family:var(--display);margin:0;max-width:880px;font-size:clamp(34px,5.2vw,57px);font-weight:800;
  line-height:1.03;letter-spacing:-.035em;text-wrap:pretty}
.p-lead{margin:20px 0 0;max-width:660px;font-size:16.5px;line-height:1.6;color:var(--lead);
  text-wrap:pretty}
/* this one introduces the counts below it, so it carries more weight than a normal lead */
.p-lead-big{font-size:clamp(19px,2.1vw,24px);color:var(--ink);max-width:none;font-weight:600;
  letter-spacing:-.01em}
.p-intro{padding:26px 0 10px}
.p-intro h1{font-family:var(--display);margin:0;max-width:820px;font-size:clamp(30px,4.4vw,46px);font-weight:800;
  line-height:1.06;letter-spacing:-.03em;text-wrap:pretty}
.p-intro .p-eyebrow{color:var(--accent)}
.p-title-accent{color:var(--accent)}

/* the numbers */
.p-bignums{display:flex;gap:52px;flex-wrap:wrap;margin:34px 0 0}
.p-bignums b{font-family:var(--display);display:block;font-size:clamp(30px,4vw,44px);font-weight:800;letter-spacing:-.04em;
  line-height:1;color:var(--ink)}
.p-bignums span{display:block;margin-top:7px;font:600 11px/1.4 var(--mono);color:var(--ink3);
  letter-spacing:.11em;text-transform:uppercase;max-width:20ch}

/* institutions */
.p-inst-band{display:flex;flex-wrap:wrap;gap:8px 0;border-bottom:1px solid var(--hair);
  margin:0 0 4px;padding:16px 0}
.p-inst-band span{font:600 13.5px/1.2 var(--sans);color:var(--ink2);letter-spacing:.045em;
  text-transform:uppercase;white-space:nowrap}
.p-inst-band span:not(:last-child)::after{content:"·";margin:0 14px;color:var(--ink3);
  font-weight:400}

/* cards */
.p-carousel{display:flex;align-items:stretch;gap:10px;padding:26px 0 44px}
/* the three cards sit on one spot and are placed in depth, so the two that are not centred stand
   behind the front one and turn toward the viewer */
/* the track is transparent to the pointer: in a preserve-3d context the two side cards sit at
   translateZ(-250px), behind the track's own plane, so the track was swallowing every click and
   hover meant for them */
.p-track{position:relative;flex:1;min-width:0;perspective:1250px;perspective-origin:50% 42%;
  transform-style:preserve-3d;pointer-events:none}
.p-track .p-card{pointer-events:auto}
/* a disc lying flat under the cards, so the carousel reads as turning on a surface */
/* the lit patch stays low and near the middle of the disc: a taller, brighter core rose up
   behind the cards and cut a bright ridge across the two standing at the sides */
.p-table{position:absolute;left:50%;bottom:-14px;width:100%;height:248px;border-radius:50%;
  transform:translateX(-50%) rotateX(74deg);transform-origin:50% 100%;pointer-events:none;
  /* a tinted surface under the lit patch, so the disc is dark blue like the cards standing
     on it rather than a glow on bare page */
  background:radial-gradient(44% 46% at 50% 62%,#c8d2de29,#c8d2de19 44%,#c8d2de0b 66%,
      transparent 80%),
    radial-gradient(72% 74% at 50% 58%,#16181bf0,#16181bc4 52%,#16181b70 74%,transparent 88%);
  box-shadow:inset 0 0 0 1px #c8d2de30,0 0 48px 6px #c8d2de10;z-index:0}
.p-arrow{flex:none;align-self:center;width:38px;height:38px;border-radius:50%;cursor:pointer;
  background:var(--surface);border:1px solid var(--hair2);color:var(--ink2);padding:8px;
  transition:background .2s,color .2s,border-color .2s}
.p-arrow:hover{background:var(--elev);color:var(--ink);border-color:#ffffff44}
.p-arrow svg{width:100%;height:100%;display:block}
/* Every card is the same size. The two that are not centred are scaled back and turned away,
   and the whole set slides when it rotates, so the middle card is always full size. */
.p-track .p-card{position:absolute;top:0;left:50%;width:35%;transform-style:preserve-3d;
  transform-origin:50% 50%;backface-visibility:hidden;
  transition:transform .6s cubic-bezier(.22,.75,.2,1),opacity .6s ease,
    border-color .3s,box-shadow .4s,background .3s}
/* barely translucent, so a trace of the disc's light shows through the card's foot and it reads
   as sitting in the same space — the deep shadow is what keeps it standing off the surface */
.p-track .p-card.is-center{background:color-mix(in srgb,var(--card) 97%,transparent);
  box-shadow:0 1px 2px #00000066,0 44px 80px -28px #000}
/* a card standing behind is a control: click it and the carousel turns toward it */
.p-track .p-card.is-side{opacity:.72;cursor:pointer}
/* the highlight was too quiet to notice: a card behind now brightens, takes an accent edge and
   a blue glow, so it reads as the control it already was */
.p-track .p-card.is-side:hover{opacity:1;background:var(--card-hi);
  border-color:color-mix(in srgb,var(--edge) 80%,transparent);
  box-shadow:0 1px 2px #00000066,0 30px 60px -22px #000,0 0 0 3px #2997ff33}
/* the centred card is the one that goes somewhere, so hovering it grows the card and sets its
   button pulsing at the same moment. The two cards behind are unchanged. */
.p-track .p-card.is-center:hover{--pop:1.045;transition:transform .25s cubic-bezier(.2,.7,.2,1),
  border-color .3s,box-shadow .3s,background .3s;
  border-color:color-mix(in srgb,var(--edge) 55%,transparent);
  box-shadow:0 1px 2px #00000066,0 54px 92px -30px #000}
@keyframes p-go-pulse{
  0%,100%{box-shadow:0 0 0 0 #2997ff00}
  50%{box-shadow:0 0 0 7px #2997ff2e}
}
.p-track .p-card.is-center:hover .p-go{background:#2997ff45;border-color:#2997ffcc;color:#cfe6ff;
  opacity:1;animation:p-go-pulse 1.15s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){
  .p-track .p-card.is-center:hover .p-go{animation:none}
}
/* the people below follow the centred card, and cross-fade when it changes */
.p-people{position:relative;transition:opacity .3s ease}
.p-people.is-fading{opacity:0}
.p-team{display:flex;flex-wrap:wrap;justify-content:center;gap:16px 12px;padding:6px 0 2px}
.p-team[hidden],.p-band[hidden]{display:none}
.p-team .p-face{width:104px}
.p-card[data-card="gmtol"]{--card:var(--gm);--card-hi:var(--gm-hi);--edge:var(--gm-edge)}
.p-card[data-card="mmc"]{--card:var(--mm);--card-hi:var(--mm-hi);--edge:var(--mm-edge)}
.p-card[data-card="hmtol"]{--card:var(--hm);--card-hi:var(--hm-hi);--edge:var(--hm-edge)}
.p-card{position:relative;overflow:hidden;display:flex;flex-direction:column;padding:20px 22px 18px;
  background:var(--card);border:1px solid color-mix(in srgb,var(--edge) 16%,transparent);
  border-radius:var(--r);
  box-shadow:var(--shadow);color:inherit;
  transition:transform .3s cubic-bezier(.2,.7,.2,1),border-color .3s,box-shadow .3s,background .3s}
.p-card:hover{transform:translateY(-6px);background:var(--card-hi);
  border-color:color-mix(in srgb,var(--edge) 40%,transparent);
  box-shadow:0 1px 2px #00000066,0 34px 64px -22px #000}
.p-card:hover .p-go{transform:translateX(7px);opacity:1}
.p-card:hover .p-rule{width:100%}
/* on its own line under the stats rather than floated over them: "students, 19 institutions"
   is long enough that a bottom-right button sat on top of it */
.p-go{align-self:flex-end;margin-top:14px;opacity:.85;display:flex;align-items:center;
  gap:6px;font:700 12.5px/1 var(--mono);letter-spacing:.04em;color:var(--accent);white-space:nowrap;
  padding:7px 12px;border-radius:999px;background:#2997ff1a;border:1px solid #2997ff4d;
  transition:transform .3s cubic-bezier(.2,.7,.2,1),opacity .3s,background .3s,border-color .3s}
.p-go svg{display:block}
.p-card:hover .p-go{background:#2997ff33;border-color:#2997ff99}
/* every card's graphic occupies the same box, whatever its natural aspect */
.p-motif{margin:0 0 16px;height:118px;border-radius:10px;overflow:hidden;
  display:flex;align-items:center;justify-content:center}
.p-motif img{width:100%;height:100%;object-fit:cover;display:block}
.p-motif svg{width:100%;height:100%;display:block}
.p-motif-svg{width:100%;height:100%;display:flex}
/* the slot the project abbreviation used to sit in now carries the run of years, so it reads
   as a date rather than as a tag */
.p-abbr{font:600 11.5px/1 var(--mono);color:var(--ink3);letter-spacing:.13em;
  text-transform:uppercase;margin-bottom:9px}
.p-card-h{font-family:var(--display);font-size:22px;font-weight:800;letter-spacing:-.025em;line-height:1.1;
  margin-bottom:11px;text-wrap:pretty}
.p-card-p{margin:0 0 16px;font-size:13px;line-height:1.5;color:var(--ink2);text-wrap:pretty}
.p-stats{margin-top:auto;display:flex;gap:20px;padding-top:13px}
.p-stat{display:flex;flex-direction:column;gap:3px}
.p-stat b{font-size:17.5px;font-weight:700;letter-spacing:-.02em;line-height:1}
.p-stat span{font:600 10.5px/1 var(--mono);color:var(--ink3);letter-spacing:.1em;
  text-transform:uppercase}
.p-rule{position:absolute;left:0;bottom:0;height:2px;width:32%;
  background:var(--edge,var(--accent));
  transition:width .45s cubic-bezier(.2,.7,.2,1)}

/* the papers behind a project */
.p-papers{margin:34px 0 0}
.p-papers .p-sec-h{margin:0 0 14px}
.p-papers ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}
.p-papers li{padding:15px 18px;background:var(--surface);border:1px solid var(--hair);
  border-radius:12px}
.p-paper-t{font-family:var(--display);font-size:16px;font-weight:600;line-height:1.35;
  letter-spacing:-.01em;text-wrap:pretty}
.p-paper-t a{color:var(--ink);border-bottom:1px solid #2997ff59}
.p-paper-t a:hover{color:var(--accent);border-bottom-color:var(--accent)}
.p-paper-t span{color:var(--ink2)}
.p-paper-v{margin-top:5px;font-size:13px;color:var(--ink3)}

/* figures — two up unless a figure asks for the whole width */
.p-figs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;margin:20px 0 0}
.p-fig{margin:0;padding:22px 22px 18px;background:var(--surface);border:1px solid var(--hair);
  border-radius:var(--r);box-shadow:var(--shadow);display:flex;flex-direction:column}
.p-full{grid-column:1 / -1}
.p-fig-kicker{font:700 10.5px/1 var(--mono);color:var(--ink3);letter-spacing:.14em;
  text-transform:uppercase;margin-bottom:8px}
.p-fig-h{font-family:var(--display);margin:0 0 16px;font-size:18px;font-weight:700;letter-spacing:-.02em;line-height:1.25;
  text-wrap:pretty}
.p-fig-body{margin:0 0 14px}
.p-fig-svg svg{width:100%;height:auto;display:block;overflow:visible}
/* keep tall figures from dominating a row: cap the height and centre, rather than always
   filling the column width */
.p-fig-body img{max-width:100%;max-height:460px;width:auto;height:auto;display:block;margin:0 auto}
.p-full .p-fig-body img{max-height:600px}

.p-cap{font-size:12.5px;line-height:1.55;color:var(--ink2);text-wrap:pretty;margin-top:auto}
.p-wide{max-width:76ch}
.p-after-nums{margin-top:26px}
.p-src{color:var(--ink3);font-style:italic;font-size:12px;white-space:nowrap}
.p-note{margin:34px 0 0;padding:18px 22px;background:#f0b4291a;border:1px solid #f0b42966;
  border-radius:12px;font-size:13.5px;line-height:1.6;color:var(--lead);max-width:80ch}
.p-note b{color:var(--you)}
.p-note code{font-family:var(--code);font-size:12px;color:var(--ink)}
.p-built{font-family:var(--display);margin:26px 0 28px;font-size:clamp(17px,1.85vw,22px);font-weight:800;
  letter-spacing:-.02em;line-height:1.3;text-wrap:pretty}
.p-built em{font-style:normal;color:var(--you)}
.p-cohort{padding:40px 0 0}
.p-cohort-after{padding-top:26px}
.p-cohort-h{font-family:var(--display);margin:0;font-size:clamp(28px,4vw,44px);font-weight:800;letter-spacing:-.035em;
  line-height:1.05}
.p-lens{margin:34px 0 0}
.p-lens h1{font-size:clamp(26px,3.4vw,36px);letter-spacing:-.028em}

/* people */
.p-sec-h{margin:52px 0 18px;font-size:16px;font-weight:700;letter-spacing:.15em;
  text-transform:uppercase;color:var(--ink);font-family:var(--mono)}
.p-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));gap:14px 10px;
  margin:18px 0 0}
/* a short last row reads as unfinished when it is left-aligned under a full one */
.p-grid-center{display:flex;flex-wrap:wrap;justify-content:center}
.p-grid-center .p-face{width:112px}
.p-face{margin:0;display:flex;flex-direction:column;gap:7px}
.p-face-img{width:100%;aspect-ratio:1;border-radius:9px;background-size:cover;
  background-position:center;display:block}
.p-face figcaption{font-size:11.5px;line-height:1.3;color:var(--ink2);text-wrap:pretty}
.p-face-role{display:block;margin-top:2px;font:700 9.5px/1.2 var(--mono);color:var(--accent);
  letter-spacing:.1em;text-transform:uppercase}
.p-group-note{margin:30px 0 6px}
.p-face-anon .p-face-img{opacity:.72}
.p-leads-top{margin-top:8px}
.p-leads{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.p-lead-card{display:flex;gap:14px;align-items:center;padding:14px;background:var(--surface);
  border:1px solid var(--hair);border-radius:14px}
.p-lead-card img{width:64px;height:64px;object-fit:cover;border-radius:50%;flex:none}
.p-lead-card b{display:block;font-size:15px;font-weight:700}
.p-lead-card i{display:block;margin-top:3px;font-style:normal;font:700 10.5px/1 var(--mono);
  color:var(--accent);letter-spacing:.13em;text-transform:uppercase}
.p-lead-card span{display:block;margin-top:5px;font-size:12px;color:var(--ink2);line-height:1.4}
.p-names{list-style:none;margin:16px 0 0;padding:0;columns:4;column-gap:26px;font-size:13.5px;
  color:var(--lead)}
.p-names li{break-inside:avoid;padding:5px 0;border-bottom:1px solid var(--hair)}

/* news — one item per row, picture beside it */
.p-news{padding:52px 0 0;border-top:1px solid var(--hair);margin-top:44px}
.p-news > .p-sec-h{font-size:42px;font-weight:700;letter-spacing:-.03em;text-transform:none;
  font-family:var(--display);color:var(--ink);margin-bottom:26px}
.p-news-group{margin:0 0 34px}
.p-news-group h3{margin:0 0 16px;font-family:var(--display);font-size:29px;font-weight:700;
  color:var(--accent);letter-spacing:-.02em;line-height:1.15;padding-bottom:10px;
  border-bottom:1px solid var(--hair)}
.p-news-group ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:16px}
.p-news-item{display:grid;grid-template-columns:290px minmax(0,1fr);gap:26px;align-items:start;
  padding:22px;background:var(--surface);border:1px solid var(--hair);border-radius:16px}
.p-news-date{font:700 12px/1 var(--mono);color:var(--accent);letter-spacing:.14em;
  text-transform:uppercase;margin-bottom:9px}
.p-news-item h4{font-family:var(--display);margin:0;font-size:23px;font-weight:800;line-height:1.22;letter-spacing:-.025em;
  text-wrap:pretty}
.p-news-item h4 a{color:var(--ink)}
.p-news-item h4 a:hover{color:var(--accent)}
.p-news-meta{margin-top:8px;font-size:13.5px;color:var(--ink3)}
.p-news-item p{margin:12px 0 0;font-size:14.5px;line-height:1.6;color:var(--lead);
  text-wrap:pretty;max-width:70ch}
.p-news-flip{grid-template-columns:minmax(0,1fr) 290px}
.p-news-flip > .p-news-pic,.p-news-flip > .p-news-mark{order:2}
.p-news-flip > .p-news-body{order:1}
.p-news-pic{margin:0}
.p-news-pic img{width:100%;height:190px;object-fit:cover;border-radius:11px;display:block}
.p-news-pic figcaption{margin-top:7px;font:400 11px/1.45 var(--sans);color:var(--ink3);
  font-style:italic}
.p-news-mark{display:flex;align-items:center;justify-content:center;height:190px}
.p-mark-svg{width:100%;height:100%}
.p-mark-svg svg{width:100%;height:100%;display:block}
/* an offer: institution on one side, the person on the other, sides swapping down the list */
.p-offer{grid-template-columns:250px minmax(0,1fr);align-items:center;
  width:min(830px,100%);gap:30px}
.p-offer.is-right{margin-left:auto;grid-template-columns:minmax(0,1fr) 250px}
.p-offer.is-right .p-news-portrait{order:2}
.p-offer.is-right .p-news-body{order:1;text-align:right}
.p-offer.is-left{margin-right:auto}
.p-offer.p-offer-solo,.p-offer.is-right.p-offer-solo{grid-template-columns:minmax(0,1fr)}
/* a full-width paragraph set ragged-left reads as a mistake, so a row without a portrait
   keeps the offset but not the mirrored text */
.p-offer.p-offer-solo .p-news-body,.p-offer.is-right.p-offer-solo .p-news-body{text-align:left}
.p-news-portrait{margin:0}
.p-news-portrait > div{width:100%;aspect-ratio:1;border-radius:14px;background-size:cover;
  background-position:center;box-shadow:0 0 0 1px var(--hair2)}
.p-news-portrait figcaption{margin-top:9px;text-align:center;font-size:13.5px;font-weight:600;
  color:var(--ink)}
.p-news-faces{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.p-news-face{width:60px;height:60px;border-radius:50%;background-size:cover;
  background-position:center;box-shadow:0 0 0 1px var(--hair2);display:block}

/* footer */
.p-foot{border-top:1px solid var(--hair);padding:22px 0 40px;display:flex;
  justify-content:space-between;gap:18px;flex-wrap:wrap;font-size:12.5px;color:var(--ink3)}

@media (max-width:1000px){
  .p-figs{grid-template-columns:1fr}
  .p-names{columns:3}
}
@media (max-width:900px){
  .p-leads{grid-template-columns:1fr}
  .p-track{position:static;perspective:none;display:flex;flex-direction:column;gap:18px;
    height:auto !important}
  .p-track .p-card{position:static;width:auto;transform:none !important;opacity:1 !important}
  .p-arrow{display:none}
  .p-wrap,.p-top-in{padding-left:20px;padding-right:20px}
  .p-hero{padding-top:44px}
  .p-fig{padding:18px 14px 16px}
  .p-names{columns:2}
  .p-bignums{gap:30px}
  .p-news-item,.p-news-flip,.p-offer,.p-offer.is-right{grid-template-columns:1fr;width:auto;margin:0}
  .p-news-flip > .p-news-pic,.p-news-flip > .p-news-mark,.p-news-flip > .p-news-body{order:0}
  .p-offer .p-news-portrait,.p-offer .p-news-body{order:0;text-align:left}
  .p-news-item h4{font-size:20px}
  .p-news-face{width:52px;height:52px}
}
/* Dense figures stop being readable if they shrink to phone width, so they scroll inside their
   own card instead; the page body never scrolls sideways. */
@media (max-width:760px){
  .p-fig-body{overflow-x:auto;overscroll-behavior-x:contain}
  .p-fig-svg{min-width:600px}
  .p-lens{overflow-x:auto}
  .p-row{height:62px}
}
@media (max-width:700px){
  .p-top-in{flex-direction:column;align-items:flex-start;gap:10px}
  /* nineteen names wrap to seven lines on a phone and push the cards off the screen; keep
     them on one swipeable line instead */
  /* the nav takes a full row of its own here, which squeezes the field to nothing; hide it
     rather than leave a zero-width element behind */
  .p-banner{display:none}
  .p-inst{padding-left:20px;padding-right:20px;font-size:10.5px;letter-spacing:.04em;
    white-space:nowrap;overflow-x:auto;overscroll-behavior-x:contain;
    -webkit-mask-image:linear-gradient(90deg,#000 88%,transparent);
    mask-image:linear-gradient(90deg,#000 88%,transparent)}
  .p-nav{width:100%;gap:4px}
  .p-nav a{padding:6px 11px;font-size:13px}
  .p-names{columns:1}
  .p-modal{padding:12px 10px}
  .p-sheet{max-height:calc(100vh - 24px);border-radius:16px;padding-top:50px}
  .p-sheet-body{padding:0 14px 6px}
  main.p-behind{transform:none}
  .p-inst-band span{font-size:12px}
  .p-inst-band span:not(:last-child)::after{margin:0 9px}
}
"""

JS = """
const VIEWS = ['home','gmtol','mmc','hmtol','people'];

/* ---- home carousel: three equal cards; the two off-centre are scaled back and turned ---- */
const ORDER = ['gmtol','mmc','hmtol'];
const TEAM_LABELS = __TEAM_LABELS__;
const TURN = 30, DEPTH = 250, SPREAD = 0.80;
let centre = 1;                                   // MMC opens in the middle
let swapping = false;

function place(animate){
  const track = document.querySelector('#view-home .p-track');
  const cards = [...document.querySelectorAll('#view-home .p-card')];
  if(!track || !cards.length) return;
  const slot = {};
  slot[(centre + 2) % 3] = -1;                    // behind, to the left
  slot[centre] = 0;                               // front and centre
  slot[(centre + 1) % 3] = 1;                     // behind, to the right
  let tallest = 0;
  cards.forEach(el => { tallest = Math.max(tallest, el.offsetHeight); });
  if(tallest) track.style.height = tallest + 'px';
  cards.forEach((el, i) => {
    if(!animate) el.style.transition = 'none';
    const s = slot[i], middle = s === 0;
    el.style.transform =
      'translateX(-50%)' +
      ' translateX(' + (s * SPREAD * 100) + '%)' +
      ' translateZ(' + (middle ? 0 : -DEPTH) + 'px)' +
      ' rotateY(' + (-s * TURN) + 'deg)' +
      ' scale(var(--pop, 1))';               // CSS drives --pop on hover of the centred card
    // the dimmed side cards each create a stacking context, so 3D sorting cannot be relied on
    // to paint the front card over them — say it explicitly
    el.style.zIndex = middle ? 3 : 1;
    el.classList.toggle('is-center', middle);
    el.classList.toggle('is-side', !middle);
    if(!animate) requestAnimationFrame(() => { el.style.transition = ''; });
  });
}

function showTeam(){
  const team = ORDER[centre];
  document.querySelector('#view-home .p-band').hidden = team !== 'mmc';
  document.querySelectorAll('#view-home .p-team').forEach(t => {
    t.hidden = t.dataset.team !== team;
  });
  document.querySelector('.p-built').innerHTML = TEAM_LABELS[team];
}

function rotate(dir){
  if(swapping) return;
  swapping = true;
  // a click on the right arrow brings the card on the left into the middle
  centre = (centre + (dir === 1 ? 2 : 1)) % 3;
  place(true);
  const people = document.querySelector('.p-people');
  people.classList.add('is-fading');
  setTimeout(() => { showTeam(); people.classList.remove('is-fading'); swapping = false; }, 300);
}

document.querySelectorAll('#view-home .p-arrow').forEach(b => {
  b.addEventListener('click', () => rotate(b.dataset.dir === '1' ? 1 : -1));
});

document.querySelectorAll('#view-home .p-card').forEach((el, i) => {
  el.addEventListener('click', ev => {
    if(i === centre) return;                      // the front card is a link to its project
    ev.preventDefault();
    const slot = (i - centre + 3) % 3;            // 1 = behind right, 2 = behind left
    rotate(slot === 2 ? 1 : -1);                  // turn the carousel toward the one clicked
  });
});

/* the swap area keeps the height of its tallest panel so a rotation does not jolt the page */
function sizePeople(){
  const people = document.querySelector('.p-people');
  if(!people) return;
  // only worth reserving space where the carousel can actually rotate; on a phone the tallest
  // panel is a three-per-row team grid and the reserve would leave a screen of empty space
  if(innerWidth <= 900){ people.style.minHeight = ''; return; }
  const panels = [...people.children];
  const hidden = panels.map(p => p.hidden);
  let tallest = 0;
  panels.forEach(p => { p.hidden = false; tallest = Math.max(tallest, p.offsetHeight); });
  panels.forEach((p, i) => { p.hidden = hidden[i]; });
  people.style.minHeight = tallest + 'px';
}

// the home view is display:none until show() runs, and a hidden element measures as zero, so
// the carousel is laid out when that view actually becomes visible
function initHome(){ place(false); showTeam(); sizePeople(); }
addEventListener('resize', () => { if(location.hash.slice(1) !== 'home' && location.hash) return;
                                   place(false); sizePeople(); });

let lensesBuilt = false;

/* ---- the project views open as a sheet over the home page, not as a page swap ---- */
const sheet     = () => document.getElementById('p-modal');
const sheetBody = () => document.getElementById('p-sheet-body');
const wrap      = () => document.querySelector('main .p-wrap');

function closeSheet(){
  const body = sheetBody();
  // put whatever is in the sheet back where it came from, so there is one copy of each view
  [...body.children].forEach(el => { el.classList.remove('on'); wrap().appendChild(el); });
  sheet().hidden = true;
  document.documentElement.classList.remove('p-locked');
  document.querySelector('main').classList.remove('p-behind');
}

function openSheet(id){
  const body = sheetBody(), view = document.getElementById('view-' + id);
  if(view.parentElement !== body) body.appendChild(view);
  view.classList.add('on');
  sheet().hidden = false;
  const card = sheet().querySelector('.p-sheet');
  card.classList.remove('is-in'); void card.offsetWidth; card.classList.add('is-in');
  document.documentElement.classList.add('p-locked');
  document.querySelector('main').classList.add('p-behind');
  body.scrollTop = 0;
}

function show(id){
  if(!VIEWS.includes(id)) id = 'home';
  document.querySelectorAll('[data-nav]').forEach(a =>
    a.classList.toggle('on', a.dataset.nav === id));

  // home stays mounted underneath, which is what the sheet floats over
  closeSheet();
  document.getElementById('view-home').classList.add('on');
  initHome();

  if(id !== 'home'){
    // The two ported lenses are heavy, and only HMToL uses them, so build on first visit.
    if(id === 'hmtol' && !lensesBuilt){
      lensesBuilt = true;
      try{ window.poopLens.studies(document.getElementById('lens-ordination')); }
      catch(e){ console.error('ordination lens failed:', e); }
      try{ window.poopLens.tree(document.getElementById('lens-tree')); }
      catch(e){ console.error('tree lens failed:', e); }
    }
    openSheet(id);
  }else{
    window.scrollTo(0, 0);
  }
  document.title = (id==='home' ? 'poopomics' :
                    (id==='people' ? 'People' : id.toUpperCase()) + ' · poopomics');
}

function dismiss(){ if(!sheet().hidden) location.hash = '#home'; }
document.addEventListener('click', ev => { if(ev.target.closest('[data-close]')) dismiss(); });
document.addEventListener('keydown', ev => { if(ev.key === 'Escape') dismiss(); });

window.addEventListener('hashchange', ()=>show(location.hash.slice(1)));
show(location.hash.slice(1));
"""


# ----------------------------------------------------------------- build ----
def build():
    # people_view() also builds the portrait CSS and the one-block version for the MMC view
    people_html = people_view()
    banner = CSS.replace("__BANNER__", data_uri("figs/cards/banner-pcoa.svg", "image/svg+xml"))
    css_lenses = open(os.path.join(HERE, "lenses", "lenses.css")).read()
    js_lenses = open(os.path.join(HERE, "lenses", "lenses.js")).read()
    nav = "".join('<a href="#%s" data-nav="%s">%s</a>' % (v, v, lbl) for v, lbl in
                  [("home", "Home"), ("gmtol", "GMToL"), ("mmc", "MMC"),
                   ("hmtol", "HMToL"), ("people", "People")])
    fonts = ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
             'family=Work+Sans:ital,wght@0,300..800;1,300..600'
             '&family=Literata:ital,opsz,wght@0,7..72,300..800;1,7..72,300..700'
             '&display=swap">')
    insts = " &nbsp;·&nbsp; ".join(i.replace(" ", "&nbsp;") for i in INSTITUTIONS)

    # the script has plenty of its own % operators, so splice rather than %-format
    js_main = JS.replace("__TEAM_LABELS__", json.dumps(TEAM_LABEL))
    body = f"""<header class="p-top">
  <div class="p-top-in">
    <a href="#home" class="p-mark">poopomics</a>
    <div class="p-banner" aria-hidden="true"></div>
    <nav class="p-nav">{nav}</nav>
  </div>
</header>

<main>
  <div class="p-wrap">
    <div class="p-view" id="view-home">{home_view()}</div>
    <div class="p-view" id="view-people">{people_html}</div>
    <div class="p-view" id="view-gmtol">{GMTOL}</div>
    <div class="p-view" id="view-mmc">{MMC}
{MMC_CONSORTIUM}</div>
    <div class="p-view" id="view-hmtol">{HMTOL}</div>
  </div>
</main>

<div class="p-modal" id="p-modal" hidden>
  <div class="p-modal-back" data-close></div>
  <div class="p-sheet" role="dialog" aria-modal="true" aria-label="Project">
    <button class="p-x" data-close aria-label="Close">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"
           stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
    </button>
    <div class="p-sheet-body" id="p-sheet-body"></div>
  </div>
</div>

<div class="p-wrap"><footer class="p-foot">
  <div>DeGregori et&nbsp;al. 2024 &nbsp;·&nbsp; <em>Biological Reviews</em> &nbsp;·&nbsp;
    <a href="https://doi.org/10.1111/brv.13161">Gut microbiomes across the tree of life</a></div>
  <div>@poopomics</div>
</footer></div>

<script>{js_lenses}</script>
<script>{js_main}</script>"""

    standalone = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>poopomics</title>
{fonts}
<style>{banner}</style>
<style>{band_css()}</style>
<style>{FACE_CSS}</style>
<style>{css_lenses}</style>
</head>
<body>
{body}
</body>
</html>"""
    if ASSET_DIR:
        site = os.path.dirname(ASSET_DIR)
        page = os.path.join(site, "index.html")
        open(page, "w").write(standalone)
        n = len(os.listdir(ASSET_DIR))
        print("wrote site/index.html  %.2f MB  + %d files in site/assets (%.2f MB)"
              % (os.path.getsize(page) / 1e6, n,
                 sum(os.path.getsize(os.path.join(ASSET_DIR, f))
                     for f in os.listdir(ASSET_DIR)) / 1e6))
        return

    open(OUT, "w").write(standalone)
    print("wrote %s  %.2f MB" % (os.path.basename(OUT), os.path.getsize(OUT) / 1e6))

    # artifact: the host supplies doctype/html/head/body, so this is the page content only
    art = f"""<title>poopomics</title>
{fonts}
<style>{banner}</style>
<style>{band_css()}</style>
<style>{FACE_CSS}</style>
<style>{css_lenses}</style>
{body}"""
    open(ART, "w").write(art)
    print("wrote %s  %.2f MB" % (os.path.basename(ART), os.path.getsize(ART) / 1e6))


if __name__ == "__main__":
    build()
