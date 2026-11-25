"""Adds Uzbek sura names to data/suras.json (field "uz"). Names are copied verbatim (Cyrillic, as in the source).
Source: QuranEnc.com Uzbek interface, sura list on https://quranenc.com/uz/browse/uzbek_sadiq/1
(muslim.uz has no sura-name list: its Quran page embeds tanzil.net. api.quran.com was unreachable on 2026-11-25.)
Also writes data/sura-names-uz.json with source, url, date and the raw list.
Run AFTER tools/build_data.py (which rewrites suras.json without "uz"):
    python -I -X utf8 tools/build_sura_names.py data
"""
import json, sys, re, html, urllib.request, datetime
URL = "https://quranenc.com/uz/browse/uzbek_sadiq/1"
out = sys.argv[1]
t = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "kitab-data-build"}), timeout=60).read().decode("utf-8")
pairs = re.findall(r'<span class="surah_number[^"]*">\s*(\d+)\s*</span>.*?<h2 class="surah_name[^"]*">\s*([^<]+?)\s*</h2>', t, re.S)
names = {}
for n, name in pairs:
    names.setdefault(int(n), html.unescape(name).strip())
assert sorted(names) == list(range(1, 115)), f"expected 114 names, got {len(names)}"
suras = json.load(open(f"{out}/suras.json", encoding="utf-8"))
for s in suras:
    s["uz"] = names[s["n"]]
json.dump(suras, open(f"{out}/suras.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
json.dump({"source": "QuranEnc.com (o'zbekcha interfeys, sura ro'yxati)", "url": URL,
           "retrieved": datetime.date.today().isoformat(), "status": "Olim tekshiruvi kerak",
           "note": "Nomlar manbadagidek kirill yozuvida, o'zgartirilmagan. Ikkinchi manba bilan solishtirilmagan.",
           "names": [names[i] for i in range(1, 115)]},
          open(f"{out}/sura-names-uz.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(names), [names[i] for i in (1, 2, 3, 36, 112, 114)])
