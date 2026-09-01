"""Lift the two lenses we are reusing — Tree of life and See yourself — out of
AGP/Report/agp-report-prototype-wild-v2-dark.html, dropping everything the poopomics site
does not run.

Cuts are located by searching for the declaration text rather than by hard-coded offsets, so
this survives edits to the prototype. Emits lenses.js and lenses.css next to this file.
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = ("/Users/samde/Library/CloudStorage/OneDrive-UniversityofCalifornia,SanDiegoHealth/"
       "AGP/Report/agp-report-prototype-wild-v2-dark.html")

html = open(SRC, encoding="utf-8", errors="replace").read()

# ---------------- script ----------------
i = html.index("<script>") + len("<script>")
js = html[i:html.index("</script>", i)]
orig_len = len(js)

def at(decl):
    m = re.search(r"^" + re.escape(decl), js, re.M)
    if not m: raise SystemExit("not found: " + decl)
    return m.start()

def end_of_function(start):
    """Offset just past the closing brace of the function beginning at `start`."""
    j = js.index("{", start); d = 0; k = j
    while k < len(js):
        if js[k] == "{": d += 1
        elif js[k] == "}":
            d -= 1
            if d == 0: return k + 1
        k += 1
    raise SystemExit("unbalanced braces")

# everything after buildSeeYourself is the prototype's own bootstrap (lens rail, keyboard
# nav, intro overlay) — the site supplies its own.
sy = at("function buildSeeYourself")
CUTS = [
    ("TAXA + WORLD data (inhabitants list, world map)", at("const TAXA"), at("const FACTS")),
    ("taxonomy table + lifestyle factors + logo + brand mark",
     at("const TAX_ROWS"), at("const shSorted")),
    # the panel/explorer components only served the removed scenes; one of them also carried a
    # script-driven SVG download, which does nothing inside an artifact viewer
    ("panel shell + distribution/scatter/question/neighbour explorers",
     at("function PanelShell"), at("function PhyloTree")),
    ("SCENES rail and go() router", at("const SCENES"), at("function head")),
    ("overview / diversity / kinfolk / inhabitants scenes",
     at("function buildOverview"), at("function buildTree")),
    ("world / traits / go-deeper scenes", at("function buildWorld"), at("const SY_CC")),
    ("prototype bootstrap", end_of_function(sy), len(js)),
]
for label, a, b in sorted(CUTS, key=lambda t: -t[1]):
    print("  cut %-52s %8d chars" % (label, b - a))
    js = js[:a] + js[b:]


# ---------------- reframe from participant voice to project voice ----------------
# The prototype speaks to one AGP participant ("you're one dot"). On a project site there is
# no "you": the same figures have to describe the dataset. Each replacement is exact-match so
# a change upstream fails loudly here instead of silently shipping the old copy.
REFRAME = [
    # kill the participant marker everywhere it is drawn; an early return leaves the original
    # body as unreachable code, which keeps the prototype's brace structure valid as-is
    ('function youDot(x,y,r=7){',
     'function youDot(x,y,r=7){ return "";  /* poopomics: no participant on a project site */'),
    ('function youLabel(x,y,text="You",dy=-13){',
     'function youLabel(x,y,text="You",dy=-13){ return "";'),

    # --- tree lens ---
    ("head(scene,'Tree of life','Your <em>family</em> tree',\n"
     "    'A time-calibrated, genus-level tree of ~210 gut microbes. The genera in your sample "
     "are labelled and marked on the inner ring, shaded by how enriched or depleted each is "
     "versus the cohort. Hover any labelled microbe for what it does. Drag to pan, scroll to "
     "zoom.');",
     "head(scene,'Tree of life','A genus-level <em>tree</em> of the gut',\n"
     "    'A time-calibrated tree of ~210 gut microbial genera. Hover any labelled genus for "
     "what it does; drag to pan, scroll to zoom. <b>The two ring encodings are placeholder "
     "values carried over from the report prototype</b> — they are not GMToL or HMToL results, "
     "and are here to show the component, not a finding.');"),
    ("const dir = en>0.15?'enriched vs. cohort':en<-0.15?'depleted vs. cohort':'typical vs. cohort';",
     "const dir = ph;   // the prototype's enrichment call is placeholder, so it is not shown"),
    ("const fact = FACTS[gn] || ('A '+(ph||'gut')+' microbe detected in your sample.');",
     "const fact = FACTS[gn] || ('A '+(ph||'gut')+' microbe in the reference tree.');"),
    ('<div class="tt-sub">${ph} · ${dir}</div>', '<div class="tt-sub">${ph}</div>'),

    # Wheel zoom is removed: the handler called preventDefault on every wheel event over the
    # tree, so scrolling the page stopped dead once the cursor crossed it. Drag to pan and the
    # +/- buttons still work.
    ("svg.addEventListener('wheel',e=>{ e.preventDefault(); const rc=svg.getBoundingClientRect();",
     "svg.addEventListener('wheel',e=>{ return;  /* poopomics: the page scroll wins */\n"
     "    const rc=svg.getBoundingClientRect();"),

    ("what it does; drag to pan, scroll to zoom. <b>The two ring encodings are placeholder ",
     "what it does; drag to pan, or use the zoom buttons. <b>The two ring encodings are "
     "placeholder "),

    # --- see-yourself lens ---
    ("head(scene,'See yourself in a study','See yourself inside <em>a global study</em>',\n"
     "    'You\u2019re one dot among a continent-balanced sample of '+S.n.pcoa.toLocaleString()+"
     "' gut microbiomes, drawn from the full '+S.n.cohortGut.toLocaleString()+'-sample HMTOL "
     "global cohort. Recolour the ordination to see how your microbiome sits against age, "
     "geography and development \u2014 then find where your diversity falls across the human "
     "lifespan.');",
     "head(scene,'The global ordination','The most diverse human gut microbiome dataset <em>to date</em> (70 countries)',\n"
     "    'A continent-balanced sample of '+S.n.pcoa.toLocaleString()+' gut microbiomes, drawn "
     "from the full '+S.n.cohortGut.toLocaleString()+'-sample HMToL collection. Recolour the "
     "ordination by geography, development or age \u2014 then see how phylogenetic diversity "
     "moves across the human lifespan.');"),
    # the three disease-cohort tabs are dropped; only the colour-by controls remain
    ("'<span class=\"seg-div\" aria-hidden=\"true\"></span>'+"
     "[['ibd','IBD'],['t2d','Type 2 Diabetes'],['crc','Colorectal Cancer']]"
     ".map(function(a){return '<button data-m=\"'+a[0]+'\">'+a[1]+'</button>';}).join('')+",
     "''+"),

    ("'<h3 class=\"fig-h\">Where you land in the ordination</h3>'+",
     "'<h3 class=\"fig-h\">Where the samples land in the ordination</h3>'+"),
    ("h.textContent=d?(d.display+' \u2014 '+d.cite):'Where you land in the ordination';",
     "h.textContent=d?(d.display+' \u2014 '+d.cite):'Where the samples land in the ordination';"),
    ("<h3 class=\"fig-h\">Your diversity across the human lifespan</h3>",
     "<h3 class=\"fig-h\">Phylogenetic diversity across the human lifespan</h3>"),
    # the two ring encodings are prototype placeholders — say so where they are read, not just
    # in the paragraph above the component
    ('<span class="pl-title">Inner ring — enrichment vs. cohort</span>',
     '<span class="pl-title">Inner ring — placeholder encoding</span>'),
    ('<span class="pl-title">Outer ring — diet correlation</span>',
     '<span class="pl-title">Outer ring — placeholder encoding</span>'),

    # The ordination now opens on the age gradient, because the two figures that follow it on the
    # page are both about age. The chip markup is built before `mode` exists, so the highlighted
    # chip is hard-coded and has to move with it — these two edits belong together.
    ("const W=660,Hh=480,mL=52,mR=16,mT=14,mB=44; let mode='hemisphere';",
     "const W=660,Hh=480,mL=52,mR=16,mT=14,mB=44; let mode='age';"),
    ("""['Hemisphere','HDI','Age'].map(function(m,i){return '<button data-m="'+m.toLowerCase()+'"'+(i===0?' class="on"':'')+'>'+m+'</button>';})""",
     """['Hemisphere','HDI','Age'].map(function(m,i){return '<button data-m="'+m.toLowerCase()+'"'+(i===2?' class="on"':'')+'>'+m+'</button>';})"""),

    # Faith-PD figure: carry the age PCoA's baby-to-adult silhouettes onto the lifespan axis, and
    # drop the last of the participant-voice copy (the caption still spoke to "you")
    ("""    s+=youDot(xB(you.a),yB(di(you.f)),7)+youLabel(xB(you.a),yB(di(you.f)),'You');
    s+='</svg>'; scrB.innerHTML=s;""",
     """    s+='</svg>'; scrB.innerHTML=s;"""),
    # The silhouettes go in a band BELOW the axis, not inside the plot: the infant end of the
    # scatter is far too dense for a watermark to survive there. Deepening the bottom margin by
    # the same amount keeps the plotting area exactly where it was.
    ("const W2=660,H2=380,mL2=52,mR2=14,mT2=14,mB2=42; let filt='All';",
     "const W2=660,H2=430,mL2=52,mR2=14,mT2=14,mB2=92; let filt='All';"),
    ("""    s+='</svg>'; scrB.innerHTML=s;""",
     """    s+='<g opacity="0.95">'+fig(SY_BABY,SY_BABY_VB,mL2+30,H2-10,42,syRamp(0,SY_AGE))
      +fig(SY_ADULT,SY_ADULT_VB,W2-mR2-34,H2-10,60,syRamp(1,SY_AGE))+'</g>';
    s+='</svg>'; scrB.innerHTML=s;"""),
    ("    else { var rel=(you.f>near.f?'higher than':(you.f<near.f?'lower than':'about')); body='your diversity index of <b>'+youi+'</b> is <b>'+rel+'</b> the '+reg+' median for ages '+S.bins[bi]+'–'+S.bins[bi+1]+'.'; }",
     "    else { var lo=la[0], hi=la[la.length-1]; body='the '+reg+' median climbs from <b>'+di(lo.f).toFixed(1)+'</b> in the youngest age band to <b>'+di(hi.f).toFixed(1)+'</b> in the oldest.'; }"),
    ("""    var la=lines[filt]||lines.All||[]; var near=la.length>=2?la.reduce(function(b,p){return Math.abs(p.a-you.a)<Math.abs(b.a-you.a)?p:b;},la[0]):null;
    var bi=0; for(var q=0;q<S.bins.length-1;q++){ if(you.a>=S.bins[q]&&you.a<S.bins[q+1]){bi=q;break;} }
    var reg=(filt==='All'?'global':filt), body, youi=di(you.f).toFixed(1);
    if(!near) body='there are too few '+reg+' samples spread across ages to draw a lifespan median.';""",
     """    var la=lines[filt]||lines.All||[];
    var reg=(filt==='All'?'global':filt), body;
    if(la.length<2) body='there are too few '+reg+' samples spread across ages to draw a lifespan median.';"""),
]
for old, new in REFRAME:
    if old not in js:
        raise SystemExit("reframe target missing (prototype changed?):\n  " + old[:110])
    js = js.replace(old, new)
print("  reframed %d passages" % len(REFRAME))

js = js.rstrip() + """

