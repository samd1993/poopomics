INK = "#141513"
PAPER = "#fbfbf8"
MUTED = "#75776f"
HAIR = "#14151326"
ACCENT = "#1533b8"

HEAD = '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
  <style>
    body { margin: 0; background: #fbfbf8; }
    a { color: #1533b8; text-decoration: none; }
    a:hover { color: #0f2589; }
    .col { transition: background .22s linear, color .22s linear; }
    .col:hover { background: #141513; }
    .col:hover .c-num, .col:hover .c-title, .col:hover .c-val, .col:hover .c-open { color: #fbfbf8; }
    .col:hover .c-lab, .col:hover .c-body { color: #9a9c93; }
    .col:hover .c-code { color: #8fa6ff; }
    .col:hover .c-row { border-color: #fbfbf833; }
    .col:hover .c-bar { background: #fbfbf826; }
    .col:hover .c-bar > span { background: #8fa6ff; }
    .col:hover .c-open span { transform: translateX(6px); }
    .c-open span { display: inline-block; transition: transform .22s linear; }
    .nav a { color: #141513; }
    .nav a:hover { color: #1533b8; }
  </style>
</helmet>
'''

def cell(label, value, borderleft=True):
    bl = f"border-left: 1px solid {HAIR};" if borderleft else ""
    return (f'<div style="{bl} padding: 13px 18px; display: flex; flex-direction: column; gap: 6px">'
            f'<div style="font: 400 9px/1 \'IBM Plex Mono\', monospace; color: {MUTED}; letter-spacing: 0.16em; text-transform: uppercase">{label}</div>'
            f'<div style="font: 500 12.5px/1 \'IBM Plex Sans\', sans-serif; color: {INK}">{value}</div>'
            '</div>')

def column(num, code, title, body, bar_pct, bar_note, rows, borderleft=True):
    bl = f"border-left: 1px solid {HAIR};" if borderleft else ""
    trs = "".join(
        f'<div class="c-row" style="display: flex; justify-content: space-between; align-items: baseline; '
        f'padding: 10px 0; border-bottom: 1px solid {HAIR}">'
        f'<span class="c-lab" style="font: 400 10px/1 \'IBM Plex Mono\', monospace; color: {MUTED}; letter-spacing: 0.1em; text-transform: uppercase">{l}</span>'
        f'<span class="c-val" style="font: 600 15px/1 \'IBM Plex Sans\', sans-serif; color: {INK}; letter-spacing: -0.01em">{v}</span>'
        '</div>'
        for l, v in rows
    )
    return f'''      <a href="#" class="col" style="{bl} display: flex; flex-direction: column; padding: 30px 26px 26px; text-decoration: none">
        <div class="c-num" style="font: 400 64px/0.9 'IBM Plex Mono', monospace; color: {INK}; letter-spacing: -0.04em">{num}</div>
        <div class="c-code" style="margin: 20px 0 10px; font: 500 10.5px/1 'IBM Plex Mono', monospace; color: {ACCENT}; letter-spacing: 0.16em; text-transform: uppercase">{code}</div>
        <div class="c-title" style="font: 700 24px/1.15 'IBM Plex Sans', sans-serif; color: {INK}; letter-spacing: -0.025em; margin-bottom: 14px; text-wrap: pretty">{title}</div>
        <div class="c-body" style="font: 400 13.5px/1.6 'IBM Plex Sans', sans-serif; color: {MUTED}; margin-bottom: 26px; text-wrap: pretty">{body}</div>
        <div class="c-bar" style="height: 8px; background: {INK}14; display: flex; margin-bottom: 8px">
          <span style="display: block; width: {bar_pct}%; background: {ACCENT}"></span>
        </div>
        <div class="c-lab" style="font: 400 9.5px/1 'IBM Plex Mono', monospace; color: {MUTED}; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 26px">{bar_note}</div>
        <div style="margin-top: auto">{trs}</div>
        <div class="c-open" style="margin-top: 22px; font: 500 11px/1 'IBM Plex Mono', monospace; color: {ACCENT}; letter-spacing: 0.14em; text-transform: uppercase">Open <span>&rarr;</span></div>
      </a>'''

BODY = f'''<div style="width: 1280px; background: {PAPER}; font-family: 'IBM Plex Sans', -apple-system, sans-serif; color: {INK}; -webkit-font-smoothing: antialiased">

  <header style="border-bottom: 1px solid {HAIR}">
    <div style="display: grid; grid-template-columns: 300px repeat(3, minmax(0, 1fr)) 1fr; align-items: stretch">
      <div style="padding: 13px 26px; display: flex; align-items: center; font: 600 15px/1 'IBM Plex Mono', monospace; letter-spacing: 0.04em; text-transform: uppercase">poopomics</div>
      {cell("Host", "UC San Diego")}
      {cell("Partner", "Northwestern")}
      {cell("Partner", "Johns Hopkins")}
      <nav class="nav" style="border-left: 1px solid {HAIR}; display: flex; gap: 26px; align-items: center; justify-content: flex-end; padding: 13px 26px; font: 400 11px/1 'IBM Plex Mono', monospace; letter-spacing: 0.12em; text-transform: uppercase">
        <a href="#">Projects</a>
        <a href="#">People</a>
        <a href="#">Publications</a>
        <a href="#">Data</a>
      </nav>
    </div>
  </header>

  <section style="display: grid; grid-template-columns: 1.5fr 1fr; border-bottom: 1px solid {HAIR}">
    <div style="padding: 58px 26px 52px">
      <div style="font: 400 10.5px/1 'IBM Plex Mono', monospace; color: {MUTED}; letter-spacing: 0.16em; text-transform: uppercase; margin-bottom: 26px">Three projects &nbsp;/&nbsp; one dataset</div>
      <h1 style="margin: 0; max-width: 700px; font: 700 52px/1.06 'IBM Plex Sans', sans-serif; letter-spacing: -0.04em; text-wrap: pretty">The world's gut microbiome data, catalogued until it can actually be compared.</h1>
    </div>
    <div style="border-left: 1px solid {HAIR}; display: flex; flex-direction: column; justify-content: flex-end; padding: 32px 26px 30px; gap: 14px">
      <p style="margin: 0; font: 400 14.5px/1.65 'IBM Plex Sans', sans-serif; color: {MUTED}; text-wrap: pretty">We compile published gut microbiome data across the animal tree of life and across human populations, then audit whether the literature it came from can be reused at all.</p>
      <div style="font: 400 10px/1.7 'IBM Plex Mono', monospace; color: {MUTED}; letter-spacing: 0.1em; text-transform: uppercase">Knight Lab &nbsp;·&nbsp; Amato Lab &nbsp;·&nbsp; 280 undergraduate contributors</div>
    </div>
  </section>

  <section>
    <div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border-bottom: 1px solid {HAIR}">
{column("01", "GMToL", "Gut Microbiome Tree of Life", "Gut microbiomes compiled across the animal kingdom &mdash; chordates to arthropods to annelids &mdash; curated for even coverage of phylogeny, diet, ecology and geography.", 62, "Coverage of target host phyla", [("Samples", "17,000"), ("Host species", "828"), ("Status", "In analysis")], borderleft=False)}
{column("02", "HMToL", "Human Microbiome Tree of Life", "The human-focused successor: a global atlas that deliberately reaches the populations the literature has left out.", 41, "Countries represented of 193", [("Studies", "170"), ("Countries", "79"), ("Status", "Collecting")])}
{column("03", "MMC", "Microbiome Metadata Crisis", "A systematic review of the field's own record-keeping. Public does not mean reusable &mdash; we measured the gap and what closing it requires.", 11, "Papers with reusable annotations", [("Papers reviewed", "2,300"), ("Reusable", "10.8%"), ("Status", "In review")])}
    </div>
  </section>

  <footer style="display: flex; justify-content: space-between; align-items: center; padding: 20px 26px 30px; font: 400 11px/1 'IBM Plex Mono', monospace; color: {MUTED}; letter-spacing: 0.06em">
    <div>DeGregori et&nbsp;al. 2024 &nbsp;/&nbsp; Biological Reviews &nbsp;/&nbsp; <a href="#">Gut microbiomes across the tree of life</a></div>
    <div style="text-transform: uppercase; letter-spacing: 0.14em">@poopomics</div>
  </footer>

</div>'''

TAIL = '''
</x-dc>
<script data-dc-script data-props='{}'>
class Component extends DCLogic {
  renderVals() {
    return {};
  }
}
</script>
</body>
</html>
'''

open("SpecimenGrid.dc.html", "w").write(HEAD + BODY + TAIL)
print("SpecimenGrid.dc.html", len(HEAD + BODY + TAIL))
