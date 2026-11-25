"use strict";
/* Kitab — o'quv ilovasi (sinov versiyasi).
   Diniy matnlar faqat data/ papkasidagi manba fayllardan olinadi (Tanzil, QuranEnc, sunnah.com, HadeethEnc).
   Bu faylda hech qanday oyat, tarjima, duo yoki hadis matni yozilmagan. */

const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const store = {
  get(k, d) { try { const v = localStorage.getItem("kitab." + k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem("kitab." + k, JSON.stringify(v)); } catch {} }
};
const st = {
  script: store.get("script", "lat"),       // UI yozuvi: lat / kir
  tr: store.get("tr", "uz"),                 // tarjima tili: uz / ru / en / none
  fn: store.get("fn", false),                // izohlarni ko'rsatish
  reciter: store.get("reciter", 7),
  style: store.get("style", "k6"),
  arsize: store.get("arsize", 28),
  hijriAdj: store.get("hijriAdj", 0),
  region: store.get("region", "toshkent"),
  autoNext: store.get("autoNext", false),
  last: store.get("last", null)
};
const save = k => store.set(k, st[k]);

/* ---------- Lotin -> Kirill (faqat interfeys matni uchun; diniy matnga ishlatilmaydi) ---------- */
function toCyr(s) {
  const pairs = [["O'", "Ў"], ["o'", "ў"], ["G'", "Ғ"], ["g'", "ғ"], ["Sh", "Ш"], ["SH", "Ш"], ["sh", "ш"], ["Ch", "Ч"], ["CH", "Ч"], ["ch", "ч"],
    ["Yo'", "Йў"], ["yo'", "йў"], ["Yo", "Ё"], ["yo", "ё"], ["Yu", "Ю"], ["yu", "ю"], ["Ya", "Я"], ["ya", "я"], ["Ye", "Е"], ["ye", "е"], ["ʼ", "ъ"]];
  const one = { a: "а", b: "б", d: "д", e: "е", f: "ф", g: "г", h: "ҳ", i: "и", j: "ж", k: "к", l: "л", m: "м", n: "н", o: "о", p: "п", q: "қ", r: "р", s: "с", t: "т", u: "у", v: "в", x: "х", y: "й", z: "з", c: "с" };
  return s.split(/(<[^>]*>|\{[^}]*\})/).map(part => {
    if (part.startsWith("<") || part.startsWith("{")) return part;
    let out = "", i = 0;
    while (i < part.length) {
      const prev = i ? part[i - 1] : " ";
      const start = !/[A-Za-zʼ'ЀЁЂ-ӿ]/.test(prev);
      const p = pairs.find(([l]) => part.startsWith(l, i));
      if (p) { out += p[1]; i += p[0].length; continue; }
      const c = part[i], lc = c.toLowerCase();
      if (lc === "e" && start) out += c === "E" ? "Э" : "э";
      else if (one[lc]) out += c === lc ? one[lc] : one[lc].toUpperCase();
      else out += c;
      i++;
    }
    return out;
  }).join("");
}
const T = s => (st.script === "kir" ? toCyr(s) : s).replace(/[{}]/g, "");

/* ---------- Ma'lumotlar ---------- */
const RECITERS = [
  { id: 7, name: "Mishari Rashid al-Afasy", dir: "Alafasy/mp3/" },
  { id: 2, name: "AbdulBaset AbdulSamad (Murattal)", dir: "AbdulBaset/Murattal/mp3/" },
  { id: 1, name: "AbdulBaset AbdulSamad (Mujawwad)", dir: "AbdulBaset/Mujawwad/mp3/" },
  { id: 9, name: "Mohamed Siddiq al-Minshawi (Murattal)", dir: "Minshawi/Murattal/mp3/" },
  { id: 8, name: "Mohamed Siddiq al-Minshawi (Mujawwad)", dir: "Minshawi/Mujawwad/mp3/" },
  { id: 3, name: "Abdur-Rahman as-Sudais", dir: "Sudais/mp3/" },
  { id: 10, name: "Sa'ud ash-Shuraym", dir: "Shuraym/mp3/" },
  { id: 4, name: "Abu Bakr al-Shatri", dir: "Shatri/mp3/" },
  { id: 5, name: "Hani ar-Rifai", dir: "Rifai/mp3/" }
];
const AUDIO_BASE = "https://verses.quran.com/";
const REGIONS = {
  toshkent: ["Toshkent", 41.2995, 69.2401], andijon: ["Andijon", 40.7821, 72.3442], namangan: ["Namangan", 40.9983, 71.6726],
  fargona: ["Farg'ona", 40.3864, 71.7864], samarqand: ["Samarqand", 39.6542, 66.9597], buxoro: ["Buxoro", 39.7747, 64.4286],
  navoiy: ["Navoiy", 40.1039, 65.3739], qarshi: ["Qarshi", 38.8606, 65.7891], termiz: ["Termiz", 37.2242, 67.2783],
  jizzax: ["Jizzax", 40.1158, 67.8422], guliston: ["Guliston", 40.4897, 68.7842], urganch: ["Urganch", 41.5506, 60.6317],
  nukus: ["Nukus", 42.4531, 59.6103]
};
/* Hisob: Fajr/Isha 15°, Asr — Hanafiy. Tuzatishlar (tune: Imsak,Fajr,Quyosh,Peshin,Asr,Shom,Sunset,Xufton,Midnight)
   Idora Fatvo markazining @fatvouz_taqvim_bot jadvaliga moslangan (egasi qarori, 2026-11-25):
   Namangan viloyatidagi bir nuqta, 25.11–01.12, 7 kun × 6 vaqt — formula 42/42 mos. Aladhan'ning Asr hisobi
   ~0,3 daqiqa kechroq, shuning uchun Asr ba'zi kunlari botdan 1 daqiqa kech chiqishi mumkin.
   Avvalgi sozlama (0,-3,-4,5,-1,3,0,-1,0) muslim.uz'dagi Toshkent vaqtiga mos edi; bot undan 1 daqiqa farq qiladi. Taxminiy. */
const PT_QS = "method=99&methodSettings=15,null,15&school=1&tune=0,-3,-5,5,0,4,0,0,0";
const MAKKAH = [21.4225, 39.8262];
/* Rasmiy jonli efir kanallari (Saudiya Radio va Televideniye idorasi, SBA). 2026-11-25 tekshirildi:
   YouTube tasdiq belgisi bor, kanal tavsifida SBA'ga tegishli deyilgan, jonli efir ishlaydi va embed ruxsat etilgan.
   sba.sa saytidagi havola hali tekshirilmadi (sayt ochilmadi).
   `video` — kanalning hozirgi jonli efiri (2026-11-25). Makka kanali uchun `live_stream?channel=` embed'i
   "Video mavjud emas" ko'rsatdi, shuning uchun aniq video ID birinchi ishlatiladi. Efir qayta boshlansa ID
   o'zgaradi: unda youtube.com/channel/<channel>/live dan yangi ID'ni olib yozing. */
const LIVE = [
  { key: "makka", title: "Makka — Masjidul Harom", channel: "UCos52azQNBgW63_9uDJoPDA", video: "IsJTAdC3-Jw", name: "قناة القرآن الكريم", handle: "@SaudiQuranTv" },
  { key: "madina", title: "Madina — Masjidun Nabaviy", channel: "UCROKYPep-UuODNwyipe6JMw", video: "DLnqQHiDbaI", name: "قناة السنة النبوية", handle: "@SaudiSunnahTv" }
];
const HMONTHS = ["Muharram", "Safar", "Rabiul avval", "Rabiul oxir", "Jumodul avval", "Jumodul oxir", "Rajab", "Sha'bon", "Ramazon", "Shavvol", "Zulqa'da", "Zulhijja"];
const GMONTHS = ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"];
const WDAYS = ["Yakshanba", "Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"];
const LETTERS = [
  ["ا", "Alif", 0], ["ب", "Bo", 1], ["ت", "To", 1], ["ث", "So", 1], ["ج", "Jim", 1], ["ح", "Ho", 1], ["خ", "Xo", 1], ["د", "Dol", 0],
  ["ذ", "Zol", 0], ["ر", "Ro", 0], ["ز", "Zay", 0], ["س", "Sin", 1], ["ش", "Shin", 1], ["ص", "Sod", 1], ["ض", "Dod", 1], ["ط", "Toʼ", 1],
  ["ظ", "Zoʼ", 1], ["ع", "Ayn", 1], ["غ", "G'ayn", 1], ["ف", "Fa", 1], ["ق", "Qof", 1], ["ك", "Kof", 1], ["ل", "Lom", 1], ["م", "Mim", 1],
  ["ن", "Nun", 1], ["ه", "Ha", 1], ["و", "Vov", 0], ["ي", "Yo", 1]
];

let SURAS = [];
const suraCache = new Map();
async function getJSON(url) { const r = await fetch(url); if (!r.ok) throw new Error(r.status); return r.json(); }
/* Sura nomi: o'zbekcha (QuranEnc, kirillda, T() dan o'tmaydi), bo'lmasa transliteratsiya. */
const sname = s => s.uz || s.lat;
let zikrCache = null;
async function loadZikr() { return zikrCache ||= await getJSON("data/zikr.json"); }
async function loadSura(n) {
  if (!suraCache.has(n)) suraCache.set(n, await getJSON(`data/s/${String(n).padStart(3, "0")}.json`));
  return suraCache.get(n);
}

/* ---------- Sanalar ---------- */
function hijriParts(d) {
  const dd = new Date(d.getTime() + st.hijriAdj * 864e5);
  const f = new Intl.DateTimeFormat("en-u-ca-islamic-umalqura-nu-latn", { day: "numeric", month: "numeric", year: "numeric" });
  const p = Object.fromEntries(f.formatToParts(dd).map(x => [x.type, x.value]));
  return { d: +p.day, m: +p.month, y: parseInt(p.year) };
}
function dateLine(d = new Date()) {
  const h = hijriParts(d);
  return { greg: `${WDAYS[d.getDay()]}, ${d.getDate()} ${GMONTHS[d.getMonth()]} ${d.getFullYear()}`, hijri: `${h.d} ${HMONTHS[h.m - 1]} ${h.y} h.` };
}

/* ---------- Audio ---------- */
const audio = new Audio();
audio.preload = "auto";
const pl = { sura: 0, ayah: 0, total: 0, mode: "one", playing: false };
const pad3 = n => String(n).padStart(3, "0");
const reciter = () => RECITERS.find(r => r.id === st.reciter) || RECITERS[0];
const audioURL = (s, a) => `${AUDIO_BASE}${reciter().dir}${pad3(s)}${pad3(a)}.mp3`;
const preload = new Audio();

function playAyah(s, a, mode) {
  const meta = SURAS[s - 1];
  pl.sura = s; pl.ayah = a; pl.total = meta.v; if (mode) pl.mode = mode;
  audio.src = audioURL(s, a);
  audio.play().then(() => { pl.playing = true; updPlayer(); }).catch(() => { pl.playing = false; updPlayer(true); });
  if (a < meta.v) preload.src = audioURL(s, a + 1);
  markAyah();
  if ("mediaSession" in navigator) {
    navigator.mediaSession.metadata = new MediaMetadata({ title: `${sname(meta)} ${s}:${a}`, artist: reciter().name, album: "Kitab" });
  }
  updPlayer();
}
audio.addEventListener("ended", () => {
  if (pl.mode !== "all") { pl.playing = false; updPlayer(); markAyah(); return; }
  if (pl.ayah < pl.total) return playAyah(pl.sura, pl.ayah + 1);
  if (st.autoNext && pl.sura < 114) {
    const nx = pl.sura + 1;
    if (route.name === "sura") go("sura", nx).then(() => playAyah(nx, 1, "all")); else playAyah(nx, 1, "all");
    return;
  }
  pl.playing = false; updPlayer(); markAyah();
});
audio.addEventListener("pause", () => { pl.playing = false; updPlayer(); });
audio.addEventListener("play", () => { pl.playing = true; updPlayer(); });
audio.addEventListener("error", () => updPlayer(true));
if ("mediaSession" in navigator) {
  navigator.mediaSession.setActionHandler("nexttrack", () => step(1));
  navigator.mediaSession.setActionHandler("previoustrack", () => step(-1));
}
function step(d) { if (!pl.sura) return; const a = pl.ayah + d; if (a >= 1 && a <= pl.total) playAyah(pl.sura, a); }
function toggle() { if (!pl.sura) return; audio.paused ? audio.play() : audio.pause(); }
function stopAll() { audio.pause(); pl.sura = 0; updPlayer(); markAyah(); }
function markAyah() {
  document.querySelectorAll(".ayah.on").forEach(e => e.classList.remove("on"));
  document.querySelectorAll(".ayah [data-play][aria-pressed=true]").forEach(b => { b.setAttribute("aria-pressed", "false"); b.textContent = "▶"; });
  if (route.name !== "sura" || route.arg !== pl.sura) return;
  const el = document.getElementById("a" + pl.ayah);
  if (!el) return;
  el.classList.add("on");
  const b = el.querySelector("[data-play]");
  if (b && pl.playing) { b.setAttribute("aria-pressed", "true"); b.textContent = "❚❚"; }
  const r = el.getBoundingClientRect();
  if (pl.mode === "all" && (r.top < 70 || r.bottom > innerHeight - 140)) el.scrollIntoView({ behavior: "smooth", block: "center" });
}
function updPlayer(err) {
  const p = $("#player");
  if (!pl.sura) { p.classList.remove("show"); return; }
  p.classList.add("show");
  const m = SURAS[pl.sura - 1];
  $("#ptitle").innerHTML = err ? T("Audio yuklanmadi (internetni tekshiring)") : `<b>${esc(sname(m))}</b> · ${pl.sura}:${pl.ayah} · ${esc(reciter().name)}`;
  $("#ptog").textContent = pl.playing ? "❚❚" : "▶";
  $("#ptog").setAttribute("aria-label", T(pl.playing ? "To'xtatish" : "Ijro etish"));
  const b = document.querySelector('[data-all]');
  if (b) b.textContent = T(pl.mode === "all" && pl.playing && pl.sura === route.arg ? "❚❚ To'xtatish" : "▶ Butun surani o'qish");
  markAyah();
}

/* ---------- Router ---------- */
const route = { name: "quran", arg: null };
const TABS = [
  ["quran", "Qur'on", '<path d="M4 5c3-1 6-1 8 1 2-2 5-2 8-1v14c-3-1-6-1-8 1-2-2-5-2-8-1z"/><path d="M12 6v14"/>'],
  ["namoz", "Namoz vaqti", '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'],
  ["tasbeh", "Tasbeh", '<circle cx="12" cy="5" r="2"/><circle cx="6" cy="9" r="2"/><circle cx="18" cy="9" r="2"/><circle cx="7" cy="16" r="2"/><circle cx="17" cy="16" r="2"/><path d="M12 18v4"/>'],
  ["qibla", "Qibla", '<circle cx="12" cy="12" r="9"/><path d="M12 4l3 9-3-2-3 2z"/>'],
  ["yana", "Yana", '<circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/>']
];
const ICON = p => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${p}</svg>`;
const MORE = [
  ["ramazon", "Ramazon taqvimi", "Saharlik va iftorlik vaqtlari", '<path d="M15 3a9 9 0 1 0 6 15A7 7 0 0 1 15 3z"/>'],
  ["jonli", "Makka va Madina", "Jonli efir", '<rect x="3" y="6" width="18" height="13" rx="2"/><path d="M10 10l5 2.5-5 2.5z"/>'],
  ["tajvid", "Tajvid", "Qur'on o'qish qoidalari", '<path d="M4 19l4-14h8l4 14"/><path d="M7 13h10"/>'],
  ["harflar", "Arab harflari", "28 harf va ularning shakllari", '<path d="M18 6c0 6-3 10-9 10H5"/><circle cx="9" cy="20" r="1"/>'],
  ["sana", "Sana", "Milodiy va hijriy taqvim", '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>'],
  ["sozlama", "Sozlamalar", "Shrift, uslub, qori, tarjima", '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2"/>'],
  ["manbalar", "Manbalar", "Matn va audio qayerdan olingan", '<path d="M4 4h12l4 4v12H4z"/><path d="M8 12h8M8 16h6"/>']
];
const TITLES = Object.fromEntries([...TABS.map(t => [t[0], t[1]]), ...MORE.map(m => [m[0], m[1]])]);

async function go(name, arg = null, push = true) {
  route.name = name; route.arg = arg;
  if (push) history.pushState({ name, arg }, "", "#" + name + (arg ? "/" + arg : ""));
  await render();
  scrollTo(0, 0);
}
addEventListener("popstate", e => { const s = e.state || parseHash(); route.name = s.name; route.arg = s.arg; render(); });
function parseHash() { const [n, a] = location.hash.slice(1).split("/"); return { name: n || "quran", arg: a ? +a : null }; }

function shell() {
  const top = TABS.some(t => t[0] === route.name);
  $("#back").classList.toggle("hide", top);
  $("#title").textContent = route.name === "sura" ? `${route.arg}. ${sname(SURAS[route.arg - 1])}` : T(TITLES[route.name] || "Kitab");
  if (route.name === "quran") $("#title").textContent = "Kitab";
  $("#lat").setAttribute("aria-pressed", st.script === "lat"); $("#kir").setAttribute("aria-pressed", st.script === "kir");
  const active = route.name === "sura" ? "quran" : (TABS.some(t => t[0] === route.name) ? route.name : "yana");
  $("#nav").innerHTML = TABS.map(([k, l, i]) => `<button data-tab="${k}" ${k === active ? 'aria-current="page"' : ""}>${ICON(i)}<span>${T(l)}</span></button>`).join("");
  document.documentElement.dataset.style = st.style;
  document.documentElement.style.setProperty("--arsize", st.arsize + "px");
  document.documentElement.lang = st.script === "kir" ? "uz-Cyrl" : "uz-Latn";
}

async function render() {
  shell();
  const m = $("#main");
  const v = VIEWS[route.name] || VIEWS.quran;
  try { m.innerHTML = await v(); } catch (e) { m.innerHTML = `<div class="note">${T("Yuklashda xato. Internetni tekshirib, qayta urinib ko'ring.")}</div>`; console.error(e); }
  AFTER[route.name]?.();
}

/* ---------- Ekranlar ---------- */
const VIEWS = {
  async quran() {
    const d = dateLine();
    const last = st.last ? SURAS[st.last.s - 1] : null;
    return `<div class="datebar"><span>${T(d.greg)}</span><b>${T(d.hijri)}</b></div>
    ${last ? `<button class="btn2" style="width:100%;margin-bottom:12px" data-open="${st.last.s}" data-ayah="${st.last.a}">${T("Davom ettirish")}: ${esc(sname(last))} ${st.last.s}:${st.last.a}</button>` : ""}
    <input class="search" id="q" type="search" placeholder="${T("Sura nomi yoki raqami")}" aria-label="${T("Sura qidirish")}">
    <ul class="slist" id="slist">${suraItems("")}</ul>`;
  },
  async sura() {
    const n = route.arg, meta = SURAS[n - 1], d = await loadSura(n);
    st.last = st.last && st.last.s === n ? st.last : { s: n, a: 1 }; save("last");
    const tr = st.tr !== "none" ? d[st.tr] : null, fns = st.tr !== "none" ? d[st.tr + "_fn"] : null;
    const bism = n !== 1 && n !== 9 ? splitBasmala(d.ar[0], (await loadSura(1)).ar[0]) : null;
    const place = T(meta.place === "makkah" ? "Makkiy" : "Madaniy");
    let h = `<div class="card sura"><div class="stitle"><h2>${esc(meta.ar)}</h2><div class="sub">${meta.uz ? `<b lang="uz-Cyrl">${esc(meta.uz)}</b> · ` : ""}${esc(meta.lat)} · ${place} · ${meta.v} ${T("oyat")}</div></div>
    <div class="row" style="justify-content:center"><button class="btn" data-all>${T("▶ Butun surani o'qish")}</button>
    <select id="rec" aria-label="${T("Qori")}">${RECITERS.map(r => `<option value="${r.id}" ${r.id === st.reciter ? "selected" : ""}>${esc(r.name)}</option>`).join("")}</select></div>
    <div class="row" style="justify-content:center"><label><input type="checkbox" id="autonext" ${st.autoNext ? "checked" : ""}> ${T("Keyingi suraga avtomatik o'tish")}</label></div>`;
    if (bism) h += `<p class="ar bism">${esc(bism[0])}</p>`;
    d.ar.forEach((ar, i) => {
      const a = i + 1, txt = i === 0 && bism ? bism[1] : ar;
      h += `<div class="ayah" id="a${a}"><div class="arow"><span class="num">${a}</span><span class="sp"></span>
      <button class="ib" data-play="${a}" aria-pressed="false" aria-label="${T("Oyatni tinglash")} ${a}">▶</button></div>
      <p class="ar">${esc(txt)}</p>${tr ? `<div class="tr">${esc(tr[i])}</div>` : ""}${st.fn && fns && fns[i] ? `<div class="fn">${esc(fns[i])}</div>` : ""}</div>`;
    });
    h += `<div class="src">${T("Arabcha matn")}: <a href="https://tanzil.net" target="_blank" rel="noopener">Tanzil Project</a> (Uthmani 1.1, CC BY 3.0).
      ${tr ? `${T("Tarjima")}: ${trCredit()} — <a href="https://quranenc.com" target="_blank" rel="noopener">QuranEnc.com</a>.` : ""}
      ${T("Audio")}: Quran.com (Quran Foundation).
      ${meta.uz ? `${T("Sura nomi (o'zbekcha)")}: <a href="https://quranenc.com/uz/browse/uzbek_sadiq/${n}" target="_blank" rel="noopener">QuranEnc.com</a>.` : ""} <br>${T("Holat: olim tekshiruvi kutilmoqda.")}</div></div>
      <div class="row" style="justify-content:space-between">${n > 1 ? `<button class="btn2" data-open="${n - 1}">← ${esc(sname(SURAS[n - 2]))}</button>` : "<span></span>"}
      ${n < 114 ? `<button class="btn2" data-open="${n + 1}">${esc(sname(SURAS[n]))} →</button>` : ""}</div>`;
    return h;
  },
  async namoz() {
    return `<div class="card"><div class="row"><label for="reg">${T("Hudud")}</label><select id="reg">${regionOpts()}</select></div>
    <div id="pt" class="mut">${T("Yuklanmoqda…")}</div>
    <div class="note">${T("Vaqtlar taxminiy hisob ({Aladhan}, 15°, Hanafiy). Idora Fatvo markazining taqvim boti ({@fatvouz_taqvim_bot}) jadvaliga moslangan: 2026-yil 25-noyabr – 1-dekabr kunlari daqiqasigacha tekshirildi (Asr ba'zan 1 daqiqa kech chiqishi mumkin). Rasmiy vaqt — {@fatvouz_taqvim_bot}.")}</div></div>`;
  },
  async tasbeh() {
    const c = store.get("tcount", 0), goal = store.get("tgoal", 33), rounds = store.get("trounds", 0);
    let Z = [];
    try { Z = await loadZikr(); } catch {}
    const sel = Z.find(z => z.id === store.get("tzikr", ""));
    const top = sel ? `<p class="ar zk-now" id="tz" dir="rtl" lang="ar">${esc(sel.phrases[rounds % sel.phrases.length])}</p>
      ${sel.second?.compare.some(x => x.farq) ? `<p class="mut"><span class="farq-badge">FARQ BOR</span> ${T("Ikki manbada harakatlar farq qiladi — pastda ikkalasi ko'rsatilgan.")}</p>` : ""}` : "";
    return `<div class="card" style="text-align:center">${top}
      <button class="counter" id="tap" aria-label="${T("Sanash")}"><span><span id="tc">${c}</span><small id="tg">${goal ? "/ " + goal : "∞"} · ${T("davra")}: <span id="tr">${rounds}</span></small></span></button>
      <div class="row" style="justify-content:center">${[33, 99, 100, 0].map(g => `<button class="ib" data-goal="${g}" aria-pressed="${g === goal}">${g || "∞"}</button>`).join("")}</div>
      <div class="row" style="justify-content:center"><button class="btn2" id="treset">${T("Nolga qaytarish")}</button></div>
      <p class="mut">${T("Ekranning istalgan joyiga emas, faqat doiraga bosing. Maqsadga yetganda telefon titraydi.")}</p>
    </div>
    <div class="card"><h2>${T("Zikrlar")}</h2>
      <div class="note">${T("Olim tekshiruvi kerak. Matnlar manbadan o'zgarishsiz olingan: hadis — {sunnah.com} (Sahih al-Buxoriy), tarjima — {HadeethEnc}.")}</div>
      ${Z.length ? Z.map(z => zikrCard(z, sel)).join("") : `<p class="mut">${T("Zikr matnlarini yuklab bo'lmadi. Internetni tekshiring.")}</p>`}
    </div>`;
  },
  async qibla() {
    const reg = REGIONS[st.region];
    const b = bearing(reg[1], reg[2]);
    return `<div class="card" style="text-align:center">
      <div class="compass" id="comp"><div class="dial" id="dial"><span>N</span>
      <div class="qarm" id="qarm" style="transform:rotate(${b}deg)"><div class="needle"></div>
      <svg class="kaaba" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="6" width="14" height="14" fill="#111" stroke="#e7c873"/><path d="M5 10h14" stroke="#e7c873" stroke-width="2"/></svg></div></div></div>
      <p><b style="color:var(--goldb);font-size:22px" id="qdeg">${b.toFixed(1)}°</b><br><span class="mut">${T("Shimoldan soat yo'nalishi bo'yicha")} · ${T(reg[0])}</span></p>
      <div class="row" style="justify-content:center"><button class="btn" id="qstart">${T("Kompasni yoqish")}</button><button class="btn2" id="qgps">${T("Joylashuvimni aniqlash")}</button></div>
      <p class="mut" id="qmsg">${T("Telefonni tekis ushlang. Temir va magnitlardan uzoqroq turing.")}</p></div>`;
  },
  async yana() {
    return `<div class="grid">${MORE.map(([k, l, s, i]) => `<button class="tile" data-go="${k}">${ICON(i)}<b>${T(l)}</b><small>${T(s)}</small></button>`).join("")}</div>`;
  },
  async ramazon() {
    return `<div class="card"><div class="row"><label for="reg">${T("Hudud")}</label><select id="reg">${regionOpts()}</select></div>
    <div class="note">${T("Ramazon 1448 h. — taxminiy hisob. Ramazon boshlanish kuni va rasmiy taqvimni O'zbekiston musulmonlari idorasi e'lon qiladi; e'lon qilingach shu jadval Idora taqvimi bilan almashtiriladi.")}</div>
    <div id="rt" class="mut">${T("Yuklanmoqda…")}</div></div>`;
  },
  async jonli() {
    return LIVE.map(l => `<div class="card"><h2>${T(l.title)}</h2><div class="vid">${l.channel
      ? `<iframe src="https://www.youtube-nocookie.com/embed/${l.video ? encodeURIComponent(l.video) : `live_stream?channel=${encodeURIComponent(l.channel)}`}" title="${esc(l.title)}" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen loading="lazy"></iframe>`
      : `<span class="mut">${T("Rasmiy kanal hali tasdiqlanmadi. Saudiya rasmiy kanali ({SBA}) aniqlangach shu yerda jonli efir ochiladi.")}</span>`}</div>${l.channel
      ? `<p class="mut">${T("Manba")}: <a href="https://www.youtube.com/channel/${encodeURIComponent(l.channel)}" target="_blank" rel="noopener">${esc(l.name)} (${esc(l.handle)})</a> — ${T("Saudiya Radio va Televideniye idorasi ({SBA}) rasmiy kanali.")}<br>${T("Video ochilmasa")}: <a href="https://www.youtube.com/channel/${encodeURIComponent(l.channel)}/live" target="_blank" rel="noopener">${T("{YouTube}'da ochish")}</a></p>` : ""}</div>`).join("");
  },
  async tajvid() {
    return `<div class="card"><h2>${T("Tajvid")}</h2>
    <p>${T("Tajvid darslari faqat ishonchli manbadan (O'zbekiston musulmonlari idorasi darsliklari) olinadi. Matnni o'zimizdan yozmaymiz.")}</p>
    <div class="note">${T("Bo'lim tayyorlanmoqda: manba tanlanishi va olim tekshiruvi kutilmoqda.")}</div></div>`;
  },
  async harflar() {
    return `<div class="card"><p class="mut">${T("Harfga bosing — uning so'z boshida, o'rtasida va oxiridagi shakli chiqadi.")}</p>
    <div id="lform"></div><div class="letters">${LETTERS.map(([c, n], i) => `<button data-letter="${i}"><span class="l">${c}</span><small>${T(n)}</small></button>`).join("")}</div></div>`;
  },
  async sana() {
    const now = new Date(), d = dateLine(now), h = hijriParts(now);
    return `<div class="card" style="text-align:center"><p class="mut">${T("Milodiy")}</p><h2 style="font-size:22px">${T(d.greg)}</h2>
    <p class="mut">${T("Hijriy")}</p><h2 style="font-size:26px;color:var(--goldb)">${T(d.hijri)}</h2>
    <p class="mut">${T("Hisob: {Umm al-Qura} taqvimi.")} ${T("Tuzatish")}: <b>${st.hijriAdj > 0 ? "+" : ""}${st.hijriAdj}</b> ${T("kun")}</p>
    <div class="row" style="justify-content:center"><button class="ib" data-hadj="-1">−1</button><button class="ib" data-hadj="0">0</button><button class="ib" data-hadj="1">+1</button></div>
    <div class="note">${T("Hijriy sana Idora e'lonidan bir kun farq qilsa, yuqoridagi tugma bilan to'g'rilang. 25.11.2026 kuni {muslim.uz} ko'rsatgan sana bilan tekshirildi: mos.")}</div></div>
    <div class="card"><h2>${T("Sanani o'girish")}</h2><input class="search" type="date" id="conv" value="${now.toISOString().slice(0, 10)}"><div id="convout" style="color:var(--goldb);font-size:18px"></div></div>`;
  },
  async sozlama() {
    return `<div class="card">
    <div class="row"><label for="s-tr">${T("Tarjima")}</label><select id="s-tr">${[["uz", "O'zbekcha (Shayx Muhammad Sodiq Muhammad Yusuf) — kirill"], ["ru", "Ruscha ({Rowwad} markazi)"], ["en", "Inglizcha ({Saheeh International})"], ["none", "Tarjimasiz"]].map(([k, l]) => `<option value="${k}" ${st.tr === k ? "selected" : ""}>${T(l)}</option>`).join("")}</select></div>
    <div class="row"><label><input type="checkbox" id="s-fn" ${st.fn ? "checked" : ""}> ${T("Tarjima izohlarini ko'rsatish")}</label></div>
    <div class="row"><label for="s-rec">${T("Qori")}</label><select id="s-rec">${RECITERS.map(r => `<option value="${r.id}" ${r.id === st.reciter ? "selected" : ""}>${esc(r.name)}</option>`).join("")}</select></div>
    <div class="row"><label for="s-size">${T("Arabcha shrift o'lchami")}</label><input type="range" id="s-size" min="22" max="44" value="${st.arsize}"></div>
    <div class="row"><label>${T("Oyat rangi")}</label><div class="seg"><button data-style="k6" aria-pressed="${st.style === "k6"}">${T("Yorqin oltin")}</button><button data-style="k7" aria-pressed="${st.style === "k7"}">${T("Metall oltin")}</button></div></div>
    <p class="ar" style="--arsize:${st.arsize}px">${esc((await loadSura(1)).ar[1])}</p>
    <div class="note">${T("O'zbekcha tarjima manbada kirill yozuvida. Lotin yozuviga o'tkazish uchun tarjima egasining ruxsati kerak, shuning uchun u kirillda qoladi.")}</div></div>`;
  },
  async manbalar() {
    return `<div class="card"><h2>${T("Manbalar")}</h2><ul>
    <li>${T("Arabcha matn")}: <a href="https://tanzil.net" target="_blank" rel="noopener">Tanzil Project</a> — Uthmani, ${T("versiya")} 1.1, CC BY 3.0. ${T("Matn o'zgartirilmagan.")}</li>
    <li>${T("O'zbekcha tarjima")}: QuranEnc.com — uzbek_sadiq (${T("versiya aniqlanmadi")}).</li>
    <li>${T("Ruscha tarjima")}: QuranEnc.com — russian_rwwad (${T("versiya aniqlanmadi")}).</li>
    <li>${T("Inglizcha tarjima")}: QuranEnc.com — english_saheeh, ${T("versiya")} 1.1.2.</li>
    <li>${T("Audio")}: Quran.com / Quran Foundation (verses.quran.com).</li>
    <li>${T("Namoz vaqtlari")}: Aladhan API (${T("taxminiy")}), ${T("Idora Fatvo markazining taqvim botiga moslangan")}; ${T("rasmiy")}: <a href="https://t.me/fatvouz_taqvim_bot" target="_blank" rel="noopener">@fatvouz_taqvim_bot</a>, <a href="https://muslim.uz" target="_blank" rel="noopener">muslim.uz</a>.</li>
    <li>${T("Sura nomlari (o'zbekcha)")}: <a href="https://quranenc.com/uz/browse/uzbek_sadiq/1" target="_blank" rel="noopener">QuranEnc.com</a> — ${T("o'zgartirilmagan, kirillda. Olim tekshiruvi kerak.")}</li>
    <li>${T("Tasbeh zikrlari")}: <a href="https://sunnah.com/bukhari" target="_blank" rel="noopener">sunnah.com</a> — Sahih al-Bukhari 843, 6403, 6405; ${T("tarjima va solishtirish")}: <a href="https://hadeethenc.com" target="_blank" rel="noopener">HadeethEnc</a>. ${T("843 va 6403 ning o'zbekcha tarjimasi manbada yo'q: ularni {Claude} (sun'iy intellekt) manbadagi inglizcha/ruscha matndan o'girgan, bu manba emas.")} ${T("Olim tekshiruvi kerak.")}</li>
    <li>${T("Jonli efir")}: ${LIVE.map(l => `<a href="https://www.youtube.com/channel/${encodeURIComponent(l.channel)}" target="_blank" rel="noopener">${esc(l.handle)}</a>`).join(", ")} — ${T("Saudiya Radio va Televideniye idorasi ({SBA}), YouTube.")}</li></ul>
    <p class="mut">${T("Arabcha matn ikkinchi manba ({QuranEnc}) bilan 6236 oyat bo'yicha solishtirildi. Natija: {docs/tekshiruv-hisoboti.md}.")}</p>
    <div class="note">${T("Sinov versiyasi. O'zbekiston musulmonlari idorasi tasdiqlamaguncha ommaga chiqarilmaydi.")}</div></div>`;
  }
};

/* Zikr kartasi: matnlar data/zikr.json dan (tools/build_zikr.py), bu yerda hech narsa yozilmaydi. Tarjimalar T() dan o'tmaydi.
   uz_claude — manba emas: Claude'ning manbadagi ru/en matndan tarjimasi, alohida belgi bilan ko'rsatiladi. */
function zikrCard(z, sel) {
  const num = z.source.url.split(":").pop(), on = sel?.id === z.id;
  const arP = s => `<span class="ar" dir="rtl" lang="ar">${esc(s)}</span>`;
  const farq = (z.second?.compare || []).filter(x => x.farq);
  const cl = z.uz_claude;   // Claude tarjimasi (manba emas): data/zikr-uz-claude.json
  const claude = cl ? `<div class="ai-tr"><b class="farq-badge">${T("Manba emas")}</b>
      <p class="mut">${T("Manbada o'zbekcha tarjima yo'q. Bu tarjimani {Claude} (sun'iy intellekt) quyidagi " + (cl.from === "ru" ? "ruscha" : "inglizcha") + " matndan o'girgan. Idora tekshiruvi kerak.")}</p>
      <p class="tr" lang="uz-Cyrl">${esc(cl.text)}</p>${cl.attribution ? `<p class="src" lang="uz-Cyrl">${esc(cl.attribution)}</p>` : ""}
      <p class="src">${T("Qaysi matndan")}: ${esc(cl.from_source)}. ${T("Sana")}: ${esc(cl.date)}.</p></div>` : "";
  const tr = z.uz
    ? `<p class="tr" lang="uz-Cyrl">${esc(z.uz.text)}</p><p class="src">${T("Tarjima")}: <a href="${esc(z.uz.url)}" target="_blank" rel="noopener">HadeethEnc</a> — ${esc(z.uz.attribution)}, ${esc(z.uz.grade)}. ${T("Olingan")}: ${esc(z.uz.retrieved)}.</p>`
    : claude + (z.ru
      ? `<p class="mut">${T("O'zbekcha tarjima manbada topilmadi. Ruscha tarjima:")}</p><p class="tr" lang="ru">${esc(z.ru.text)}</p><p class="src">${T("Tarjima")}: <a href="${esc(z.ru.url)}" target="_blank" rel="noopener">HadeethEnc</a> — ${esc(z.ru.attribution)}, ${esc(z.ru.grade)}. ${T("Olingan")}: ${esc(z.ru.retrieved)}.</p>`
      : `<p class="mut">${T("O'zbekcha va ruscha tarjima manbada topilmadi. Inglizcha tarjima ({sunnah.com}):")}</p><p class="tr" lang="en">${esc(z.en)}</p>`);
  return `<div class="zk${on ? " on" : ""}">
    <div class="zk-ph">${z.phrases.map(arP).join("")}</div>
    <div class="row"><b class="zk-n">× ${z.count}${z.phrases.length > 1 ? " " + T("(har biri)") : ""}</b>
      <button class="btn2" data-zikr="${esc(z.id)}" aria-pressed="${on}">${T(on ? "Tanlangan" : "Tanlash")}</button></div>
    ${farq.length ? `<div class="farq"><b class="farq-badge">FARQ BOR</b>
      <p class="mut">${T("Ikki manbada harakatlar farq qiladi. Qaysi biri olinishini olim aytadi.")}</p>
      ${farq.map(x => `<div class="farq-row"><div><small>sunnah.com</small>${arP(x.sunnah)}</div><div><small>HadeethEnc #${esc(z.second.id)}</small>${arP(x.hadeethenc)}</div></div>`).join("")}
      ${z.second.same_hadith ? "" : `<p class="src">${T("{HadeethEnc}'dagi matn boshqa hadis (#{" + z.second.id + "}): u faqat iboraning imlosini solishtirish uchun olingan.")}</p>`}</div>` : ""}
    <details><summary>${T("Manba va tarjima")}</summary>
      <p class="src">${T("Manba")}: <a href="${esc(z.source.url)}" target="_blank" rel="noopener">Sahih al-Bukhari ${esc(num)}</a> — sunnah.com. ${T("Daraja")}: ${T("sahih")}. ${T("Olingan")}: ${esc(z.source.retrieved)}.</p>
      ${tr}
      <p class="mut">${T("Hadisning to'liq arabcha matni")}:</p><p class="ar zk-full" dir="rtl" lang="ar">${esc(z.hadith_ar)}</p>
    </details>
  </div>`;
}
function trCredit() { return { uz: T("Shayx Muhammad Sodiq Muhammad Yusuf ({uzbek_sadiq})"), ru: "Rowwad (russian_rwwad)", en: "Saheeh International (english_saheeh 1.1.2)" }[st.tr] || ""; }
function regionOpts() { return Object.entries(REGIONS).map(([k, r]) => `<option value="${k}" ${k === st.region ? "selected" : ""}>${T(r[0])}</option>`).join(""); }
function suraItems(q) {
  q = q.trim().toLowerCase();
  return SURAS.filter(s => !q || String(s.n) === q || s.lat.toLowerCase().includes(q) || s.ar.includes(q) || s.en.toLowerCase().includes(q) || (s.uz || "").toLowerCase().includes(q) || (s.uz || "").toLowerCase().includes(toCyr(q).toLowerCase()))
    .map(s => `<li><button data-open="${s.n}"><span class="num">${s.n}</span><span class="sname"><b lang="${s.uz ? "uz-Cyrl" : "en"}">${esc(sname(s))}</b><small>${s.uz ? esc(s.lat) + " · " : ""}${T(s.place === "makkah" ? "Makkiy" : "Madaniy")} · ${s.v} ${T("oyat")}</small></span><span class="sar">${esc(s.ar)}</span></button></li>`).join("");
}
/* Basmala faqat ko'rinishda alohida qatorga chiqariladi (Tanzil matni o'zgarmaydi):
   1-oyatning dastlabki 4 so'zi Fotiha 1-oyati bilan (shaddasiz) bir xil bo'lsa. */
function splitBasmala(a1, fatiha1) {
  const w = a1.split(" "), b = fatiha1.split(" "), strip = s => s.replace(/ّ/g, "");
  if (w.length > 4 && b.length === 4 && w.slice(0, 4).every((x, i) => strip(x) === strip(b[i]))) return [w.slice(0, 4).join(" "), w.slice(4).join(" ")];
  return null;
}
function bearing(lat, lon) {
  const r = Math.PI / 180, [kl, kn] = MAKKAH;
  const y = Math.sin((kn - lon) * r), x = Math.cos(lat * r) * Math.tan(kl * r) - Math.sin(lat * r) * Math.cos((kn - lon) * r);
  return (Math.atan2(y, x) / r + 360) % 360;
}
async function prayerFor(dateStr) {
  const r = REGIONS[st.region], key = `pt.${st.region}.${dateStr}`;
  const c = store.get(key, null); if (c) return c;
  const j = await getJSON(`https://api.aladhan.com/v1/timings/${dateStr}?latitude=${r[1]}&longitude=${r[2]}&${PT_QS}`);
  const t = j.data.timings; store.set(key, t); return t;
}
const ddmmyyyy = d => `${String(d.getDate()).padStart(2, "0")}-${String(d.getMonth() + 1).padStart(2, "0")}-${d.getFullYear()}`;

const AFTER = {
  quran() { $("#q").addEventListener("input", e => { $("#slist").innerHTML = suraItems(e.target.value); }); },
  sura() {
    if (st.last && st.last.s === route.arg && st.last.a > 1 && pendingAyah === null) pendingAyah = st.last.a;
    if (pendingAyah) { const el = document.getElementById("a" + pendingAyah); if (el) setTimeout(() => el.scrollIntoView({ block: "center" }), 50); pendingAyah = null; }
    updPlayer();
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { st.last = { s: route.arg, a: +e.target.id.slice(1) }; save("last"); } }), { rootMargin: "-45% 0px -50% 0px" });
    document.querySelectorAll(".ayah").forEach(a => io.observe(a));
  },
  async namoz() {
    $("#reg").onchange = e => { st.region = e.target.value; save("region"); render(); };
    try {
      const now = new Date(), t = await prayerFor(ddmmyyyy(now));
      const names = [["Fajr", "Bomdod"], ["Sunrise", "Quyosh"], ["Dhuhr", "Peshin"], ["Asr", "Asr"], ["Maghrib", "Shom"], ["Isha", "Xufton"]];
      const mins = s => { const [h, m] = s.slice(0, 5).split(":"); return +h * 60 + +m; };
      const cur = now.getHours() * 60 + now.getMinutes();
      const nx = names.find(([k]) => mins(t[k]) > cur);
      $("#pt").innerHTML = `<div class="times">${names.map(([k, l]) => `<div class="${nx && nx[0] === k ? "next" : ""}"><span class="mut">${T(l)}</span><b>${t[k].slice(0, 5)}</b></div>`).join("")}</div>`;
    } catch { $("#pt").innerHTML = `<div class="note">${T("Vaqtlarni yuklab bo'lmadi. Internetni tekshiring.")}</div>`; }
  },
  tasbeh() {
    let c = store.get("tcount", 0), goal = store.get("tgoal", 33), rounds = store.get("trounds", 0);
    const sel = (zikrCache || []).find(z => z.id === store.get("tzikr", ""));
    const draw = () => {
      $("#tc").textContent = c; $("#tr").textContent = rounds; store.set("tcount", c); store.set("trounds", rounds);
      if (sel && $("#tz")) $("#tz").textContent = sel.phrases[rounds % sel.phrases.length];
    };
    $("#tap").onclick = () => { c++; if (goal && c >= goal) { rounds++; c = 0; navigator.vibrate?.([80, 60, 80]); } else navigator.vibrate?.(15); draw(); };
    $("#treset").onclick = () => { c = 0; rounds = 0; draw(); };
    document.querySelectorAll("[data-goal]").forEach(b => b.onclick = () => { store.set("tgoal", +b.dataset.goal); store.set("tzikr", ""); render(); });
    document.querySelectorAll("[data-zikr]").forEach(b => b.onclick = () => {
      const z = zikrCache.find(x => x.id === b.dataset.zikr), off = z.id === store.get("tzikr", "");
      store.set("tzikr", off ? "" : z.id); if (!off) store.set("tgoal", z.count);
      store.set("tcount", 0); store.set("trounds", 0); render(); scrollTo({ top: 0, behavior: "smooth" });
    });
  },
  qibla() {
    let target = bearing(REGIONS[st.region][1], REGIONS[st.region][2]);
    const setB = b => { target = b; $("#qdeg").textContent = b.toFixed(1) + "°"; $("#qarm").style.transform = `rotate(${b}deg)`; };
    const onOri = e => {
      const head = e.webkitCompassHeading ?? (e.absolute && e.alpha != null ? 360 - e.alpha : null);
      if (head == null) return;
      $("#dial").style.transform = `rotate(${-head}deg)`;
      const diff = Math.abs(((target - head + 540) % 360) - 180);
      $("#qmsg").textContent = diff < 5 ? T("Qibla yo'nalishidasiz ✓") : T("Telefonni oltin strelka tepaga qaragunicha buring.");
      if (diff < 5) navigator.vibrate?.(30);
    };
    $("#qstart").onclick = async () => {
      try { if (typeof DeviceOrientationEvent?.requestPermission === "function" && (await DeviceOrientationEvent.requestPermission()) !== "granted") throw 0; } catch { $("#qmsg").textContent = T("Kompasga ruxsat berilmadi."); return; }
      addEventListener("deviceorientationabsolute", onOri); addEventListener("deviceorientation", onOri);
      $("#qmsg").textContent = T("Kompas yoqildi. Telefonni sakkiz shaklida aylantirib sozlang.");
    };
    $("#qgps").onclick = () => navigator.geolocation?.getCurrentPosition(p => setB(bearing(p.coords.latitude, p.coords.longitude)), () => { $("#qmsg").textContent = T("Joylashuvga ruxsat berilmadi; hudud bo'yicha hisoblandi."); });
  },
  async ramazon() {
    $("#reg").onchange = e => { st.region = e.target.value; save("region"); render(); };
    const r = REGIONS[st.region], key = `ram1448.${st.region}`;
    try {
      let rows = store.get(key, null);
      if (!rows) {
        const j = await getJSON(`https://api.aladhan.com/v1/hijriCalendar/1448/9?latitude=${r[1]}&longitude=${r[2]}&${PT_QS}`);
        rows = j.data.map(d => [d.date.hijri.day, d.date.gregorian.date, d.timings.Fajr.slice(0, 5), d.timings.Maghrib.slice(0, 5)]);
        store.set(key, rows);
      }
      const today = ddmmyyyy(new Date());
      $("#rt").innerHTML = `<table class="tt"><thead><tr><th>${T("Kun")}</th><th>${T("Sana")}</th><th>${T("Saharlik (tugashi)")}</th><th>${T("Iftorlik")}</th></tr></thead><tbody>${rows.map(([h, g, f, m]) => `<tr class="${g === today ? "today" : ""}"><td>${+h}</td><td>${g.slice(0, 5).replace("-", ".")}</td><td>${f}</td><td>${m}</td></tr>`).join("")}</tbody></table>`;
    } catch { $("#rt").innerHTML = `<div class="note">${T("Taqvimni yuklab bo'lmadi. Internetni tekshiring.")}</div>`; }
  },
  harflar() {
    document.querySelectorAll("[data-letter]").forEach(b => b.onclick = () => {
      const [c, n, joins] = LETTERS[+b.dataset.letter], Z = "‍";
      const f = [["Alohida", c], ["Boshida", joins ? c + Z : c], ["O'rtasida", joins ? Z + c + Z : Z + c], ["Oxirida", Z + c]];
      $("#lform").innerHTML = `<div class="card" style="margin-top:0"><h2 style="text-align:center">${T(n)}</h2><div class="forms">${f.map(([l, s]) => `<div><span class="l">${s}</span><small>${T(l)}</small></div>`).join("")}</div></div>`;
      $("#lform").scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  },
  sana() {
    document.querySelectorAll("[data-hadj]").forEach(b => b.onclick = () => { st.hijriAdj = +b.dataset.hadj; save("hijriAdj"); render(); });
    const conv = () => { const v = $("#conv").value; if (!v) return; const d = new Date(v + "T12:00:00"); $("#convout").textContent = dateLine(d).hijri; };
    $("#conv").oninput = conv; conv();
  },
  sozlama() {
    $("#s-tr").onchange = e => { st.tr = e.target.value; save("tr"); };
    $("#s-fn").onchange = e => { st.fn = e.target.checked; save("fn"); };
    $("#s-rec").onchange = e => { st.reciter = +e.target.value; save("reciter"); };
    $("#s-size").oninput = e => { st.arsize = +e.target.value; save("arsize"); document.documentElement.style.setProperty("--arsize", st.arsize + "px"); $(".card .ar").style.setProperty("--arsize", st.arsize + "px"); };
    document.querySelectorAll("[data-style]").forEach(b => b.onclick = () => { st.style = b.dataset.style; save("style"); render(); });
  }
};
let pendingAyah = null;

/* ---------- Umumiy bosishlar ---------- */
document.addEventListener("click", e => {
  const t = e.target.closest("button"); if (!t) return;
  if (t.dataset.tab) return go(t.dataset.tab);
  if (t.dataset.go) return go(t.dataset.go);
  if (t.dataset.open) { pendingAyah = t.dataset.ayah ? +t.dataset.ayah : 0; return go("sura", +t.dataset.open); }
  if (t.dataset.play) {
    const a = +t.dataset.play;
    if (pl.sura === route.arg && pl.ayah === a && pl.playing) return audio.pause();
    return playAyah(route.arg, a, "one");
  }
  if (t.hasAttribute("data-all")) {
    if (pl.mode === "all" && pl.playing && pl.sura === route.arg) return audio.pause();
    const from = pl.sura === route.arg && pl.ayah ? pl.ayah : 1;
    return playAyah(route.arg, from, "all");
  }
});
document.addEventListener("change", e => {
  if (e.target.id === "rec") { st.reciter = +e.target.value; save("reciter"); if (pl.sura) playAyah(pl.sura, pl.ayah); }
  if (e.target.id === "autonext") { st.autoNext = e.target.checked; save("autoNext"); }
});

async function init() {
  $("#back").onclick = () => history.length > 1 ? history.back() : go("quran");
  $("#lat").onclick = () => { st.script = "lat"; save("script"); render(); };
  $("#kir").onclick = () => { st.script = "kir"; save("script"); render(); };
  $("#ptog").onclick = toggle; $("#pprev").onclick = () => step(-1); $("#pnext").onclick = () => step(1); $("#pstop").onclick = stopAll;
  SURAS = await getJSON("data/suras.json");
  const h = parseHash(); route.name = h.name; route.arg = h.arg;
  if (route.name === "sura" && !(route.arg >= 1 && route.arg <= 114)) route.name = "quran";
  history.replaceState({ name: route.name, arg: route.arg }, "", location.hash || "#quran");
  await render();
  if ("serviceWorker" in navigator && location.protocol !== "file:") navigator.serviceWorker.register("sw.js").catch(() => {});
}
init();
