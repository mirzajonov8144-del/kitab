"""Builds data/hadis.json for the "Hadislar" screen. Nothing is typed by hand or edited.

Sources (owner's plan, 2026-11-25):
- HadeethEnc (hadeethenc.com API, language=uz): Arabic text, Uzbek translation, attribution, grade,
  explanation (sharh) and benefits. Copied verbatim; the Uzbek stays in Cyrillic.
- sunnah.com (Sahih al-Bukhari): the hadith NUMBER. A HadeethEnc hadith gets "Bukhari N" only when every quoted
  part of its Arabic text (between « and ») is found, letter for letter (harakat ignored), inside the Arabic of
  sunnah.com bukhari:N, in the same order. HadeethEnc gives no numbers, and its "متفق عليه" wording can be Muslim's,
  so a hadith whose words are not found in Bukhari is left out of this first part.
  The companion named in HadeethEnc's intro ("عن X رضي") must also be in the Bukhari text (so the words are not
  taken from another companion's hadith); if the name is written differently there (e.g. "ابن عمر" = "عن ابيه"),
  the hadith is left out too. HadeethEnc duplicates (same Bukhari number, same letters) are kept once.
- The matched parts are then compared WITH harakat (after the known harmless encodings: U+06E1 -> U+0652, tatweel
  dropped). Any difference -> "farq": both variants are stored and shown side by side; neither is chosen.

Only the NUMBER and the compared parts are taken from sunnah.com (no bulk copying of its text).
Everything is "Olim tekshiruvi kerak".

Two steps:
  1) python -I -X utf8 tools/build_hadis.py find <cache_dir>
     For each HadeethEnc hadith marked Bukhari / "Muttafaqun alayh", search sunnah.com and keep the first
     bukhari:N whose Arabic contains the hadith's words. Writes tools/hadis-bukhari.json (HadeethEnc id -> ref).
  2) python -I -X utf8 tools/build_hadis.py build <cache_dir> data
     Re-checks every pair from tools/hadis-bukhari.json and writes data/hadis.json.
cache_dir keeps downloaded pages (outside the repo) so a re-run does not download them again.
"""
import json, sys, os, re, time, datetime, urllib.request, urllib.parse
from html.parser import HTMLParser

MODE, CACHE = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
MAPF = os.path.join(HERE, "hadis-bukhari.json")
UA = {"User-Agent": "kitab-data-build"}
TODAY = datetime.date.today().isoformat()
os.makedirs(CACHE, exist_ok=True)

def fetch(url, name, delay=1.0):
    f = os.path.join(CACHE, name)
    if os.path.exists(f):
        return open(f, encoding="utf-8").read()
    for t in range(6):   # the network sometimes drops for a minute
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                s = r.read().decode("utf-8")
            break
        except Exception as e:
            err = e; time.sleep(20)
    else:
        raise err
    open(f, "w", encoding="utf-8").write(s)
    time.sleep(delay)
    return s

def he(i, lang="uz"):
    return json.loads(fetch(f"https://hadeethenc.com/api/v1/hadeeths/one/?language={lang}&id={i}", f"he_{lang}_{i}.json", 0.3))

def he_all():
    """{id: [root category ids]} for every Uzbek HadeethEnc hadith (a root's list includes its sub-categories),
    and the full category list."""
    cats = json.loads(fetch("https://hadeethenc.com/api/v1/categories/list/?language=uz", "he_cats_uz.json", 0.3))
    ids = {}
    for c in cats:
        if c["parent_id"]:
            continue
        p = 1
        while True:
            j = json.loads(fetch(f"https://hadeethenc.com/api/v1/hadeeths/list/?language=uz&category_id={c['id']}&page={p}&per_page=100",
                                 f"he_list_uz_{c['id']}_{p}.json", 0.3))
            for h in j["data"]:
                ids.setdefault(h["id"], []).append(c["id"])
            if p >= int(j["meta"]["last_page"]):
                break
            p += 1
    return ids, cats

class ByClass(HTMLParser):
    """Text of the first element having each wanted class."""
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

