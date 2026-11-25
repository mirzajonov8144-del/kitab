"""Builds data/tajvid.json for the Tajvid screen.
- Rule explanations (Uzbek) are written by Claude on the owner's decision (2026-11-25): NOT a source,
  shown with a "Manba emas" label until the Muslim Board (Idora) reviews them.
- Every Quran example is cut character for character from data/s/NNN.json ("ar" = Tanzil Uthmani 1.1),
  never typed. KEY is a bare-letter search key only and is never shown.
- Each example is also checked by machine against its rule (e.g. the letter after nun sakin / tanwin
  belongs to the rule's letter group). A failed check stops the build.
Usage: python -I -X utf8 tools/build_tajvid.py data
"""
import json, sys, re, datetime

D = sys.argv[1]
VOW = "َُِ"            # fatha, damma, kasra
TANWIN = "ًٌٍ"         # fathatan, dammatan, kasratan
SHADDA, SUKUN, MADDA = "ّ", "ْ", "ٓ"
MARK = re.compile(r"[ً-ٰٟۖ-ۭـ]")
LET = re.compile(r"[ء-يٱ]")
FOLD = {"ى": "ي", "ة": "ه", "ٱ": "ا"}

def units(t):
    """[(letter, marks)] for the base letters of t (spaces/punctuation dropped)."""
    out = []
    for c in t:
        if LET.match(c): out.append([c, ""])
        elif MARK.match(c) and out: out[-1][1] += c
    return out

def cut(text, key):
    L = [(i, FOLD.get(c, c)) for i, c in enumerate(text) if LET.match(c)]
    k = "".join(FOLD.get(c, c) for c in key if LET.match(c))
    s = "".join(c for _, c in L); p = s.find(k)
    if p < 0: return None
    a, b = L[p][0], L[p + len(k) - 1][0] + 1
    while b < len(text) and MARK.match(text[b]): b += 1
    return text[a:b]

def next_after(u, i):
    """Next pronounced letter after unit i (skips a bare alif / alif maqsura carrying the tanwin)."""
    j = i + 1
    while j < len(u) and u[j][0] in "اى" and not any(m in u[j][1] for m in VOW + TANWIN + SHADDA):
        j += 1
    return u[j][0] if j < len(u) else None

def check(kind, arg, span):
    u = units(span)
    if kind == "nun":       # nun sakin or tanwin followed by a letter of arg
        return any(((c == "ن" and not any(m in mk for m in VOW + TANWIN + SHADDA)) or any(t in mk for t in TANWIN))
                   and (next_after(u, i) or "") in arg for i, (c, mk) in enumerate(u))
    if kind == "mim":       # mim sakin followed by a letter of arg
        return any(c == "م" and not any(m in mk for m in VOW + TANWIN + SHADDA) and (next_after(u, i) or "") in arg
                   for i, (c, mk) in enumerate(u))
    if kind == "shadda":    # nun or mim with shadda
        return any(c in "نم" and SHADDA in mk for c, mk in u)
    if kind == "qalqala":   # qalqala letter with sukun, or last letter (stopping on it)
        return any(c in arg and (SUKUN in mk or i == len(u) - 1) for i, (c, mk) in enumerate(u))
    if kind == "madda":     # maddah sign present
        return MADDA in span
    al = next((i + 1 for i in range(len(u) - 2) if FOLD.get(u[i][0], u[i][0]) == "ا" and u[i + 1][0] == "ل"), None)
    if kind == "shams":     # al- + letter with shadda, lam without sukun
        return al is not None and SUKUN not in u[al][1] and SHADDA in u[al + 1][1] and u[al + 1][0] in arg
    if kind == "qamar":     # al- with lam sukun
        return al is not None and SUKUN in u[al][1] and u[al + 1][0] in arg
    if kind == "allah":     # the word Allah, previous vowel given in arg
        i = next((i for i in range(len(u) - 2) if u[i + 1][0] == "ل" and u[i + 2][0] == "ل" and u[i + 2][1].find(SHADDA) >= 0 and FOLD.get(u[i][0], u[i][0]) == "ا"), None)
        return i is not None and i > 0 and arg in u[i - 1][1]
    if kind == "none":
        return True
    raise ValueError(kind)

HALQ = "ءهعحغخأإ"           # ء ه ع ح غ خ (+ hamza seats)
YANMU = "ينمو"                                   # ي ن م و
LR = "لر"                                                  # ل ر
IKHFA = "تثجدذزسشصضطظفقك"
QALQ = "قطبجد"
SHAMS = "تثدذرزسشصضطظلن"
QAMAR = "ابغحجكوخفعقيمه"
NOT_BM = "".join(c for c in "ءاتثجحخدذرزسشصضطظعغفقكلنهويأإ")

