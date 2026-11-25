/* Oflayn ishlash: ilova fayllari va o'qilgan suralar keshda saqlanadi. Audio keshlanmaydi. */
const V = "kitab-v4";
const CORE = ["./", "index.html", "style.css", "app.js", "manifest.webmanifest", "icons/icon.svg", "data/suras.json", "data/s/001.json", "data/zikr.json"];
self.addEventListener("install", e => e.waitUntil(caches.open(V).then(c => c.addAll(CORE)).then(() => self.skipWaiting())));
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.hostname.endsWith("quran.com") || u.hostname.endsWith("aladhan.com")) return;
  e.respondWith(caches.match(e.request).then(hit => {
    const net = fetch(e.request).then(r => { if (r.ok && (u.origin === location.origin || u.hostname.includes("fonts"))) { const copy = r.clone(); caches.open(V).then(c => c.put(e.request, copy)); } return r; });
    return hit ? (net.catch(() => hit), hit) : net;
  }));
});
