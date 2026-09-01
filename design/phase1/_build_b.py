from _gen_motifs import fan, globe, reuse_grid

INK = "#23201b"
PAPER = "#f2ece0"
PLATE = "#faf6ec"
MUTED = "#6f675a"
RUST = "#9c4f2f"
MOSS = "#4d5b3a"

TIPS = [INK, RUST, MOSS, "#8a7a4e", INK]

HEAD = '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..600&display=swap">
  <style>
    body { margin: 0; background: #f2ece0; }
    a { color: #9c4f2f; text-decoration: none; }
    a:hover { color: #7d3d22; }
    .plate { transition: background .35s ease, border-color .35s ease, box-shadow .35s ease; }
    .plate:hover { background: #fffdf7; border-color: #23201b; box-shadow: 0 18px 40px -26px #23201b80; }
    .plate:hover .plate-title { text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 5px; }
    .plate:hover .num { color: #9c4f2f; }
    .num { transition: color .35s ease; }
    .nav a { color: #23201b; }
    .nav a:hover { color: #9c4f2f; }
  </style>
</helmet>
'''

def caption(t):
    return (f'<div style="font: italic 300 12.5px/1.5 Newsreader, Georgia, serif; color: {MUTED}; '
            f'text-align: center; padding: 0 6px">{t}</div>')

def plate(num, abbr, title, blurb, motif, cap, figures):
    figrow = "".join(
        f'<div style="display: flex; justify-content: space-between; align-items: baseline; '
        f'padding: 7px 0; border-bottom: 1px dotted {INK}40">'
        f'<span style="font: 400 11px/1 Newsreader, Georgia, serif; color: {MUTED}; '
        f'letter-spacing: 0.12em; text-transform: uppercase">{l}</span>'
        f'<span style="font: 500 15px/1 Newsreader, Georgia, serif; color: {INK}">{v}</span></div>'
        for l, v in figures
    )
    return f'''    <a href="#" class="plate" style="display: flex; flex-direction: column; padding: 26px 24px 22px; background: {PLATE}; border: 1px solid {INK}33">
      <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 26px">
        <span class="num" style="font: 400 15px/1 'Instrument Serif', Georgia, serif; color: {MUTED}; letter-spacing: 0.18em">{num}</span>
        <span style="font: 400 10.5px/1 Newsreader, Georgia, serif; color: {MUTED}; letter-spacing: 0.2em; text-transform: uppercase">{abbr}</span>
      </div>
      <div style="margin-bottom: 14px">{motif}</div>
      {caption(cap)}
      <div class="plate-title" style="margin: 26px 0 12px; font: 400 27px/1.12 'Instrument Serif', Georgia, serif; color: {INK}; letter-spacing: -0.005em; text-wrap: pretty">{title}</div>
      <div style="font: 300 14.5px/1.62 Newsreader, Georgia, serif; color: {MUTED}; margin-bottom: 22px; text-wrap: pretty">{blurb}</div>
      <div style="margin-top: auto; border-top: 1px solid {INK}33; padding-top: 4px">{figrow}</div>
    </a>'''

BODY = f'''<div style="width: 1280px; background: {PAPER}; font-family: Newsreader, Georgia, 'Times New Roman', serif; color: {INK}; -webkit-font-smoothing: antialiased">

  <header style="padding: 30px 64px 0">
    <div style="display: flex; justify-content: space-between; align-items: baseline; padding-bottom: 14px">
      <div style="font: 400 11px/1 Newsreader, Georgia, serif; color: {MUTED}; letter-spacing: 0.24em; text-transform: uppercase">Est.&nbsp;2023</div>
      <nav class="nav" style="display: flex; gap: 30px; font: 400 12px/1 Newsreader, Georgia, serif; letter-spacing: 0.16em; text-transform: uppercase">
        <a href="#">Projects</a>
        <a href="#">People</a>
        <a href="#">Publications</a>
        <a href="#">Data</a>
      </nav>
    </div>
    <div style="border-top: 1px solid {INK}; border-bottom: 3px double {INK}; padding: 26px 0 22px; text-align: center">
      <div style="font: 400 46px/1 'Instrument Serif', Georgia, serif; letter-spacing: 0.02em">poopomics</div>
      <div style="margin-top: 14px; font: 400 10.5px/1 Newsreader, Georgia, serif; color: {MUTED}; letter-spacing: 0.28em; text-transform: uppercase">UC San Diego &nbsp;&mdash;&nbsp; Northwestern &nbsp;&mdash;&nbsp; Johns Hopkins</div>
    </div>
  </header>

  <section style="display: grid; grid-template-columns: 1.55fr 1fr; gap: 56px; align-items: end; padding: 52px 64px 46px">
    <h1 style="margin: 0; font: 400 60px/1.04 'Instrument Serif', Georgia, serif; letter-spacing: -0.01em; text-wrap: pretty">A natural history of the gut, assembled from everything already published.</h1>
    <p style="margin: 0 0 8px; font: 300 16px/1.68 Newsreader, Georgia, serif; color: {MUTED}; text-wrap: pretty">Seventeen thousand gut microbiomes, eight hundred host species, and a field-wide audit of whether any of it can be reused. Three projects, one library.</p>
  </section>

  <section style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 26px; padding: 0 64px 44px">
{plate("I.", "GMToL", "Gut Microbiome Tree of Life", "Gut microbiomes compiled across the animal kingdom, from chordates to arthropods to annelids, curated for even coverage of phylogeny, diet, ecology and geography.", fan(INK, TIPS, sw=0.9, opacity="0.85"), "Plate I. Host phylogeny, time-calibrated, with phylum composition at the tips.", [("Samples", "17,000"), ("Host species", "828")])}
{plate("II.", "HMToL", "Human Microbiome Tree of Life", "The human-focused successor: a global gut microbiome atlas that deliberately reaches the populations the literature has left out.", globe(INK, RUST, sw=0.9), "Plate II. Global coverage of the human collection to date.", [("Studies", "170"), ("Countries", "79")])}
{plate("III.", "MMC", "Microbiome Metadata Crisis", "A systematic review of the field's own record-keeping. Most published microbiome data is public but not reusable; we measured how much, and what it would take to fix.", reuse_grid("#e2dac9", "#b9a98b", RUST), "Plate III. Of 60 studies, those with accessions, and those truly reusable.", [("Papers reviewed", "2,300"), ("Reusable", "10.8%")])}
  </section>

  <footer style="border-top: 1px solid {INK}; margin: 0 64px; padding: 18px 0 32px; display: flex; justify-content: space-between; align-items: baseline; font: 300 12.5px/1 Newsreader, Georgia, serif; color: {MUTED}">
    <div>DeGregori et&nbsp;al. 2024 &nbsp;&mdash;&nbsp; <em>Biological Reviews</em> &nbsp;&mdash;&nbsp; <a href="#">Gut microbiomes across the tree of life</a></div>
    <div style="letter-spacing: 0.14em; text-transform: uppercase">@poopomics</div>
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

open("FieldPlate.dc.html", "w").write(HEAD + BODY + TAIL)
print("FieldPlate.dc.html", len(HEAD + BODY + TAIL))
