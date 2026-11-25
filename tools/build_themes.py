"""themes.css ni yig'adi: 4 iliq mavzu (Samarqand, Rishton, So'zana, Zardo'zi) va milliy naqshlar (SVG).
Ishga tushirish: python -I -X utf8 tools/build_themes.py themes.css
Diniy matn yo'q, faqat ranglar va bezak."""
import sys
from urllib.parse import quote

def uri(svg):
    return 'url("data:image/svg+xml,' + quote(svg, safe="=:/' ") + '")'

T = {
  # Samarqand: Registon koshinlari — feruza, lojuvard, oltin; girih yulduzi
  "samarqand": dict(name="Samarqand", bg="#f6f1e7", bg2="#efe7d6", panel="#fffcf6", ink="#2f2a22", mut="#7a7162",
      acc="#0f6b6b", acc2="#2c5a88", gold="#b58d38", ar="#173c3c", hl="#e4efea", btn="#ffffff"),
  # Rishton: sopol — kobalt va ishqor (feruza), qaymoq fon; gul (islimiy) rozetkasi
  "rishton": dict(name="Rishton", bg="#f6f4ee", bg2="#ece8dc", panel="#fffdf8", ink="#26303a", mut="#6c7480",
      acc="#1d4f91", acc2="#2a9895", gold="#bf984a", ar="#182c4e", hl="#e3ebf5", btn="#ffffff"),
  # So'zana: anor qizil, zaytun yashil, zig'ir fon; so'zana gul-doirasi
  "sozana": dict(name="So'zana", bg="#f5ecdd", bg2="#ecdfca", panel="#fffaf0", ink="#3a2a22", mut="#7c6a5c",
      acc="#9a2c25", acc2="#66702f", gold="#bd9045", ar="#46201a", hl="#f5e2d8", btn="#ffffff"),
  # Zardo'zi: Buxoro zardo'zi — to'q qizil baxmal va oltin ip
  "zardozi": dict(name="Zardo'zi", bg="#f7f0e6", bg2="#efe4d5", panel="#fffaf3", ink="#33242a", mut="#7a6870",
      acc="#6c1f36", acc2="#a87f26", gold="#b08628", ar="#3a1522", hl="#f3e3e3", btn="#ffffff"),
}

PET = [(5,0),(3.54,3.54),(0,5),(-3.54,3.54),(-5,0),(-3.54,-3.54),(0,-5),(3.54,-3.54)]

def star(cx, cy, s, fill, stroke, sw=1):
    h = s / 2
    return (f"<g transform='translate({cx} {cy})'><rect x='{-h}' y='{-h}' width='{s}' height='{s}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}'/>"
            f"<rect x='{-h}' y='{-h}' width='{s}' height='{s}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}' transform='rotate(45)'/></g>")

def rosette(cx, cy, k, petal, center, r=2.6):
    p = "".join(f"<circle cx='{cx+x*k:.2f}' cy='{cy+y*k:.2f}' r='{r*k:.2f}' fill='{petal}'/>" for x, y in PET)
    return p + f"<circle cx='{cx}' cy='{cy}' r='{3*k:.2f}' fill='{center}'/>"