class SearchResults(HTMLParser):
    """sunnah.com search page: {ref: Arabic text} of the results (text is put under the last link seen)."""
    def __init__(self):
        super().__init__(convert_charrefs=True); self.ref = None; self.res = {}; self.depth = 0; self.cur = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        m = re.fullmatch(r"/([a-z]+:\d+[a-z]?)", a.get("href") or "")
        if m: self.ref = m.group(1)
        if self.cur is not None: self.depth += 1
        elif "arabic_hadith_full" in (a.get("class") or "").split() and self.ref:
            self.cur = self.ref; self.depth = 1; self.res[self.cur] = ""
    def handle_endtag(self, tag):
        if self.cur is not None:
            self.depth -= 1
            if self.depth == 0: self.cur = None
    def handle_data(self, d):
        if self.cur is not None: self.res[self.cur] += d

def sunnah(ref):
    p = ByClass(["arabic_hadith_full", "hadith_reference"])
    p.feed(fetch(f"https://sunnah.com/{ref}", "sunnah_" + ref.replace(":", "_") + ".html", 1.5))
    return p.out.get("arabic_hadith_full", "").strip()

# ---- letter matching ----
MARK = re.compile(r"[ً-ٰٟۖ-ۭـ]")
LETTER = re.compile(r"[ء-يٱ]")
FOLD = {"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه", "ؤ": "ء", "ئ": "ء"}

def letters(t):
    """[(index, folded letter)] of the base letters of t."""
    return [(i, FOLD.get(c, c)) for i, c in enumerate(t) if LETTER.match(c)]

def parts(h):
    """Quoted parts of the HadeethEnc Arabic («...»); if none, the text after the narrator intro."""
    ar = h["hadeeth_ar"]
    q = [m for m in re.findall(r"«([^«»]+)»", ar) if len(letters(m)) >= 8]
    if q:
        return q
    intro = h.get("hadeeth_intro_ar") or ""
    return [ar[len(intro):] if intro and ar.startswith(intro) else ar]

def span(text, part, start=0):
    """Locate part's letters in text (from letter position start). Returns (a, b, next_start) or None."""
    L = letters(text); s = "".join(c for _, c in L); k = "".join(c for _, c in letters(part))
    p = s.find(k, start)
    if p < 0 or not k:
        return None
    a, b = L[p][0], L[p + len(k) - 1][0] + 1
    while b < len(text) and MARK.match(text[b]):
        b += 1
    return a, b, p + len(k)

LAMALIF = re.compile(r"ل([اأإآ])([ًٌٍَُِّْ]+)")
CLUSTER = re.compile(r"[ًٌٍَُِّْ]+")

def norm(t):
    """For the harakat comparison: letters and marks only, known harmless encodings unified:
    - U+06E1 -> U+0652 and tatweel dropped (as in the Quran check);
    - lam-alif mark order: sunnah.com writes the lam's marks after the alif (lam, alif, fatha), HadeethEnc before it
      (lam, fatha, alif); both draw the same lam-alif ligature;
    - the order of several marks on one letter (shadda+fatha == fatha+shadda), as Unicode normalisation does."""
    t = t.replace("ۡ", "ْ").replace("ـ", "")
    t = "".join(c for c in t if LETTER.match(c) or MARK.match(c))
    t = LAMALIF.sub(lambda m: "ل" + m.group(2) + m.group(1), t)
    return CLUSTER.sub(lambda m: "".join(sorted(m.group(0))), t)

def narrator(h):
    """Bare letters of the key word of the companion named in the HadeethEnc intro ("عن X رضي ..."), or None.
    Case endings change "ابي/ابو/ابا" and Bukhari often drops "بن ...", so: after ابي/ابو/ابا/ابن the next word
    ("هريره", "مسعود", "عباس"); after عبد/ام the two words ("عبدالله"); else the first word ("انس", "عاءشه")."""
    intro = h["hadeeth_ar"].split("«")[0]
    m = re.search(r"عَ?نْ?\s+(.+?)\s+رَ?ضِ?يَ?", intro)
    if not m:
        return None
    w = ["".join(c for _, c in letters(x)) for x in m.group(1).split()]
    w = [x for x in w if x]
    if not w:
        return None
    if w[0] in ("ابي", "ابو", "ابا", "ابن") and len(w) > 1:
        return w[1]
    if w[0] in ("عبد", "ام") and len(w) > 1:
        return w[0] + w[1]
    return w[0]

def match(h, bukhari_ar):
    """None if the companion named by HadeethEnc is not in the Bukhari text, or if not every quoted part is in it
    in order; else the per-part comparison."""
    nm = narrator(h)
    if nm and nm not in "".join(c for _, c in letters(bukhari_ar)):
        return None
    out, pos = [], 0
    for prt in parts(h):
        sp = span(bukhari_ar, prt, pos)
        if not sp:
            return None
        a, b, pos = sp
        hs = span(prt, prt)  # the HadeethEnc part itself, trimmed to its letters
        mine = prt[hs[0]:hs[1]]
        theirs = bukhari_ar[a:b]
        out.append({"hadeethenc": mine, "sunnah": theirs, "farq": norm(mine) != norm(theirs)})
    return out

