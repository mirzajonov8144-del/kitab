"""Builds app data from downloaded source files. Text is copied verbatim; nothing is edited.
Usage: python3 -I tools/build_data.py <raw_quranenc_dir> <tanzil_uthmani.txt> <chapters.json> <out_dir>
"""
import json, sys, os
raw, tz, ch, out = sys.argv[1:5]
tan, notice = {}, []
for line in open(tz, encoding="utf-8"):
    p = line.rstrip("\n").split("|")
    if len(p) == 3 and p[0].isdigit(): tan[(int(p[0]), int(p[1]))] = p[2]
    elif line.startswith("#"): notice.append(line.rstrip("\n"))
open(f"{out}/TANZIL-LICENSE.txt", "w", encoding="utf-8").write("\n".join(notice) + "\n")
chap = json.load(open(ch))["chapters"]
keys = {"uz": "uzbek_sadiq", "ru": "russian_rwwad", "en": "english_saheeh"}
suras = []
for c in chap:
    s = c["id"]
    d = {"n": s, "ar": [], "tanzil_notice": "Tanzil Quran Text (Uthmani, Version 1.1), Copyright (C) 2007-2026 Tanzil Project, CC BY 3.0, changing it is not allowed - https://tanzil.net"}
    n = c["verses_count"]
    d["ar"] = [tan[(s, a)] for a in range(1, n + 1)]
    for lang, k in keys.items():
        rows = json.load(open(f"{raw}/{k}_{s:03d}.json"))["result"]
        assert [int(r["aya"]) for r in rows] == list(range(1, n + 1)), (k, s)
        d[lang] = [r["translation"] for r in rows]
        d[lang + "_fn"] = [r.get("footnotes") or "" for r in rows]
    json.dump(d, open(f"{out}/s/{s:03d}.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    suras.append({"n": s, "ar": c["name_arabic"], "lat": c["name_simple"], "en": c["translated_name"]["name"],
                  "v": n, "place": c["revelation_place"], "bism": c["bismillah_pre"]})
json.dump(suras, open(f"{out}/suras.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("ok", len(suras), sum(x["v"] for x in suras))
