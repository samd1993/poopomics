import math

def fan(stroke, tip_colors, sw=1.0, w=260, h=132, opacity="0.8"):
    """Radial phylogeny fan: lines from a bottom-centre root out to tips."""
    cx, cy, r = w/2, h - 6, h - 22
    parts = [f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" aria-hidden="true">']
    parts.append(f'<g stroke="{stroke}" stroke-width="{sw}" fill="none" opacity="{opacity}" stroke-linecap="round">')
    n = 13
    angs = [180 + (i + 0.5) * (180 / n) for i in range(n)]
    tips = []
    for a in angs:
        rad = math.radians(a)
        x, y = cx + r * math.cos(rad), cy + r * math.sin(rad)
        mx, my = cx + r * 0.44 * math.cos(rad), cy + r * 0.44 * math.sin(rad)
        # slight splay: kink at the mid radius
        parts.append(f'<path d="M {cx:.1f} {cy:.1f} L {mx:.1f} {my:.1f} L {x:.1f} {y:.1f}"/>')
        tips.append((x, y, a))
    # arc joining the tips
    parts.append(f'<path d="M {cx-r:.1f} {cy:.1f} A {r:.1f} {r:.1f} 0 0 1 {cx+r:.1f} {cy:.1f}" opacity="0.35" stroke-dasharray="2 4"/>')
    parts.append('</g>')
    # tip marks, coloured by "phylum"
    for i, (x, y, a) in enumerate(tips):
        c = tip_colors[i % len(tip_colors)]
        parts.append(f'<rect x="{x-2.5:.1f}" y="{y-2.5:.1f}" width="5" height="5" fill="{c}"/>')
    parts.append('</svg>')
    return "".join(parts)

def globe(stroke, dot, sw=1.0, w=260, h=132):
    """Graticule sphere with sampling dots."""
    cx, cy, r = w/2, h/2, h/2 - 8
    p = [f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" aria-hidden="true">']
    p.append(f'<g stroke="{stroke}" fill="none" stroke-width="{sw}" opacity="0.7">')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>')
    for f in (0.28, 0.62, 0.9):
        p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r*f:.1f}" ry="{r}"/>')
    for dy in (-0.62, -0.3, 0, 0.3, 0.62):
        yy = cy + r * dy
        rx = r * math.sqrt(max(0.0, 1 - dy * dy))
        p.append(f'<path d="M {cx-rx:.1f} {yy:.1f} L {cx+rx:.1f} {yy:.1f}"/>')
    p.append('</g>')
    pts = [(-0.55,-0.42),(-0.30,-0.55),(-0.10,-0.20),(0.22,-0.48),(0.48,-0.22),
           (0.60,0.18),(0.30,0.40),(-0.02,0.58),(-0.34,0.34),(-0.62,0.05),
           (0.05,-0.05),(-0.18,0.10),(0.38,0.02),(0.14,0.24)]
    for ux, uy in pts:
        p.append(f'<circle cx="{cx+r*ux:.1f}" cy="{cy+r*uy:.1f}" r="2.6" fill="{dot}"/>')
    p.append('</svg>')
    return "".join(p)

def reuse_grid(empty, partial, full, w=260, h=132, cols=12, rows=5,
               p_acc=0.633, p_use=0.108):
    """60 cells = the literature. 63.3% have an accession; 10.8% are actually reusable."""
    cells = cols * rows
    n_acc = round(cells * p_acc)
    n_use = round(cells * p_use)
    cw = (w - 4) / cols
    ch = (h - 4) / rows
    s = min(cw, ch) - 3
    p = [f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" aria-hidden="true">']
    i = 0
    for ry in range(rows):
        for rx in range(cols):
            x = 2 + rx * cw
            y = 2 + ry * ch
            if i < n_use:
                fill, op = full, "1"
            elif i < n_acc:
                fill, op = partial, "1"
            else:
                fill, op = empty, "1"
            p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{s:.1f}" height="{s:.1f}" fill="{fill}" opacity="{op}"/>')
            i += 1
    p.append('</svg>')
    return "".join(p)