# examples: (sura, ayah, key, check kind, check arg)
LESSONS = [
 {"id": "nun", "title": "Nun sokin va tanvin",
  "intro": "Sukunli nun (نْ) yoki tanvin (ـً ـٍ ـٌ) dan keyin qaysi harf kelishiga qarab, ular 4 xil o'qiladi.",
  "rules": [
   {"name": "Izhor (aniq o'qish)", "letters": "ء ه ع ح غ خ",
    "text": "Keyin bo'g'iz harflari kelsa, nun yoki tanvin g'unnasiz, aniq o'qiladi.",
    "ex": [(1, 7, "أنعمت", "nun", HALQ), (2, 62, "من ءامن", "nun", HALQ)]},
   {"name": "Idg'om (qo'shib o'qish)", "letters": "ي ن م و  ·  ل ر",
    "text": "Keyin ي ن م و kelsa, nun keyingi harfga qo'shilib, g'unna bilan o'qiladi. Keyin ل yoki ر kelsa, g'unnasiz qo'shiladi. Nun va keyingi harf bir so'z ichida bo'lsa, idg'om qilinmaydi.",
    "ex": [(2, 8, "من يقول", "nun", YANMU), (2, 5, "من ربهم", "nun", LR), (2, 2, "هدى للمتقين", "nun", LR)]},
   {"name": "Iqlob (aylantirish)", "letters": "ب",
    "text": "Keyin ب kelsa, nun yoki tanvin م ga aylanib, g'unna bilan o'qiladi. Mushafda bu joyga kichik م belgisi qo'yiladi.",
    "ex": [(2, 27, "من بعد", "nun", "ب"), (2, 33, "أنبئهم", "nun", "ب")]},
   {"name": "Ixfo (yashirib o'qish)", "letters": "ت ث ج د ذ ز س ش ص ض ط ظ ف ق ك",
    "text": "Qolgan 15 harfdan biri kelsa, nun to'liq aytilmaydi: tovush burundan, g'unna bilan chiqadi.",
    "ex": [(2, 4, "من قبلك", "nun", IKHFA), (2, 23, "كنتم", "nun", IKHFA)]},
  ]},
 {"id": "mim", "title": "Mim sokin",
  "intro": "Sukunli mim (مْ) dan keyin keladigan harfga qarab 3 xil o'qiladi.",
  "rules": [
   {"name": "Ixfo shafaviy", "letters": "ب",
    "text": "Keyin ب kelsa, mim lablar yengil tegib, g'unna bilan o'qiladi.",
    "ex": [(105, 4, "ترميهم بحجارة", "mim", "ب")]},
   {"name": "Idg'om misliy", "letters": "م",
    "text": "Keyin yana م kelsa, ikki mim qo'shilib, g'unna bilan o'qiladi.",
    "ex": [(2, 10, "قلوبهم مرض", "mim", "م")]},
   {"name": "Izhor shafaviy", "letters": "",
    "text": "ب va م dan boshqa harflar oldida mim aniq o'qiladi. Ayniqsa و va ف oldida mimni yashirib yubormaslik kerak.",
    "ex": [(1, 7, "عليهم ولا", "mim", NOT_BM)]},
  ]},
 {"id": "gunna", "title": "G'unna (tashdidli nun va mim)",
  "intro": "Tashdidli nun (نّ) va tashdidli mim (مّ) har doim to'liq g'unna bilan, taxminan 2 harakat cho'zib o'qiladi.",
  "rules": [
   {"name": "Tashdidli nun va mim", "letters": "نّ  مّ", "text": "",
    "ex": [(2, 20, "إن الله", "shadda", ""), (114, 1, "الناس", "shadda", "")]},
  ]},
 {"id": "qalqala", "title": "Qalqala",
  "intro": "ق ط ب ج د harflari sukunli bo'lsa, tovush biroz «sakrab» chiqadi. Shu harfda to'xtalganda qalqala kuchliroq bo'ladi.",
  "rules": [
   {"name": "So'z ichida", "letters": "ق ط ب ج د", "text": "",
    "ex": [(2, 27, "ويقطعون", "qalqala", QALQ)]},
   {"name": "To'xtalganda (vaqfda)", "letters": "ق ط ب ج د", "text": "",
    "ex": [(112, 1, "أحد", "qalqala", QALQ), (113, 1, "الفلق", "qalqala", QALQ)]},
  ]},
 {"id": "madd", "title": "Madd (cho'zish)",
  "intro": "Madd harflari: harakatsiz ا (oldi fathali), و (oldi zammali), ي (oldi kasrali). Ular qancha cho'zilishi keyingi harfga bog'liq. «Harakat» — cho'zish o'lchovi.",
  "rules": [
   {"name": "Madd tabiiy", "letters": "ا و ي", "text": "Keyin hamza yoki sukun kelmasa — 2 harakat.",
    "ex": [(1, 4, "ملك", "none", "")]},
   {"name": "Madd muttasil (vojib)", "letters": "", "text": "Madd harfi va hamza bir so'zda — 4 yoki 5 harakat.",
    "ex": [(2, 19, "السماء", "madda", "")]},
   {"name": "Madd munfasil (joiz)", "letters": "", "text": "Madd harfi so'z oxirida, hamza keyingi so'z boshida — 4 yoki 5 harakat (Hafs rivoyati, Shotibiy yo'li).",
    "ex": [(2, 4, "بما أنزل", "madda", "")]},
   {"name": "Madd lozim", "letters": "", "text": "Madd harfidan keyin doimiy sukun yoki tashdid kelsa — 6 harakat. Ba'zi suralar boshidagi harflarda ham bor.",
    "ex": [(1, 7, "الضالين", "madda", ""), (2, 1, "الم", "madda", "")]},
   {"name": "Madd oriz (to'xtalganda)", "letters": "", "text": "Oyat oxirida to'xtalganda oxirgi harf sukunli bo'lib qoladi — 2, 4 yoki 6 harakat.",
    "ex": [(1, 2, "العلمين", "none", ""), (1, 5, "نستعين", "none", "")]},
  ]},
 {"id": "lam", "title": "«Al» dagi lom",
  "intro": "So'z boshidagi «al» (ال) ning lomi keyingi harfga qarab 2 xil o'qiladi.",
  "rules": [
   {"name": "Qamariy lom (o'qiladi)", "letters": "ا ب غ ح ج ك و خ ف ع ق ي م ه",
    "text": "Lom sukun bilan aniq o'qiladi.", "ex": [(91, 2, "والقمر", "qamar", QAMAR)]},
   {"name": "Shamsiy lom (o'qilmaydi)", "letters": "ت ث د ذ ر ز س ش ص ض ط ظ ل ن",
    "text": "Lom o'qilmaydi, keyingi harf tashdid bilan o'qiladi.", "ex": [(91, 1, "والشمس", "shams", SHAMS)]},
  ]},
 {"id": "allah", "title": "«Alloh» so'zidagi lom",
  "intro": "«Alloh» so'zining lomi oldingi harfning harakatiga qarab o'qiladi.",
  "rules": [
   {"name": "Qalin (tafxim)", "letters": "", "text": "Oldingi harf fatha yoki zammali bo'lsa, lom qalin o'qiladi.",
    "ex": [(112, 1, "هو الله", "allah", "َ")]},
   {"name": "Ingichka (tarqiq)", "letters": "", "text": "Oldingi harf kasrali bo'lsa, lom ingichka o'qiladi.",
    "ex": [(1, 1, "بسم الله", "allah", "ِ")]},
  ]},
]

