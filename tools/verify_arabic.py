import json, sys, difflib
from collections import Counter
raw, tz = sys.argv[1], sys.argv[2]
tan = {}
for line in open(tz, encoding="utf-8"):
    p = line.rstrip("\n").split("|")
    if len(p) == 3 and p[0].isdigit(): tan[(int(p[0]), int(p[1]))] = p[2]
B = tan[(1,1)] + " "
enc = {}
for s in range(1, 115):
    for r in json.load(open(f"{raw}/uzbek_sadiq_{s:03d}.json"))["result"]:
        enc[(int(r["sura"]), int(r["aya"]))] = r["arabic_text"]
# encoding-convention tokens (same mark, different code point)
T = {"ْ":"<SUK>","۟":"<ZERO>","ى":"<YA>","ي":"<YA>","ـ":"",
     "ً":"<FTN>","ٌ":"<DTN>","ٍ":"<KTN>"," ":" "}
E = {"ۡ":"<SUK>","ْ":"<ZERO>","ي":"<YA>","ى":"<YA>",
     "ٗ":"<FTN>","ٞ":"<DTN>","ٖ":"<KTN>","ً":"<FTN>","ٌ":"<DTN>","ٍ":"<KTN>"," ":" "}
def n(t, M):
    t = t.replace("أٓ", "َٔا") if M is E else t
    return "".join(M.get(ch, ch) for ch in t).replace("  "," ").strip()
res = Counter(); bad = []
for k in sorted(tan):
    a = tan[k]
    if k[1] == 1 and k[0] not in (1, 9) and a.startswith(B): a = a[len(B):]
    x, y = n(a, T), n(enc[k], E)
    if x != y:
        bad.append(k)
        for op,i1,i2,j1,j2 in difflib.SequenceMatcher(None,x,y,autojunk=False).get_opcodes():
            if op!="equal": res[(op, x[i1:i2], y[j1:j2])]+=1
print("mismatch ayahs:", len(bad))
for k,v in res.most_common(30): print(v, [(o, " ".join(f"{ord(c):04X}" if len(c)==1 else c for c in [*s]) ) for o,s in [("T",k[1]),("E",k[2])]])
print(bad[:20])
print("=== level: letters+harakat, waqf marks & spaces ignored ===")
W = set("ۖۗۘۙۚۛۜ۞۩ ـ")
res2=Counter(); bad2=[]
for k in sorted(tan):
    a = tan[k]
    if k[1] == 1 and k[0] not in (1, 9) and a.startswith(B): a = a[len(B):]
    x = "".join(c for c in n(a,T) if c not in W); y = "".join(c for c in n(enc[k],E) if c not in W)
    if x != y:
        bad2.append(k)
        for op,i1,i2,j1,j2 in difflib.SequenceMatcher(None,x,y,autojunk=False).get_opcodes():
            if op!="equal": res2[(x[i1:i2], y[j1:j2])]+=1
print("mismatch ayahs:", len(bad2))
for k,v in res2.most_common(20): print(v, [" ".join(f"{ord(c):04X}" for c in s) for s in k])
json.dump({"letters_mismatch":[f"{a}:{b}" for a,b in bad2],"pause_mismatch":[f"{a}:{b}" for a,b in bad]}, open("verify_lists.json","w"))
print([f"{a}:{b}" for a,b in bad2][:40])
