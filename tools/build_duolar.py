"""Builds data/duolar.json for the "Duolar" (Quranic duas) screen.

This script holds ONLY references (sura:ayah ranges) and interface labels. It contains no religious text:
every Arabic verse and translation is copied verbatim from data/s/NNN.json
("ar" = Tanzil Uthmani 1.1; "uz"/"ru"/"en" and "*_fn" = QuranEnc). Whole verses only, nothing is cut.

Why our own selection (2026-11-25): no approved source gives a list of Quranic duas.
- muslim.uz: the article "Qur'ondagi duolar sharhi" (https://muslim.uz/oz/e/post/46372-qur-ondagi-duolar-sharhi,
  19.03.2026) has an empty body; no other list found.
- sunnah.com Hisn al-Muslim (https://sunnah.com/hisn): no chapter of duas from the Quran.
So the list below was chosen by Claude by the criteria below and every verse was confirmed by reading its own
Uzbek translation in data/s/. The selection is NOT a source: the app says so. Status: "Olim tekshiruvi kerak".

CRITERIA
Group "rabbana" (Robbana duolari):
  - at least one verse of the range contains the word رَبَّنَا (checked by machine, bare letters ربنا / وربنا);
  - the speakers are believers or angels asking Allah for something (forgiveness, mercy, guidance, help ...);
    a range runs while the same quoted supplication continues (e.g. 3:191-194);
  - left out: speakers who are disbelievers or people of Hell (e.g. 23:107, 35:37, 40:11), duas the verse itself
    criticises (2:200, 34:19, 38:16), verses where "Robbimiz" is not an address in a supplication (e.g. 6:23, 20:50),
    and duas of named prophets (they are in the next group).
Group "anbiyo" (Payg'ambarlar duolari):
  - a prophet named in the Quran calls on Allah and asks good for himself, his family or the believers,
    or the next verse says the call was answered (21:83-84, 21:87-88);
  - at least one verse of the range contains an address/call word (checked by machine: رب, ربي, ربنا, اللهم,
    or نادى / دعا);
  - the prophet's name must be visible in the Uzbek translation (or its footnote) of the verse "name_at", which lies
    in the range or at most 6 verses before it in the same passage (checked by machine; the passage was read by hand).
    NAME is only a search key in the Cyrillic of the translation, it is never shown.
  - left out: duas against people (10:88, 71:26), calls without a request (20:45), duas taught with "say"
    (23:29, 20:114), and passages where the name is further away (26:83-87, 37:100).

Usage: python -I -X utf8 tools/build_duolar.py data
"""
import json, sys, re, datetime

D = sys.argv[1]
LET = re.compile(r"[ء-يٱ]")

def bare(w):
    return "".join(c for c in w if LET.match(c)).replace("ٱ", "ا")

RABBANA = {"ربنا", "وربنا"}
CALL = {"رب", "ربي", "ربنا", "وربنا", "اللهم", "نادى", "فنادى", "دعا", "فدعا"}

# (sura, first ayah, last ayah)
RABBANA_LIST = [
    (2, 201, 201), (2, 250, 250), (2, 285, 286), (3, 8, 9), (3, 16, 16), (3, 53, 53), (3, 147, 147),
    (3, 191, 194), (4, 75, 75), (5, 83, 83), (7, 47, 47), (7, 126, 126), (10, 85, 86), (18, 10, 10),
    (23, 109, 109), (25, 65, 65), (25, 74, 74), (40, 7, 9), (59, 10, 10), (66, 8, 8),
]

