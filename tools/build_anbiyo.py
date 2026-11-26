"""Builds data/anbiyo.json for the "Payg'ambarlar" (prophets) screen.

This script holds ONLY names used as search keys, references and interface labels. It contains no religious text:
the app shows verses from data/s/NNN.json (Tanzil Arabic, QuranEnc translations and footnotes, verbatim) and
hadiths from data/hadis.json (HadeethEnc + sunnah.com Bukhari number, verbatim).

Source for "25 prophets are named in the Quran, the first is Adam, the last is Muhammad":
  O'zbekiston musulmonlari idorasi, muslim.uz, "Иймон" (30.01.2019), https://muslim.uz/oz/e/post/28371-iymon
That article does not list the 25 names, so the list below is the 25 names that occur in the Arabic text and are
written as names in the Uzbek translation (both checked by machine). Order: Adam first and Muhammad last (as in the
article); the others in the order of their first mention in the Mushaf (computed, not a claim about history).

A verse is listed for a prophet when BOTH hold (checked by machine):
  - its Arabic text (Tanzil) contains one of the prophet's Arabic name forms as a whole word
    (bare letters, tatweel dropped; prefixes و ف ب ل ك ي and a tanwin alif allowed, e.g. "ونوحا", "يإبرهيم");
  - its Uzbek translation (or its footnote) contains the prophet's name (Cyrillic, as the translator writes it).
  The second condition removes words that only look like a name in Arabic: صالح "righteous", هود "Jews",
  يحيي "gives life".
Hadiths are listed for a prophet when the hadith's Uzbek text names him and its Arabic text contains his Arabic name
(a name after أبو/أبي/أبا or «Абу» is a companion's kunya, e.g. Abu Musa, and a reference such as [إبراهيم: 27]
is a sura name: neither counts).
For Muhammad ﷺ the expanded section adds: verses that address him "يا أيها النبي" / "يا أيها الرسول", and the hadiths
of data/hadis.json that HadeethEnc files under "Пайғамбаримиз Муҳаммад" (81) or "Пайғамбаримиз сийратлари" (367).

Prophets are never depicted: the app shows text only.
Usage: python -I -X utf8 tools/build_anbiyo.py <cache dir outside the repo> data
"""
import json, sys, re, os, time, datetime, urllib.request

CACHE, D = sys.argv[1], sys.argv[2]
os.makedirs(CACHE, exist_ok=True)
LET = re.compile(r"[ء-يٱ]")
FOLD = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه", "ؤ": "ء", "ئ": "ء"})

def bare(w):
    return "".join(c for c in w if LET.match(c) and c != "ـ").translate(FOLD)

def tokens(ar):
    return [bare(w) for w in ar.split()]