cache = {}
def ayah(s, a):
    if s not in cache: cache[s] = json.load(open(f"{D}/s/{s:03d}.json", encoding="utf-8"))["ar"]
    return cache[s][a - 1]

bad = []
for L in LESSONS:
    for r in L["rules"]:
        exs = []
        for s, a, key, kind, arg in r["ex"]:
            span = cut(ayah(s, a), key)
            if not span: bad.append((s, a, key, "topilmadi")); continue
            if not check(kind, arg, span): bad.append((s, a, key, kind, span)); continue
            exs.append({"ref": f"{s}:{a}", "ar": span, "check": kind})
        r["ex"] = exs
if bad:
    print("XATO:", *bad, sep="\n  "); sys.exit(1)

json.dump({"status": "Manba emas — Idora tekshiruvi kerak",
           "explanations": "Qoidalar izohini Claude (sun'iy intellekt) yozgan, egasi qarori bilan (2026-11-25). Idora tekshiradi.",
           "examples_source": "Misollar ilovadagi Tanzil matnidan (Uthmani 1.1) harfma-harf kesib olingan. Qoidaga mosligi dastur bilan tekshirilgan (madd tabiiy va madd oriz misollari bundan mustasno).",
           "riwaya": "Hafs an Osim",
           "built": datetime.date.today().isoformat(), "lessons": LESSONS},
          open(f"{D}/tajvid.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", sum(len(r["ex"]) for L in LESSONS for r in L["rules"]), "misol")
