# Going live on poopomics.com — Netlify DNS route

The domain's nameservers currently point at Google Cloud DNS
(`ns-cloud-d1…d4.googledomains.com`), which is why there are no A/CNAME records to edit in
Squarespace: Squarespace is the registrar, but it is not serving the zone. Rather than hunt for
the Google zone, hand DNS to Netlify. Changing nameservers is a registrar action, and that is
exactly what Squarespace does control.

Checked before recommending this: the domain has **no MX and no TXT records**, so no email or
domain verification depends on the old zone.

---

## 1. Upload the site  (~2 min)

Run `./publish` first if you have edited anything since.

1. Go to **app.netlify.com/drop**
2. Sign in (GitHub or email)
3. Drag the **`poopomics/site` folder** onto the drop area — the folder itself, not its contents.
   Not `deploy/`.
4. You get a URL like `https://cheerful-otter-1a2b3c.netlify.app`

## 2. Check it before touching DNS  (~5 min)

Open that URL on the laptop and on your phone. Click each card, open People, open HMToL and
scroll past the tree. Nothing about DNS is reversible in a hurry; this step is.

## 3. Name the site

Site configuration → **Change site name** → `poopomics`
Now it lives at `poopomics.netlify.app`.

## 4. Add the domain and take Netlify DNS

1. **Domain management** → **Add a domain** → type `poopomics.com` → Verify
2. Netlify sees it is registered elsewhere and offers two paths. Choose the one that sets up
   **Netlify DNS** (wording is usually "Set up Netlify DNS" or "Use Netlify DNS"), not the
   external-DNS path.
3. It creates a DNS zone and shows **four nameservers**, of the form
   `dns1.p01.nsone.net`, `dns2.p01.nsone.net`, `dns3…`, `dns4…`
   The digits vary by account. **Copy all four.**
4. Leave this page open.

## 5. Point the domain at them  (Squarespace)

1. `account.squarespace.com` → **Domains** → click **poopomics.com**
2. Find the **Nameservers** section. Depending on the panel version it sits on the domain's main
   page, under **DNS**, or under **Advanced settings**. You want the option for *custom* or
   *third-party* nameservers rather than the defaults.
3. Replace all four `ns-cloud-dN.googledomains.com` entries with Netlify's four.
4. Save.

## 6. Wait, then verify

Usually 15–60 minutes, occasionally longer. From the terminal:

```bash
dig +short NS poopomics.com          # should list dns1..4.pNN.nsone.net
dig +short www.poopomics.com         # should stop saying ghs.googlehosted.com
```

Then open `https://www.poopomics.com` in a private window. Netlify issues the HTTPS certificate
automatically once DNS resolves — if the padlock is missing at first, give it a few minutes.

## 7. Only then, retire the old site

Leave the Google Site published until the new one answers reliably. Unpublishing it is the one
step that is awkward to undo.

---

## Redeploying afterwards

```bash
./publish
```

then drag `site/` onto the same Netlify site (Deploys → drag-and-drop). Netlify keeps every
deploy, so rolling back is two clicks in the Deploys list.

## Before it is public

- **Unpublished figures.** Three GMToL captions cite manuscript figures from the paper under
  review at *Science*; every HMToL figure is unpublished data.
- **143,220 data entries** in the funnel is still 2,046 × 70 from the old export.
- The tier-by-year and sequencing panels come from that same older export — now said in their
  captions.