# (key, label (Latin, interface), Uzbek name regex (Cyrillic, search key only), Arabic bare name forms)
# A form with a space is a two-word name (e.g. ذا الكفل is matched on its second word with the first before it).
ANBIYO = [
    ("odam", "Odam", r"Одам(?!лар)", ["ءادم", "ادم"]),
    ("idris", "Idris", r"Идрис", ["ادريس"]),
    ("nuh", "Nuh", r"Нуҳ", ["نوح"]),
    ("hud", "Hud", r"Ҳуд(?!ҳуд)", ["هود"]),
    ("solih", "Solih", r"Солиҳ(?!а|лар|\s+амал)", ["صلح", "صالح"]),
    ("ibrohim", "Ibrohim", r"Иброҳим|Иброоҳиим", ["ابرهيم", "ابرهم", "ابراهيم"]),
    ("lut", "Lut", r"Лут", ["لوط"]),
    ("ismoil", "Ismoil", r"Исмоил", ["اسمعيل", "اسماعيل"]),
    ("ishoq", "Ishoq", r"Исҳоқ", ["اسحق", "اسحاق"]),
    ("yaqub", "Ya'qub", r"Яъқуб", ["يعقوب"]),
    ("yusuf", "Yusuf", r"Юсуф", ["يوسف"]),
    ("ayyub", "Ayyub", r"Айю?йуб|Айюб", ["ايوب"]),
    ("shuayb", "Shuayb", r"Шуъайб", ["شعيب"]),
    ("muso", "Muso", r"Мусо", ["موسي"]),
    ("horun", "Horun", r"Ҳорун", ["هرون", "هارون"]),
    ("zulkifl", "Zulkifl", r"Зул-?[Кк]ифл", ["ذا الكفل"]),
    ("dovud", "Dovud", r"Довуд", ["داود"]),
    ("sulaymon", "Sulaymon", r"Сулаймон", ["سليمن", "سليمان"]),
    ("ilyos", "Ilyos", r"Илёс", ["الياس", "ال ياسين"]),
    ("alyasa", "Alyasa'", r"[Аа]л-Ясаъ", ["اليسع"]),
    ("yunus", "Yunus", r"Юнус|Зуннун", ["يونس", "ذا النون"]),
    ("zakariyo", "Zakariyo", r"Закариё", ["زكريا"]),
    ("yahyo", "Yahyo", r"Яҳё", ["يحيي"]),
    ("iyso", "Iyso", r"Ийсо|Масийҳ", ["عيسي", "المسيح"]),
    ("muhammad", "Muhammad", r"Муҳаммад|Аҳмад", ["محمد", "احمد"]),
]
SURAREF = re.compile(r"\[[^\]]*:\s*\d+\]")  # a quoted verse's reference, e.g. [إبراهيم: 27], is a sura name
KUNYA = {"ابو", "ابي", "ابا"}
PREFIX = re.compile(r"^[وفبلكي]{0,2}$")

def has_name(toks, forms):
    for f in forms:
        parts = f.split()
        last = parts[-1]
        for i, t in enumerate(toks):
            if len(parts) == 1 and t.endswith(last + "ا"):  # tanwin alif: نوحا, لوطا
                t = t[:-1]
            if t.endswith(last) and PREFIX.match(t[: len(t) - len(last)]):
                if i and toks[i - 1] in KUNYA:  # أبو موسى, أبي أيوب: a companion's name, not the prophet
                    continue
                if len(parts) == 1:
                    return True
                prev = toks[i - 1] if i else ""
                if prev.endswith(parts[0]) and PREFIX.match(prev[: len(prev) - len(parts[0])]):
                    return True
    return False

def uz_rx(r):
    return re.compile(r"(?<![\w-])(?<!Абу )(?:" + r + r")")

suras = {n: json.load(open(f"{D}/s/{n:03}.json", encoding="utf-8")) for n in range(1, 115)}
hadis = json.load(open(f"{D}/hadis.json", encoding="utf-8"))["items"]

def fetch(url, name):
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        for i in range(6):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "kitab-data-build"}),
                                            timeout=60) as r:
                    data = r.read()
                break
            except Exception:
                if i == 5:
                    raise
                time.sleep(20)
        open(path, "wb").write(data)
    return json.load(open(path, encoding="utf-8"))

def he_cat(cid):
    ids, p = [], 1
    while True:
        r = fetch(f"https://hadeethenc.com/api/v1/hadeeths/list/?language=uz&category_id={cid}&page={p}&per_page=100",
                  f"anb_cat{cid}_{p}.json")
        ids += [x["id"] for x in r["data"]]
        if p >= int(r["meta"]["last_page"]):
            return ids
        p += 1

def ref_groups(refs):
    """[(s, a)] -> [{"s": s, "a": [a, ...]}] in Mushaf order"""
    out = []
    for s, a in refs:
        if out and out[-1]["s"] == s:
            out[-1]["a"].append(a)
        else:
            out.append({"s": s, "a": [a]})
    return out