/* ---- surface for the poopomics site: the site calls these directly ---- */
window.poopLens = { tree: buildTree, studies: buildSeeYourself };
"""
open(os.path.join(HERE, "lenses.js"), "w").write(js)
print("lenses.js  %d -> %d chars (%.0f%% dropped)"
      % (orig_len, len(js), 100 * (1 - len(js) / orig_len)))

# ---------------- css ----------------
# Take the component stylesheet and the see-yourself stylesheet, minus the rules that own the
# prototype's own page chrome (those would fight the site's layout).
blocks = []
for m in re.finditer(r'<style([^>]*)>', html):
    attrs = m.group(1)
    if "agp-fonts" in attrs: continue          # 179 KB of embedded webfonts; the site links Mulish
    body = html[m.end():html.index("</style>", m.end())]
    if len(body) > 200: blocks.append(body)

DROP = re.compile(r'(^|,)\s*(html|body|\.atlas|\.rail|\.rail-foot|\.brand|\.lens|\.hud|\.intro'
                  r'|\.intro-card|\.enter-btn|\.nojs|\.io-ring|\.stage)\b')
def split_rules(css):
    """Yield (selector_or_none, text) for top-level rules, keeping @-blocks whole."""
    out, i, n = [], 0, len(css)
    while i < n:
        br = css.find("{", i)
        if br < 0: out.append((None, css[i:])); break
        sel = css[i:br]
        d, k = 0, br
        while k < n:
            if css[k] == "{": d += 1
            elif css[k] == "}":
                d -= 1
                if d == 0: break
            k += 1
        out.append((sel, css[i:k + 1])); i = k + 1
    return out

# the prototype's :root is kept for its component tokens, but its font stack would land after
# ours in the built page and win, so that one declaration is stripped
FONT_DECL = re.compile(r"--sans\s*:[^;]+;")

kept, dropped = [], 0
for css in blocks:
    for sel, text in split_rules(css):
        if sel and not sel.lstrip().startswith("@") and DROP.search(sel):
            dropped += 1; continue
        kept.append(FONT_DECL.sub("", text))
# The prototype drew both control rows as bare text, which does not read as clickable on this
# page. These land after the rules they override, so they win without needing extra specificity.
BUTTONS = """
  .segbar button,.chipbar button{ background:#ffffff12; border:1px solid #ffffff2e;
    color:var(--ink); transition:background .18s,border-color .18s,color .18s; }
  .segbar button:hover,.chipbar button:hover{ background:#ffffff26; border-color:#ffffff5c; }
  .segbar button.on,.chipbar button.on{ background:var(--accent-btn); border-color:transparent;
    color:#fff; }
  .segbar{ gap:6px; padding:4px; }
  .chipbar{ gap:8px; }
"""
kept.append(BUTTONS)
open(os.path.join(HERE, "lenses.css"), "w").write("".join(kept))
print("lenses.css %d chars (%d page-chrome rules dropped)"
      % (sum(len(k) for k in kept), dropped))
