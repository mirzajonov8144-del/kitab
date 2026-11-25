"""Builds data/zikr.json for the Tasbeh screen. Nothing is typed by hand or edited:
- Hadith text, reference and English translation are downloaded from sunnah.com (Sahih al-Bukhari).
- The zikr phrase shown on screen is cut out of that Arabic text, character for character.
  KEYS below are search keys only (bare letters, no harakat); they are never shown.
- Uzbek / Russian translations and a second Arabic text come from HadeethEnc (hadeethenc.com) API.
- The phrase is compared letter by letter with the same phrase in HadeethEnc. Any difference -> "farq": true,
  both variants are stored and shown side by side; neither is chosen.
- Exception (owner's decision, 2026-11-25): where no Uzbek translation exists in the source, data/zikr-uz-claude.json
  holds Claude's translation of the source's ru/en text. It is stored apart ("uz_claude") and shown as "not a source".
Usage: python -I -X utf8 tools/build_zikr.py <out_dir>    (out_dir = data)
"""
import json, sys, re, html, urllib.request, urllib.error, datetime
from html.parser import HTMLParser

ITEMS = [  # id, sunnah.com ref, HadeethEnc id (same hadith) or None, count, search keys (bare letters)
    # "cmp": a different HadeethEnc hadith that contains the same phrases; used ONLY to compare the phrase spelling.
    {"id": "namoz", "ref": "bukhari:843", "he": None, "cmp": "5475", "count": 33, "keys": ["سبحان الله", "الحمد لله", "الله أكبر"]},
    {"id": "tasbih100", "ref": "bukhari:6405", "he": "5516", "count": 100, "keys": ["سبحان الله وبحمده"]},
    {"id": "tahlil100", "ref": "bukhari:6403", "he": "65905", "count": 100,
     "keys": ["لا إله إلا الله وحده لا شريك له له الملك وله الحمد وهو على كل شيء قدير"]},
]
UA = {"User-Agent": "kitab-data-build"}
TODAY = datetime.date.today().isoformat()

def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read().decode("utf-8")

class ByClass(HTMLParser):
    """Collects the text of the first element having each wanted class (inside .actualHadithContainer)."""
    def __init__(self, wanted):
        super().__init__(convert_charrefs=True); self.wanted = wanted; self.out = {}; self.stack = []
    def handle_starttag(self, tag, attrs):
        cls = (dict(attrs).get("class") or "").split()
        hit = next((w for w in self.wanted if w in cls and w not in self.out), None)
        self.stack.append(hit)
        if hit: self.out[hit] = ""
    def handle_endtag(self, tag):
        if self.stack: self.stack.pop()
    def handle_data(self, d):
        for w in set(x for x in self.stack if x):
            self.out[w] += d

def sunnah(ref):
    p = ByClass(["arabic_hadith_full", "english_hadith_full", "hadith_reference"])
    p.feed(fetch(f"https://sunnah.com/{ref}"))
    sp = lambda s: re.sub(r"\s+", " ", s).strip()
    return {"ar": p.out["arabic_hadith_full"].strip(), "en": sp(p.out["english_hadith_full"]),
            "reference": sp(p.out["hadith_reference"]), "url": f"https://sunnah.com/{ref}"}

def hadeethenc(i, lang):
    try: return json.loads(fetch(f"https://hadeethenc.com/api/v1/hadeeths/one/?language={lang}&id={i}"))
    except urllib.error.HTTPError: return None

# --- cut a phrase out of a text by its bare-letter key ---
MARKS = re.compile(r"[ً-ٰٟۖ-ۭـ]")
FOLD = {"ى": "ي", "ة": "ه"}  # used for matching only; output keeps the source characters
def letters(t):
    """Indices and folded values of base letters (no marks, no spaces, no punctuation)."""
    return [(i, FOLD.get(c, c)) for i, c in enumerate(t) if not MARKS.match(c) and re.match(r"[ء-ي]", c)]
def cut(text, key):
    L = letters(text); k = "".join(FOLD.get(c, c) for c in key if re.match(r"[ء-ي]", c))
    s = "".join(c for _, c in L); pos = s.find(k)
    if pos < 0: return None
    a, b = L[pos][0], L[pos + len(k) - 1][0] + 1
    while b < len(text) and MARKS.match(text[b]): b += 1   # keep the last letter's harakat
    return text[a:b]

def merge_claude(recs, d):
    """Attach data/zikr-uz-claude.json (Claude's Uzbek translation of the source ru/en text, NOT a source) as "uz_claude",
    only where the source has no Uzbek translation. Kept in its own file so it is never mixed with source text."""
    try: c = json.load(open(f"{d}/zikr-uz-claude.json", encoding="utf-8"))
    except FileNotFoundError: return
    for r in recs:
        t = c["items"].get(r["id"])
        r["uz_claude"] = None if r["uz"] or not t else {**t, "made_by": c["made_by"], "date": c["date"], "status": c["status"], "note": c["note"]}

out = []
for it in ITEMS:
    s = sunnah(it["ref"])
    phrases = [cut(s["ar"], k) for k in it["keys"]]
    assert all(phrases), (it["ref"], phrases)
    rec = {"id": it["id"], "count": it["count"], "phrases": phrases, "hadith_ar": s["ar"], "en": s["en"],
           "source": {"collection": "Sahih al-Bukhari", "reference": s["reference"], "grade": "Sahih (Sahih al-Bukhari)",
                      "site": "sunnah.com", "url": s["url"], "retrieved": TODAY},
           "uz": None, "ru": None, "second": None, "status": "Olim tekshiruvi kerak"}
    cid = it["he"] or it.get("cmp")
    if cid:
        ar = hadeethenc(cid, "ar")
        cmp_ = []
        for k, p in zip(it["keys"], phrases):
            q = cut(ar["hadeeth"], k)
            assert q, (cid, k)
            cmp_.append({"sunnah": p, "hadeethenc": q, "farq": q != p})
        rec["second"] = {"site": "HadeethEnc", "id": cid, "same_hadith": bool(it["he"]), "hadeeth_ar": ar["hadeeth"],
                         "attribution": ar["attribution"], "grade": ar["grade"],
                         "url": f"https://hadeethenc.com/ar/browse/hadith/{cid}", "retrieved": TODAY, "compare": cmp_}
    if it["he"]:
        for lang in ("uz", "ru"):
            t = hadeethenc(it["he"], lang)
            if t: rec[lang] = {"text": t["hadeeth"], "attribution": t["attribution"], "grade": t["grade"],
                               "site": "HadeethEnc", "url": f"https://hadeethenc.com/{lang}/browse/hadith/{it['he']}", "retrieved": TODAY}
    out.append(rec)
    print(it["ref"], "phrases:", phrases, "| farq:", [c["farq"] for c in (rec["second"] or {}).get("compare", [])],
          "| uz:", bool(rec["uz"]), "ru:", bool(rec["ru"]))
merge_claude(out, sys.argv[1])
json.dump(out, open(f"{sys.argv[1]}/zikr.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
