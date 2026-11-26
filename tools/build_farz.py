"""Builds data/farz.json for the "Farzlar" screen (owner's request, 2026-11-26: in place of the Hadislar section,
the farz of the religion, of prayer, of iymon, of ghusl, of wudu and of the funeral prayer).

Everything is cut out of pages of O'zbekiston musulmonlari idorasi (muslim.uz) by this script, block by block
(paragraphs and list items, as the page has them). Nothing is typed by hand, shortened or re-spelled; the Uzbek stays
in Cyrillic. Only runs of white space are made single, as a browser shows them.
This script holds only page addresses, the first and the stop block of each part, and interface labels.

muslim.uz terms (page footer): free to use, with the line "Ўзбекистон мусулмонлари идораси расмий веб-портали хабар
беради", "расмий веб-портали" linked to https://muslim.uz and "хабар беради" linked to the article. The app does so.

Status: "Olim tekshiruvi kerak".
Usage: python -I -X utf8 tools/build_farz.py <cache dir outside the repo> data
"""
import json, sys, os, re, time, datetime, urllib.request
from html.parser import HTMLParser

CACHE, D = sys.argv[1], sys.argv[2]
os.makedirs(CACHE, exist_ok=True)
TODAY = datetime.date.today().isoformat()

PAGES = {
    "namoz": "https://muslim.uz/oz/c/prayer",
    "iymon": "https://muslim.uz/oz/e/post/11124-iymon-nima",
    "janoza": "https://muslim.uz/oz/e/post/20143-nurul-izoh-janoza",
}

# (key, label (Latin, interface), page, first block (starts with), stop block (starts with; not taken),
#  check: number of list blocks expected (a) б) в) / 1. 2. / <li>) or None for a question and answer)
PARTS = [
    ("din", "Dinning (Islomning) farzlari", "iymon", "– Мусулмонлик биноси нечта?", "– Исломнинг вожиблари", None),
    ("namoz", "Namozning farzlari", "namoz", "НАМОЗДАГИ ФАРЗ АМАЛЛАР", "НАМОЗНИНГ ВОЖИБЛАРИ", 12),
    ("iymon", "Iymonning farzlari", "iymon", "– Иймоннинг фарзлари нечта?", "– Иймоннинг вожиблари", None),
    ("gusl", "G'uslning farzlari", "namoz", "Ғуслнинг фарзлари", "Ғуслнинг суннатлари", 3),
    ("tahorat", "Tahoratning farzlari", "namoz", "ТАҲОРАТНИНГ ФАРЗЛАРИ", "ТАҲОРАТНИНГ СУННАТЛАРИ", 4),
    ("janoza", "Janoza namozining farzlari", "janoza", "Жаноза намозининг ҳукми ва рукнлари", "Изоҳ: Жаноза намозини", 6),
]

BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"}

class Blocks(HTMLParser):
    """[(tag, list tag of the parent ("ol"/"ul"/None), text)] of every text block, in page order."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.cur, self.lists = [], None, []
    def handle_starttag(self, tag, attrs):
        if tag in ("ol", "ul"):
            self.lists.append(tag)
        if tag == "br" and self.cur is not None:
            self.cur[2].append("\n")
        if tag in BLOCK:
            self.flush(); self.cur = (tag, self.lists[-1] if tag == "li" and self.lists else None, [])
    def handle_endtag(self, tag):
        if tag in BLOCK:
            self.flush()
        if tag in ("ol", "ul") and self.lists:
            self.lists.pop()
    def handle_data(self, d):
        if self.cur is not None:
            self.cur[2].append(d)
    def flush(self):
        if self.cur is not None:
            t = re.sub(r"[ \t\r\n\xa0]+", " ", "".join(self.cur[2])).strip()
            if t:
                self.out.append((self.cur[0], self.cur[1], t))
        self.cur = None

def fetch(url, name):
    f = os.path.join(CACHE, name)
    if not os.path.exists(f):
        for t in range(6):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (kitab-data-build)"})
                with urllib.request.urlopen(req, timeout=90) as r:
                    s = r.read().decode("utf-8")
                break
            except Exception as e:
                err = e; time.sleep(20)
        else:
            raise err
        open(f, "w", encoding="utf-8").write(s)
    return open(f, encoding="utf-8").read()

def page(key):
    html = fetch(PAGES[key], f"farz_{key}.html")
    p = Blocks(); p.feed(html); p.flush()
    title = re.search(r"<title>([^<]*)</title>", html)
    return html, p.out, (title.group(1).strip() if title else "")

def meta(key, html, blocks):
    """Article title, date and the source line under it (for posts); the guide page has none."""
    m = {"url": PAGES[key]}
    if "/e/post/" in PAGES[key]:
        h = next(t for tag, _, t in blocks if tag in ("h1", "h2", "h3"))
        m["title"] = h
        d = re.search(r"(\d\d\.\d\d\.\d{4})", html[html.find(h):])
        m["date"] = d.group(1) if d else None
        if key == "iymon":   # the article ends with its book reference and translator
            texts = [t for _, _, t in blocks]
            k = next(n for n, t in enumerate(texts) if "Чаҳор китоб" in t)
            if not texts[k + 1].endswith("таржимаси"):
                sys.exit("iymon: tarjimon qatori topilmadi")
            m["from"] = texts[k:k + 2]
    return m

LISTMARK = re.compile(r"^(?:[а-я]\)|\d+\.)\s")

out, pages, errors = [], {}, []
for key, label, pk, first, stop, check in PARTS:
    if pk not in pages:
        html, bl, title = page(pk)
        pages[pk] = (html, bl, title, meta(pk, html, bl))
    html, bl, title, m = pages[pk]
    i = next((n for n, b in enumerate(bl) if b[2].startswith(first)), None)
    if i is None:
        errors.append(f"{key}: «{first}» topilmadi"); continue
    j = next((n for n in range(i + 1, len(bl)) if bl[n][2].startswith(stop)), None)
    if j is None or j - i > 40:
        errors.append(f"{key}: «{stop}» topilmadi"); continue
    part = [{"tag": "h" if tag.startswith("h") else tag, "list": lst, "text": t} for tag, lst, t in bl[i:j]]
    n_items = sum(1 for b in part if b["tag"] == "li" or LISTMARK.match(b["text"]))
    if check is not None and n_items != check:
        errors.append(f"{key}: {n_items} band, {check} kutilgan")
    out.append({"key": key, "label": label, "source": pk, "blocks": part})

if errors:
    sys.exit("\n".join(errors))

json.dump({
    "status": "Olim tekshiruvi kerak",
    "built": TODAY, "retrieved": TODAY,
    "site": "Ўзбекистон мусулмонлари идораси (muslim.uz)",
    "sources": {k: v[3] | {"page_title": v[2]} for k, v in pages.items()},
    "parts": out,
}, open(os.path.join(D, "farz.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for p in out:
    print(p["key"], len(p["blocks"]), "blok")
