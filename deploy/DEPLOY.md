# Deploying poopomics.com

**Upload `../site/`, not this folder.** `site/` is the hosted build: a 2.6 MB `index.html`
(0.59 MB over the wire) plus an `assets/` folder of images the browser fetches only when it needs
them. `deploy/index.html` here is the single-file fallback — everything inlined, 7.4 MB, 4.3 MB
over the wire — kept for anywhere that can only take one file.

Rebuild both with:

```bash
./publish
```

Content — news, roster, institutions — is in `build/content.yaml`. Editing that and running
`./publish` is the whole loop for adding a student or a paper.

## What is live today

| Name | Record | Points at |
|---|---|---|
| `poopomics.com` | A | `198.185.159.145` — Squarespace (the registrar's parking address; Google Domains moved to Squarespace) |
| `www.poopomics.com` | CNAME | `ghs.googlehosted.com` — Google Sites, which serves the current site |

**Google Sites cannot host this file.** It only publishes pages built in its own editor; there is
no way to upload custom HTML. So the site has to move to a static host and DNS has to follow it.

## Steps

These need account access and DNS changes, so they are yours to run — I can prepare files but I
should not be entering credentials or changing registrar settings.

1. **Put the file on a host.** Any of these work with a single drag-and-drop, no CLI:
   - Cloudflare Pages — "Direct Upload", free, fastest globally
   - Netlify Drop (`app.netlify.com/drop`) — the shortest path; drag the folder in
   - GitHub Pages — if you would rather the site live in a repo alongside the build scripts

   Upload the `site/` folder, so the host serves its `index.html` at `/`.

2. **Check it on the host's own URL first** (`something.pages.dev` / `something.netlify.app`).
   Load it on a phone as well. First paint pulls about 1.7 MB — the document, the three face
   strips and the faces on screen; the other 180 portraits wait until someone opens People.

3. **Point the domain at it**, in the Squarespace domain dashboard:
   - `www` → CNAME to the host's target, replacing `ghs.googlehosted.com`
   - apex `poopomics.com` → the host's A/ALIAS records, replacing `198.185.159.145`
   - Keep whichever of the two you want as canonical and redirect the other; the old site used
     `www`, so keeping `www` canonical avoids breaking any links already in circulation.

4. **Leave the Google Site published** until DNS has propagated and the new one is confirmed
   working. Unpublishing it is the one step that is hard to walk back.

## Before it goes public

Settled first, because these are visible on the page and cannot be fixed after people have read
it:

- **Unpublished figures.** Three GMToL captions cite "Manuscript Fig. 2A / 3A / 3C" from the
  dataset paper that is under review at *Science*, and every HMToL figure is unpublished data.
  The note that disclosed this was removed on 31 Aug. Whether this may appear publicly is a
  call for you, Katherine and Rob — and possibly for the journal.
- **The MMC counts disagree with themselves.** The funnel caption says 3,300 articles; the graphic
  above it draws 33,564 → 2,305 → 2,046; the waffle says 260 of 2,046; the home card says 3,300.
- **Unverified claims.** "The most diverse human gut microbiome dataset to date (70 countries)"
  against 68 countries everywhere else on the site; "8 undergraduate-led subprojects"; "2
  submissions under review" when only one is accounted for.
- **University of Northern Colorado** sits under a heading reading "Medical School Acceptances";
  UNC Greeley has no MD programme.
- **185 named people, with photographs.** Most came from the old public site, but the acceptance
  news is new and personal — worth being sure Kaiyuan, Randima, Tyra, Saleem, Zoey, Luis, Diego,
  Emily and Sadaf are happy to have it published.
