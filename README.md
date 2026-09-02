# poopomics.com

The site for three projects: the Gut Microbiome Tree of Life (GMToL), the Human Microbiome Tree
of Life (HMToL) and the Microbiome Metadata Crisis (MMC) — and the ~450 undergraduates, graduate
students, postdocs and professors across 19 institutions who built them.

## Building

```bash
./publish
```

writes two things:

| Output | What it is |
|---|---|
| `site/` | what gets uploaded: `index.html` plus hashed asset files. ~0.59 MB over the wire for the document; images load as they are needed |
| `deploy/index.html` | the same page as one self-contained file, everything inlined (7.4 MB) |

`build_site.py --site` produces the first, `build_site.py` on its own the second.

## Editing

Everything that changes week to week — news items, the roster, institutions, team labels — is in
[`build/content.yaml`](build/content.yaml). Edit that and run `./publish`; you should not need to
open the Python.

Figure captions and the project write-ups live in `build/build_site.py`, next to the figures they
describe.

## How it is put together

| Path | |
|---|---|
| `build/build_site.py` | assembles the page from everything below |
| `build/content.yaml` | the editable content |
| `build/figs/*.py` | figure scripts — matplotlib, emitting dark SVG whose labels use the page font |
| `build/people/` | face extraction (OpenCV) and the collage strips |
| `build/lenses/` | the two interactive HMToL figures, extracted from an earlier prototype |
| `reference/STATUS.md` | a running record of every change and why |
| `deploy/STEPS.md` | deployment |

## Reuse

The build software is MIT licensed — see [LICENSE](LICENSE).

The photographs and figures are not. The portraits are used with the permission of the students
pictured, given for media use on this project; that permission does not travel to third parties.
The GMToL figures accompany a preprint and the HMToL dataset is not yet published. Please ask
before reusing anything in `build/people/`, `build/figs/gmtol/` or `build/figs/hmtol/`.

Third-party photographs in the news section are credited in `build/news/credits.json` and are
public domain, CC0, or CC BY 4.0.