report, items = [], []
for key, label, urx, forms in ANBIYO:
    rx = uz_rx(urx)
    refs, ar_only, uz_only = [], [], []
    for n, d in suras.items():
        for i, ar in enumerate(d["ar"]):
            a = has_name(tokens(ar), forms)
            u = bool(rx.search(d["uz"][i]) or rx.search(d["uz_fn"][i] or ""))
            if a and u:
                refs.append((n, i + 1))
            elif a:
                ar_only.append(f"{n}:{i+1}")
            elif rx.search(d["uz"][i]):
                uz_only.append(f"{n}:{i+1}")
    hids = [h["id"] for h in hadis if rx.search(SURAREF.sub("", h["uz"])) and has_name(tokens(SURAREF.sub("", h["ar"])), forms)]
    for h in hadis:
        if h["id"] in hids:
            print("  ", label, h["id"], h["title"][:90])
    if not refs:
        sys.exit(f"{label}: no verse")
    items.append({"key": key, "label": label, "first": f"{refs[0][0]}:{refs[0][1]}", "n": len(refs),
                  "verses": ref_groups(refs), "hadis": hids})
    report.append(f"{label}: {len(refs)} oyat, {len(hids)} hadis | faqat arabchada: {ar_only[:12]}"
                  f" | faqat tarjimada: {len(uz_only)} {uz_only[:8]}")

# order: Adam first, Muhammad last, the rest by first mention
mid = sorted(items[1:-1], key=lambda x: tuple(map(int, x["first"].split(":"))))
items = [items[0]] + mid + [items[-1]]
if len(items) != 25:
    sys.exit(f"{len(items)} prophets, expected 25")

# Muhammad ﷺ: address verses
NABI = [("يايها", "النبي"), ("يايها", "الرسول")]
addr = {"nabiy": [], "rasul": []}
for n, d in suras.items():
    for i, ar in enumerate(d["ar"]):
        t = tokens(ar)
        for j in range(len(t) - 1):
            if t[j] == "يايها" and t[j + 1] in ("النبي", "الرسول"):
                addr["nabiy" if t[j + 1] == "النبي" else "rasul"].append((n, i + 1))
                break
have = {h["id"] for h in hadis}
mh = [i for i in dict.fromkeys(he_cat(81) + he_cat(367)) if i in have]
muh = items[-1]
muh["extra"] = [
    {"key": "nabiy", "title": "«Ey Payg'ambar» deb murojaat qilingan oyatlar", "q": "يَٰٓأَيُّهَا ٱلنَّبِىُّ",
     "verses": ref_groups(addr["nabiy"])},
    {"key": "rasul", "title": "«Ey Rasul» deb murojaat qilingan oyatlar", "q": "يَٰٓأَيُّهَا ٱلرَّسُولُ",
     "verses": ref_groups(addr["rasul"])},
]
muh["hadis"] = list(dict.fromkeys(muh["hadis"] + mh))

out = {
    "status": "Olim tekshiruvi kerak",
    "built": datetime.date.today().isoformat(),
    "selection": "Claude (manba emas), tools/build_anbiyo.py dagi mezon bo'yicha",
    "count_source": {
        "title": "Иймон", "site": "O'zbekiston musulmonlari idorasi (muslim.uz)", "date": "30.01.2019",
        "url": "https://muslim.uz/oz/e/post/28371-iymon", "retrieved": "2026-11-26",
    },
    "sources": {
        "ar": suras[1]["tanzil_notice"],
        "uz": "QuranEnc.com — uzbek_sadiq V1.0.1 (25.06.2025)",
        "ru": "QuranEnc.com — russian_rwwad V1.0.1 (29.03.2026)",
        "en": "QuranEnc.com — english_saheeh 1.1.2",
        "hadis": "HadeethEnc.com + sunnah.com (data/hadis.json)",
    },
    "items": items,
}
with open(f"{D}/anbiyo.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
print("\n".join(report))
print("order:", ", ".join(x["label"] for x in items))
print("Muhammad: nabiy", len(addr["nabiy"]), "rasul", len(addr["rasul"]), "hadis", len(muh["hadis"]), mh)
