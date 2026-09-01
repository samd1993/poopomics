Photos for the news section on the front page.

`build_site.py` looks for `asm-2026.jpg` (or .png/.webp) here and drops it into the ASM Microbe
item. If the file is absent the item still renders, with a marked placeholder in its place — so
the section never silently loses a story.

To add the ASM photo: save it here as `asm-2026.jpg` and re-run `python3 build_site.py`.
HEIC converts with `sips -s format jpeg in.heic --out news/asm-2026.jpg`.