def belt(t, c):
    S = "<svg xmlns='http://www.w3.org/2000/svg' "
    if t == "samarqand":
        return (S + "width='48' height='24'>" + f"<rect width='48' height='24' fill='{c['panel']}'/>"
                f"<g opacity='.6'><path d='M0 2H48M0 22H48' stroke='{c['gold']}' stroke-width='1.4'/>"
                + star(24, 12, 11, c['acc'], c['acc2'], .8) + f"<circle cx='24' cy='12' r='2.4' fill='{c['panel']}'/>"
                f"<path d='M0 8l4 4-4 4zM48 8l-4 4 4 4z' fill='{c['gold']}'/><circle cx='10' cy='12' r='1.3' fill='{c['acc2']}'/><circle cx='38' cy='12' r='1.3' fill='{c['acc2']}'/></g></svg>")
    if t == "rishton":
        return (S + "width='40' height='24'>" + f"<rect width='40' height='24' fill='{c['panel']}'/>"
                f"<path d='M0 2.5H40M0 21.5H40' stroke='{c['acc']}' stroke-width='1.2'/>"
                f"<circle cx='20' cy='12' r='7' fill='{c['acc']}'/>" + rosette(20, 12, .62, c['acc2'], c['panel'])
                + f"<ellipse cx='0' cy='12' rx='4.5' ry='2.2' fill='{c['acc2']}'/><ellipse cx='40' cy='12' rx='4.5' ry='2.2' fill='{c['acc2']}'/>"
                f"<circle cx='9' cy='12' r='1.2' fill='{c['gold']}'/><circle cx='31' cy='12' r='1.2' fill='{c['gold']}'/></svg>")
    if t == "sozana":
        return (S + "width='56' height='26'>" + f"<rect width='56' height='26' fill='{c['panel']}'/>"
                f"<path d='M0 2H56M0 24H56' stroke='{c['acc']}' stroke-width='1' stroke-opacity='.6'/>"
                f"<path d='M0 13C9 5 19 21 28 13S47 5 56 13' fill='none' stroke='{c['acc2']}' stroke-width='1.4'/>"
                f"<ellipse cx='11' cy='9.5' rx='3.6' ry='1.6' fill='{c['acc2']}' transform='rotate(-30 11 9.5)'/>"
                f"<ellipse cx='45' cy='16.5' rx='3.6' ry='1.6' fill='{c['acc2']}' transform='rotate(-30 45 16.5)'/>"
                + rosette(28, 13, 1, c['acc'], c['gold']) + f"<circle cx='28' cy='13' r='1.2' fill='{c['panel']}'/></svg>")
    if t == "zardozi":
        return (S + "width='36' height='24'>" + f"<rect width='36' height='24' fill='{c['acc']}'/>"
                f"<path d='M0 3H36M0 21H36' stroke='{c['gold']}' stroke-width='1.2'/>"
                f"<path d='M18 6L24 12L18 18L12 12Z' fill='none' stroke='{c['gold']}' stroke-width='1.3'/><circle cx='18' cy='12' r='1.8' fill='{c['gold']}'/>"
                f"<path d='M0 9.5Q4 12 0 14.5M36 9.5Q32 12 36 14.5' fill='none' stroke='{c['gold']}' stroke-width='1.1'/>"
                f"<circle cx='6.5' cy='12' r='1' fill='{c['gold']}'/><circle cx='29.5' cy='12' r='1' fill='{c['gold']}'/></svg>")

def bgpat(t, c):
    S = "<svg xmlns='http://www.w3.org/2000/svg' "
    if t == "samarqand":
        return S + "width='64' height='64'>" + star(32, 32, 20, "none", c['acc'], 1).replace("<g ", "<g stroke-opacity='.05' ") + "</svg>"
    if t == "rishton":
        return S + f"width='30' height='30'><circle cx='15' cy='15' r='1.5' fill='{c['acc']}' fill-opacity='.12'/></svg>"
    if t == "sozana":
        return (S + "width='90' height='90'><g fill='none' stroke='" + c['acc'] + "' stroke-opacity='.08'>"
                "<circle cx='45' cy='45' r='16'/><circle cx='45' cy='45' r='9'/>"
                + "".join(f"<circle cx='{45+x*4.4:.1f}' cy='{45+y*4.4:.1f}' r='5'/>" for x, y in PET) + "</g></svg>")
    if t == "zardozi":
        return S + f"width='32' height='32'><path d='M0 16L16 0L32 16L16 32Z' fill='none' stroke='{c['gold']}' stroke-opacity='.14'/></svg>"

def arch(c):
    # Peshtoq (ravoq) — me'moriy bezak, sura nomi atrofida
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 240 130' preserveAspectRatio='none'>"
            f"<path d='M8 130V64Q8 26 120 4Q232 26 232 64V130' fill='{c['hl']}' stroke='{c['acc']}' stroke-width='2'/>"
            f"<path d='M18 130V66Q18 34 120 15Q222 34 222 66V130' fill='none' stroke='{c['gold']}' stroke-width='1.2' stroke-dasharray='4 3'/></svg>")

def num(c):
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='-24 -24 48 48'>" + star(0, 0, 30, c['hl'], c['gold'], 1.5) + "</svg>")