def is_bukhari(h):
    a = h.get("attribution_ar") or ""
    return "متفق عليه" in a or "البخاري" in a

# ---- step 1: find numbers ----
if MODE == "find":
    ids, _ = he_all()
    found = json.load(open(MAPF, encoding="utf-8")) if os.path.exists(MAPF) else {}
    todo = [i for i in ids if i not in found]
    for n, i in enumerate(todo, 1):
        h = he(i)
        if not is_bukhari(h):
            continue
        prt = max(parts(h), key=lambda x: len(letters(x)))
        words = [w for w in MARK.sub("", prt).split() if LETTER.search(w)]
        q = " ".join(re.sub(r"[^ء-يٱ]", "", w) for w in words[:8])
        page = fetch("https://sunnah.com/search?q=" + urllib.parse.quote(q), f"search_{i}.html", 2.0)
        refs = list(dict.fromkeys(re.findall(r'href="/(bukhari:\d+[a-z]?)"', page)))[:4]
        # The search page has each result's Arabic: use it only to pick likely refs (it is sometimes attached to
        # the wrong ref), then confirm on the hadith's own page. Otherwise try the first two refs' pages.
        sr = SearchResults(); sr.feed(page)
        likely = [r for r in refs if r in sr.res and match(h, sr.res[r])]
        hit = None
        for r in likely + [r for r in refs[:2] if r not in likely]:
            if match(h, sunnah(r)):
                hit = r; break
        found[i] = hit
        print(f"{n}/{len(todo)} {i} -> {hit} ({len(refs)} cand.)", flush=True)
        json.dump(found, open(MAPF, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
    ok = sum(1 for v in found.values() if v)
    print(f"bukhari found: {ok}, not found: {len(found) - ok}")
    sys.exit()

# ---- step 2: build ----
OUT = sys.argv[3]
ids, cats = he_all()
found = json.load(open(MAPF, encoding="utf-8"))
catname = {c["id"]: c["title"] for c in cats}
items, dropped, seen = [], [], {}
for i, ref in sorted(found.items(), key=lambda x: int(x[0])):
    if not ref:
        continue
    h = he(i)
    cmp_ = match(h, sunnah(ref))
    if not cmp_:   # e.g. the narrator check, added after the search: record it, leave the hadith out
        dropped.append(f"{i} {ref}"); found[i] = None; continue
    key = (ref, tuple("".join(c for _, c in letters(x["hadeethenc"])) for x in cmp_))
    if key in seen:   # HadeethEnc has the same hadith twice under two ids: keep the first
        dropped.append(f"{i} {ref} (= {seen[key]})"); continue
    seen[key] = i
    roots = sorted(set(ids.get(i, [])), key=int)
    items.append({
        "id": i, "cat": roots[0] if roots else None,
        "title": h["title"], "uz": h["hadeeth"], "ar": h["hadeeth_ar"],
        "attribution": h["attribution"], "attribution_ar": h["attribution_ar"],
        "grade": h["grade"], "grade_ar": h["grade_ar"],
        "explanation": h["explanation"], "hints": h.get("hints") or [],
        "url": f"https://hadeethenc.com/uz/browse/hadith/{i}",
        "bukhari": {"ref": ref, "num": ref.split(":")[1], "url": f"https://sunnah.com/{ref}", "compare": cmp_},
    })
json.dump(found, open(MAPF, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
if dropped:
    print("left out:", ", ".join(dropped))
used = sorted({x["cat"] for x in items if x["cat"]}, key=int)
json.dump({
    "status": "Olim tekshiruvi kerak", "built": TODAY, "retrieved": TODAY,
    "sources": {"text": "HadeethEnc.com (language=uz)", "number": "sunnah.com — Sahih al-Bukhari"},
    "cats": [{"id": c, "title": catname[c], "n": sum(1 for x in items if x["cat"] == c)} for c in used],
    "items": items,
}, open(os.path.join(OUT, "hadis.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
farq = sum(1 for x in items if any(c["farq"] for c in x["bukhari"]["compare"]))
print(f"hadis: {len(items)} (FARQ BOR: {farq}), cats: {len(used)}")
