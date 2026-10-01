"""Identity for consortium members: the shared name key plus the sheet's own spellings.

Used by build_mmc.py and import_photos.py, so a photo and a sheet row resolve to one person.
"""
import namekey

ALIASES = {
    "alexander nath": "alex nath",
    "maxwell hong": "max hong",
    "linden stadtlander": "lindy stadtlander",
    "sai malleboyina": "sahithi malleboyina",
    "qin(amy) xia": "amy xia",
    "yuxuan xie": "bree xie",
    "randima dona": "randima bellana",      # listed in full as Randima Hasanthi Bellana Vidanelage Dona
    # existing portraits filed under the name on the uploader's account
    "aditya": "aditya sankar",
    "mike qiu": "chuyu qiu",
    "eve": "evelina iskhakova",
    "vanessa yang": "fu yang",
    "david hong": "hyunseok hong",
    "trisha": "trisha dutta",
    "jake": "jake albert",
    "jack anderson": "john anderson",
    "kirsha": "kirsha selvakumar",
    "amy xia": "qin xia",
    "alan li": "yangxi li",
    "alex chen": "yuang chen",
    "温博栋": "bodong wen",
}


def key(name):
    k = namekey.key(name)
    return ALIASES.get(k, k)