BASE = r"""
/* ===== Iliq mavzular (milliy naqshlar). Diniy matn yo'q, faqat bezak. ===== */
[data-theme]{--bg:VAR(bg);--panel:VAR(panel);--ink:VAR(ink);--mut:VAR(mut);--gold:VAR(acc);--gold2:VAR(gold);--goldb:VAR(ar);--line:color-mix(in srgb,VAR(gold) 34%,transparent);--warn:color-mix(in srgb,VAR(gold) 14%,VAR(panel));--warnink:VAR(ink)}
[data-theme] body,html[data-theme]{background-color:var(--bg);color:var(--ink)}
[data-theme] body{background:VAR(pat),linear-gradient(180deg,var(--bg),VAR(bg2)) fixed}
[data-theme] a{color:var(--gold)}
[data-theme] header.top{background:color-mix(in srgb,var(--panel) 92%,transparent);border-bottom:1px solid var(--line)}
[data-theme] header.top h1{font-family:Lora,Georgia,serif;font-weight:600;color:var(--gold);letter-spacing:.3px}
[data-theme] header.top .back{color:var(--gold)}
[data-theme] .seg{border-color:var(--gold2)}
[data-theme] .seg button[aria-pressed=true],[data-theme] .ib[aria-pressed=true]{background:var(--gold);color:VAR(btn)}
[data-theme] .belt{height:24px;background:VAR(belt) center/auto 24px repeat-x;box-shadow:0 1px 0 var(--line),0 3px 8px rgb(80 60 20/.08)}
[data-theme] .card{background:var(--panel);border:1px solid var(--line);border-image:none;border-radius:18px;box-shadow:0 1px 2px rgb(80 60 20/.06),0 8px 24px rgb(80 60 20/.07);padding:20px 18px}
[data-theme] .card::after{content:"";position:absolute;inset:5px;border:1px solid color-mix(in srgb,var(--gold2) 22%,transparent);border-radius:14px;pointer-events:none}
[data-theme] .card h2,[data-theme] .tile b{font-family:Lora,Georgia,serif;font-weight:600}
[data-theme] .card h2{color:var(--gold)}
[data-theme] .card.sura{padding-top:40px;overflow:hidden}
[data-theme] .card.sura::before{height:24px;background:VAR(belt) center/auto 24px repeat-x;border-radius:18px 18px 0 0}
[data-theme] .note{background:var(--warn);color:var(--ink);border-color:var(--line)}
[data-theme] .search,[data-theme] select{background:var(--panel);border-color:var(--line)}
[data-theme] .num{color:var(--gold);background-image:VAR(num)}
[data-theme] .sar,[data-theme] .letters .l,[data-theme] .forms .l{color:var(--goldb)}
[data-theme] .ar,[data-theme] .stitle h2{color:var(--goldb);text-shadow:none;background:none;-webkit-background-clip:border-box;background-clip:border-box;filter:none}
[data-theme] .stitle{margin:0 auto 6px;max-width:300px;padding:34px 18px 10px;background:VAR(arch) center/100% 100% no-repeat}
[data-theme] .stitle h2{color:var(--gold)}
[data-theme] .stitle .sub,[data-theme] .datebar{font-family:Lora,Georgia,serif;font-style:italic}
[data-theme] .datebar b{color:var(--gold)}
[data-theme] .ayah.on,[data-theme] table.tt tr.today td{background:VAR(hl)}
[data-theme] .ayah.on,[data-theme] .zk.on{box-shadow:inset 3px 0 0 var(--gold)}
[data-theme] table.tt tr.today td{color:var(--gold)}
[data-theme] .ib{color:var(--gold);border-color:var(--line);background:var(--panel)}
[data-theme] .player{background:var(--panel);border-top:1px solid var(--gold2);box-shadow:0 -6px 18px rgb(80 60 20/.08)}
[data-theme] .player .t b{color:var(--gold)}
[data-theme] .btn{background:var(--gold);color:VAR(btn);box-shadow:inset 0 -2px 0 rgb(0 0 0/.15)}
[data-theme] .btn2{color:var(--gold);border-color:var(--gold2);background:var(--panel)}
[data-theme] nav.bottom{background:var(--panel);border-top:1px solid var(--line);box-shadow:0 -6px 18px rgb(80 60 20/.06)}
[data-theme] nav.bottom button{color:var(--mut)}
[data-theme] nav.bottom button[aria-current=page]{color:var(--gold);box-shadow:inset 0 3px 0 var(--gold)}
[data-theme] .tile,[data-theme] .letters button{background:var(--panel);border-color:var(--line);box-shadow:0 4px 14px rgb(80 60 20/.06)}
[data-theme] .tile svg{color:var(--gold)}
[data-theme] .counter{background:radial-gradient(circle at 50% 40%,var(--panel),VAR(hl) 75%);box-shadow:0 0 0 3px var(--gold2),0 0 0 9px var(--panel),0 0 0 10px var(--line),0 10px 30px rgb(80 60 20/.12);color:var(--gold)}
[data-theme] table.tt th{background:var(--panel);color:var(--gold)}
[data-theme] .times b,[data-theme] .zk-n,[data-theme] .zk summary{color:var(--gold)}
[data-theme] .times div{background:var(--panel)}
[data-theme] .compass{background:radial-gradient(circle,var(--panel),VAR(hl) 75%);border-color:var(--gold2)}
[data-theme] .compass .needle{background:linear-gradient(var(--gold),var(--gold2))}
[data-theme] .farq-row>div,[data-theme] .forms div{background:var(--panel)}
"""

def main(out):
    css = []
    for key, c in T.items():
        block = BASE.replace("[data-theme]", f"[data-theme={key}]")
        if key != "samarqand":  # comment only once
            block = block.split("\n", 2)[2]
        rep = dict(c, belt=uri(belt(key, c)), pat=uri(bgpat(key, c)) + " center/auto repeat", num=uri(num(c)), arch=uri(arch(c)))
        for k, v in rep.items():
            block = block.replace(f"VAR({k})", v)
        css.append(block.strip())
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(css) + "\n")

main(sys.argv[1])
