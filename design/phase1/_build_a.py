from _gen_motifs import fan, globe, reuse_grid

TIPS = ["#6f8ba8", "#2997ff", "#f0b429", "#7fb069", "#c66b6b"]

HEAD = '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Mulish:ital,wght@0,300..900;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
  <style>
    body { margin: 0; background: #0b0c0e; }
    a { color: #2997ff; text-decoration: none; }
    a:hover { color: #47a6ff; }
    .card { transition: transform .3s cubic-bezier(.2,.7,.2,1), border-color .3s, box-shadow .3s, background .3s; }
    .card:hover { transform: translateY(-7px); border-color: #ffffff40; background: #1d2024;
                  box-shadow: 0 1px 2px #00000066, 0 34px 64px -22px #000000; }
    .card:hover .go { transform: translateX(7px); opacity: 1; }
    .card:hover .rule { width: 100%; }
    .go { transition: transform .3s cubic-bezier(.2,.7,.2,1), opacity .3s; opacity: .5; }
    .rule { transition: width .45s cubic-bezier(.2,.7,.2,1); }
    .nav a { color: #a1a1a6; }
    .nav a:hover { color: #f5f5f7; }
  </style>
</helmet>
'''

ARROW = ('<svg class="go" width="22" height="22" viewBox="0 0 24 24" fill="none" '
         'stroke="#2997ff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
         '<path d="M5 12h13"/><path d="M12.5 5.5 19 12l-6.5 6.5"/></svg>')

def stat(v, l):
    return (
        '<div style="display: flex; flex-direction: column; gap: 3px">'
        f'<div style="font: 700 19px/1 Mulish, sans-serif; color: #f5f5f7; letter-spacing: -0.02em">{v}</div>'
        f'<div style="font: 500 9.5px/1 \'IBM Plex Mono\', monospace; color: #86868b; '
        f'letter-spacing: 0.1em; text-transform: uppercase">{l}</div>'
        '</div>'
    )

def card(idx, abbr, title, desc, motif, stats):
    return f'''    <a href="#" class="card" style="position: relative; overflow: hidden; display: flex; flex-direction: column; padding: 26px 26px 24px; background: #141619; border: 1px solid #ffffff14; border-radius: 18px; box-shadow: 0 1px 2px #00000066, 0 12px 34px -14px #000000cc">
      <div style="display: flex; justify-content: space-between; align-items: flex-start">
        <div style="font: 500 11px/1 'IBM Plex Mono', monospace; color: #86868b; letter-spacing: 0.12em">{idx}</div>
        {ARROW}
      </div>
      <div style="margin: 20px 0 22px">{motif}</div>
      <div style="font: 500 10.5px/1 'IBM Plex Mono', monospace; color: #2997ff; letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 9px">{abbr}</div>
      <div style="font: 800 25px/1.1 Mulish, sans-serif; color: #f5f5f7; letter-spacing: -0.025em; margin-bottom: 11px; text-wrap: pretty">{title}</div>
      <div style="font: 400 13.5px/1.55 Mulish, sans-serif; color: #a1a1a6; margin-bottom: 22px; text-wrap: pretty">{desc}</div>
      <div style="margin-top: auto; display: flex; gap: 26px; padding-top: 16px; border-top: 1px solid #ffffff14">
        {stats}
      </div>
      <div class="rule" style="position: absolute; left: 0; bottom: 0; height: 2px; width: 32%; background: #2997ff"></div>
    </a>'''

BODY = f'''<div style="width: 1280px; background: radial-gradient(130% 120% at 50% -8%, #16181c 0%, #0b0c0e 60%); font-family: Mulish, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; color: #f5f5f7; -webkit-font-smoothing: antialiased">

  <header style="display: flex; justify-content: space-between; align-items: center; padding: 22px 56px; border-bottom: 1px solid #ffffff14">
    <div style="display: flex; flex-direction: column; gap: 5px">
      <div style="font: 800 19px/1 Mulish, sans-serif; letter-spacing: -0.02em">poopomics</div>
      <div style="font: 500 9.5px/1 'IBM Plex Mono', monospace; color: #86868b; letter-spacing: 0.1em; text-transform: uppercase">UC San Diego &nbsp;·&nbsp; Northwestern &nbsp;·&nbsp; Johns Hopkins</div>
    </div>
    <nav class="nav" style="display: flex; gap: 30px; font: 400 13.5px/1 Mulish, sans-serif">
      <a href="#">Projects</a>
      <a href="#">People</a>
      <a href="#">Publications</a>
      <a href="#">Data</a>
    </nav>
  </header>

  <section style="padding: 74px 56px 46px">
    <div style="font: 500 10.5px/1 'IBM Plex Mono', monospace; color: #f0b429; letter-spacing: 0.16em; text-transform: uppercase; margin-bottom: 22px">Knight Lab &nbsp;/&nbsp; Amato Lab</div>
    <h1 style="margin: 0; max-width: 880px; font: 800 57px/1.03 Mulish, sans-serif; letter-spacing: -0.035em; text-wrap: pretty">Every gut microbiome ever published, in one comparable dataset.</h1>
    <p style="margin: 22px 0 0; max-width: 640px; font: 400 17px/1.6 Mulish, sans-serif; color: #c7c7cc; text-wrap: pretty">Three projects, one aim: make the world's microbiome data actually usable — across the animal tree of life, across human populations, and across the literature itself.</p>
  </section>

  <section style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; padding: 0 56px 40px">
{card("01", "GMToL", "Gut Microbiome Tree of Life", "Gut microbiomes compiled across the animal kingdom &mdash; chordates to arthropods to annelids &mdash; and curated for even coverage of phylogeny, diet, ecology and geography.", fan("#6f8ba8", TIPS), stat("17,000", "samples") + stat("828", "host species"))}
{card("02", "HMToL", "Human Microbiome Tree of Life", "The human-focused successor: a global gut microbiome atlas that deliberately reaches the populations the literature has left out.", globe("#6f8ba8", "#f0b429"), stat("170", "studies") + stat("79", "countries"))}
{card("03", "MMC", "Microbiome Metadata Crisis", "A systematic review of the field's own data. Most published microbiome data is public but not reusable &mdash; we quantified how much, and what it would take to fix.", reuse_grid("#22252b", "#3d4a5c", "#f0b429"), stat("2,300", "papers reviewed") + stat("10.8%", "reusable"))}
  </section>

  <footer style="display: flex; justify-content: space-between; align-items: center; padding: 20px 56px 30px; border-top: 1px solid #ffffff14; font: 400 12.5px/1 Mulish, sans-serif; color: #86868b">
    <div>DeGregori et&nbsp;al. 2024 &nbsp;·&nbsp; <em style="font-style: italic">Biological Reviews</em> &nbsp;·&nbsp; <a href="#">Gut microbiomes across the tree of life</a></div>
    <div>@poopomics</div>
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

open("Main.dc.html", "w").write(HEAD + BODY + TAIL)
print("Main.dc.html", len(HEAD + BODY + TAIL))
