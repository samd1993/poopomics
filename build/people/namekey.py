"""One canonical form per person, shared by the face pipeline and the site builder.

Names reach us from five places that spell them differently: manuscript author lists (middle
initials, accents), the old project site, Zoom display names, the MMC headshot slide, and
filenames people typed themselves. `key()` collapses those to one identity; `best()` picks which
spelling to actually show.
"""
import re
import unicodedata

# Decided with Sam rather than guessed: a bare first name, a surname typo across two author
# lists, and one filename that arrived surname-first.
ALIASES = {
    "michael": "michael schweitzer",
    "jianshu zhou": "jianshu zhao",
    "wu kevin": "kevin wu",
    "diego wang": "xaolin wang",      # a replacement portrait filed under his short name
    "samuel degregori": "sam degregori",
}

# where the automatic pick is not the form we want on the page
PREFERRED = {
    "sam degregori": "Sam Degregori",
    "kevin wu": "Kevin Wu",
    "michael schweitzer": "Michael Schweitzer",
    "jianshu zhao": "Jianshu Zhao",
    "xaolin wang": "Xaolin (Diego) Wang",
}


def fold(name):
    n = unicodedata.normalize("NFKD", name)
    n = "".join(c for c in n if not unicodedata.combining(c))
    return re.sub(r"[^a-z ]", " ", n.lower()).split()


def is_initial(tok):
    return len(tok.rstrip(".")) == 1


def key(name):
    """Identity: first and last token, accents and middle names discarded."""
    toks = [t for t in fold(name) if not is_initial(t)]
    if not toks:
        return name.strip().lower()
    k = toks[0] if len(toks) == 1 else "%s %s" % (toks[0], toks[-1])
    return ALIASES.get(k, ALIASES.get(" ".join(toks), k))


def score(name):
    """Prefer the fullest spelling: real middle names help, bare initials hurt."""
    raw = name.split()
    full = sum(1 for t in raw if not is_initial(t))
    inits = sum(1 for t in raw if is_initial(t))
    accents = 1 if any(unicodedata.combining(c)
                       for c in unicodedata.normalize("NFKD", name)) else 0
    return full * 10 - inits * 3 + accents + len(name) / 100.0


def best(variants):
    """The spelling to display for one person, given every spelling we have seen."""
    k = key(variants[0])
    if k in PREFERRED:
        return PREFERRED[k]
    return max(variants, key=score)


def canonicalise(names):
    """[names] -> (display name per key, ordered unique display names)."""
    groups = {}
    for n in names:
        if n:
            groups.setdefault(key(n), []).append(n)
    display = {k: best(v) for k, v in groups.items()}
    return display, [display[k] for k in groups]