# (label shown in the app (Latin, interface), NAME search key, name_at ayah, sura, first, last)
ANBIYO_LIST = [
    ("Odam", "Одам", 19, 7, 23, 23),
    ("Nuh", "Нуҳ", 45, 11, 47, 47),
    ("Nuh", "Нуҳ", 23, 23, 26, 26),
    ("Nuh", "Нуҳ", 9, 54, 10, 10),
    ("Nuh", "Нуҳ", 26, 71, 28, 28),
    ("Ibrohim", "Иброҳим", 126, 2, 126, 126),
    ("Ibrohim va Ismoil", "Исмоил", 127, 2, 127, 129),
    ("Ibrohim", "Иброҳим", 35, 14, 35, 41),
    ("Ibrohim", "Иброҳим", 4, 60, 4, 5),
    ("Lut", "Лут", 167, 26, 169, 169),
    ("Lut", "Лут", 28, 29, 30, 30),
    ("Yusuf", "Юсуф", 31, 12, 33, 33),
    ("Yusuf", "Юсуф", 99, 12, 101, 101),
    ("Muso", "Мусо", 19, 20, 25, 28),
    ("Muso", "Мусо", 150, 7, 151, 151),
    ("Muso", "Мусо", 155, 7, 155, 156),
    ("Muso", "Мусо", 15, 28, 16, 16),
    ("Muso", "Мусо", 20, 28, 21, 21),
    ("Muso", "Мусо", 20, 28, 24, 24),
    ("Ayyub", "Айюб", 83, 21, 83, 83),
    ("Yunus", "Юнус", 87, 21, 87, 87),
    ("Zakariyo", "Закариё", 38, 3, 38, 38),
    ("Zakariyo", "Закариё", 2, 19, 4, 6),
    ("Zakariyo", "Закариё", 89, 21, 89, 89),
    ("Sulaymon", "Сулаймон", 18, 27, 19, 19),
    ("Sulaymon", "Сулаймон", 34, 38, 35, 35),
    ("Iyso", "Ийсо", 114, 5, 114, 114),
]

_cache = {}
def sura(n):
    if n not in _cache:
        _cache[n] = json.load(open(f"{D}/s/{n:03}.json", encoding="utf-8"))
    return _cache[n]

def verses(s, a, b):
    d = sura(s)
    if not (1 <= a <= b <= len(d["ar"])):
        sys.exit(f"bad range {s}:{a}-{b}")
    out = []
    for i in range(a - 1, b):
        v = {"a": i + 1, "ar": d["ar"][i]}
        for k in ("uz", "uz_fn", "ru", "ru_fn", "en", "en_fn"):
            v[k] = d[k][i]
        out.append(v)
    return out

def words(v):
    return {bare(w) for w in v["ar"].split()}

def ref(s, a, b):
    return f"{s}:{a}" if a == b else f"{s}:{a}-{b}"

errors = []
rabbana = []
for s, a, b in RABBANA_LIST:
    vs = verses(s, a, b)
    if not any(words(v) & RABBANA for v in vs):
        errors.append(f"rabbana {ref(s, a, b)}: no رَبَّنَا")
    rabbana.append({"ref": ref(s, a, b), "s": s, "from": a, "to": b, "verses": vs})

anbiyo = []
for label, key, at, s, a, b in ANBIYO_LIST:
    vs = verses(s, a, b)
    if not any(words(v) & CALL for v in vs):
        errors.append(f"anbiyo {ref(s, a, b)}: no call word")
    if not (a - 6 <= at <= b):
        errors.append(f"anbiyo {ref(s, a, b)}: name_at {at} too far")
    d = sura(s)
    if key not in d["uz"][at - 1] and key not in (d["uz_fn"][at - 1] or ""):
        errors.append(f"anbiyo {ref(s, a, b)}: {label} not named at {s}:{at}")
    anbiyo.append({"ref": ref(s, a, b), "s": s, "from": a, "to": b, "prophet": label,
                   "name_at": f"{s}:{at}", "verses": vs})

if errors:
    sys.exit("\n".join(errors))

out = {
    "status": "Olim tekshiruvi kerak",
    "built": datetime.date.today().isoformat(),
    "selection": "Claude (manba emas), tools/build_duolar.py dagi mezon bo'yicha",
    "sources": {
        "ar": sura(1)["tanzil_notice"],
        "uz": "QuranEnc.com — uzbek_sadiq V1.0.1 (25.06.2025)",
        "ru": "QuranEnc.com — russian_rwwad V1.0.1 (29.03.2026)",
        "en": "QuranEnc.com — english_saheeh 1.1.2",
        "retrieved": "2026-11-25",
    },
    "groups": [
        {"key": "rabbana", "title": "Robbana duolari", "items": rabbana},
        {"key": "anbiyo", "title": "Payg'ambarlar duolari", "items": anbiyo},
    ],
}
with open(f"{D}/duolar.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
print(f"rabbana: {len(rabbana)} duo, {sum(len(x['verses']) for x in rabbana)} oyat; "
      f"anbiyo: {len(anbiyo)} duo, {sum(len(x['verses']) for x in anbiyo)} oyat")
