# Kitab: Claude Code uchun yo'riqnoma

Egasi: Mc Raximjon (GitHub: mirzajonov8144-del). U texnik mutaxassis emas.
- Javoblarni o'zbek tilida (lotin yozuvida), oddiy so'zlar bilan yozing.
- Har bir inglizcha so'zdan keyin qavs ichida ruscha tarjimasini bering. Sayt, dastur va odam nomlari bundan mustasno.
- Sozlash qadamlarini raqamlab yozing, tugma nomlarini rus tilida bering.
- Pullik yoki ortga qaytarib bo'lmaydigan ishdan (o'chirish, nashr qilish, to'lov) oldin egasidan ruxsat so'rang.

## Loyiha
Qur'on o'quv ilovasi. Telefon uchun PWA, build (yig'ish) bosqichi yo'q: oddiy HTML, CSS va JS.
- Sinov sayti (GitHub Pages): https://mirzajonov8144-del.github.io/kitab/ — `claude/project-thread-8e57y8` branch'idan, "/ (root)" papkasidan.
- PR #1: shu branch'dan `main` ga. Hali birlashtirilmagan.
- Repo ochiq. Egasining qarori (2026-11-25): ish tugaguncha repo ochiq turishi mumkin. O'zbekiston musulmonlari idorasi ruxsati Google Play yoki ijtimoiy tarmoqlarga chiqarishdan OLDIN olinadi.

## Fayllar
| Fayl | Vazifasi |
|---|---|
| `index.html` | Qobiq: sarlavha, audio pleyer, pastki menyu |
| `style.css` | Kisva uslubi: qora fon, oltin ramka, K6 (yorqin oltin) va K7 (metall oltin) |
| `app.js` | Butun mantiq: router (`#nom/arg`), ekranlar (`VIEWS`), hodisalar (`AFTER`), audio, sanalar, qibla, Lotin→Kirill |
| `sw.js` | Oflayn kesh. Fayl o'zgarsa, `V` versiyasini oshiring |
| `data/suras.json` | 114 sura: nomi, oyatlar soni, Makkiy/Madaniy |
| `data/s/NNN.json` | Har bir sura: `ar` (Tanzil), `uz`/`ru`/`en` tarjimalari va `*_fn` izohlari (QuranEnc) |
| `data/zikr.json` | Tasbeh zikrlari: sunnah.com (Buxoriy) matni, HadeethEnc tarjimasi va solishtiruvi |
| `tools/build_zikr.py` | `data/zikr.json` ni manbalardan yig'adi: `python -I -X utf8 tools/build_zikr.py data` |
| `data/TANZIL-LICENSE.txt` | Tanzil litsenziyasi. O'chirmang |
| `tools/build_data.py` | `data/` ni manba fayllardan qayta yig'adi |
| `tools/verify_arabic.py` | Tanzil va QuranEnc arabcha matnini harfma-harf solishtiradi |
| `docs/tekshiruv-hisoboti.md` | Tekshiruv natijalari |

Lokal ishga tushirish: `python3 -m http.server 8000`, keyin brauzerda http://localhost:8000.

## TEMIR QOIDALAR (diniy matn)
1. Oyat, tarjima, tafsir, duo, hadis yoki zikr matnini HECH QACHON xotiradan yozmang, hatto "qoralama" sifatida ham. Matn faqat manbadan, so'zma-so'z olinadi. Manba topilmasa, "manba topilmadi" deb to'xtang.
2. Matnni o'zgartirmang: qisqartirmang, imloni tuzatmang. Ruxsatsiz kirill yozuvidan lotinga o'tkazmang: O'zbekcha tarjima kirillda qoladi, Lotin→Kirill konvertori (`toCyr`) faqat interfeys matni uchun.
3. Har bir matn yonida manba bo'lsin: sayt, muallif yoki tarjimon, versiya, havola, olingan sana.
4. Arabcha matnni ikkinchi manba bilan harfma-harf solishtiring. Farq chiqsa, "FARQ BOR" deb ikkala variantni yonma-yon ko'rsating va o'zingiz birini tanlamang.
5. Hadis faqat to'plam nomi, raqami va darajasi bilan olinadi. Asosiy to'plam — Sahih al-Buxoriy.
6. Payg'ambarlar hech qachon tasvirlanmaydi: rasm, AI-rasm, aktyor ham, ovoz bilan "o'ynatish" ham yo'q.
7. Hamma diniy matn olim tekshiruvidan o'tguncha "Olim tekshiruvi kerak" holatida qoladi.

Ruxsat etilgan manbalar:
- Asosiy: O'zbekiston musulmonlari idorasi (muslim.uz).
- Solishtirish uchun: Tanzil (tanzil.net), Quran Foundation (api.quran.com), QuranEnc (quranenc.com), sunnah.com, HadeethEnc.
- Boshqa sayt kerak bo'lsa, avval egasidan so'rang.

## Hozirgi holat (2026-11-25)
Ishlaydi:
- 114 sura va 6236 oyat, 3 tilda tarjima va izohlar.
- Oyatni alohida va butun surani ketma-ket tinglash, keyingi suraga o'tish, 9 qori (`verses.quran.com/<dir>/SSSAAA.mp3`).
- Namoz vaqti: Aladhan, `method=99&methodSettings=15,null,15&school=1&tune=0,-3,-5,5,0,4,0,0,0`. Idora Fatvo markazining @fatvouz_taqvim_bot jadvaliga moslangan (egasi qarori, 2026-11-25): Namangan viloyatidagi bir nuqta, 25.11–01.12, 42/42 mos (formula nusxasi bilan). Aladhan Asr'ni ~0,3 daqiqa kech hisoblaydi, shuning uchun Asr ba'zan +1 daqiqa. Avvalgi sozlama (`0,-3,-4,5,-1,3,0,-1,0`) muslim.uz'dagi Toshkent vaqtiga mos edi; Idoraning ikki manbasi Quyosh/Shom/Xufton bo'yicha 1 daqiqa farq qiladi. Foydalanuvchi koordinatalari repoga yozilmaydi (repo ochiq).
- Ramazon 1448 taqvimi (taxminiy), tasbeh, qibla (kompas va GPS), sana (Umm al-Qura, ±1 tuzatish), arab harflari va ularning 4 shakli, sozlamalar, manbalar sahifasi.

Qilinishi kerak (kamchiliklar):
1. **Arabcha matn farqlari:** 355 oyatda Tanzil va QuranEnc arabcha matni farq qiladi (iqlob tanvini, kichik yo/vov, vaqf belgilari). Olim qaysi nashrni olishni aytishi kerak. Batafsil: `docs/tekshiruv-hisoboti.md`.
2. **Makka/Madina jonli efiri (qisman bajarildi, 2026-11-25):** `LIVE` da Makka — @SaudiQuranTv (`UCos52azQNBgW63_9uDJoPDA`), Madina — @SaudiSunnahTv (`UCROKYPep-UuODNwyipe6JMw`). Ikkalasida YouTube tasdiq belgisi bor, tavsifida SBA'ga tegishli deyilgan. QOLDI: sba.sa saytidan havola tekshirilmadi (sayt bizdan ham, bulutdan ham ochilmadi). Makka kanali uchun `live_stream?channel=` embed'i ishlamadi, shuning uchun `LIVE[].video` (hozirgi efir ID'si) ishlatiladi: efir qayta boshlansa uni yangilang.
3. **Tajvid:** hozircha faqat bo'sh sahifa. Darslar Idora manbasidan olinadi. 2026-11-25: muslim.uz va old.muslim.uz'da tajvid darslari topilmadi, egasi manba berishi kerak. Quran.com `text_uthmani_tajweed` matnidan foydalanmang: unda U+0670 o'rniga U+0672 turadi.
4. **Tasbeh zikr matnlari (qisman, 2026-11-25):** 3 ta zikr qo'shildi: Buxoriy 843 (namozdan keyin 33 tadan), 6405 (100), 6403 (100). Ma'lumot `data/zikr.json`, uni `tools/build_zikr.py` yig'adi. Zikr iborasi sunnah.com'dagi hadis matnidan harfma-harf kesib olinadi. Uchala zikrda ham HadeethEnc bilan harakat farqi bor (masalan, «اللَّهِ» / «اللهِ»), ikkalasi "FARQ BOR" deb ko'rsatiladi. QOLDI: olim qaysi imloni olishni aytishi kerak. 6403 uchun o'zbekcha tarjima yo'q (faqat ruscha), 843 uchun faqat inglizcha bor. Idora (muslim.uz) zikr manbasi topilmadi. Hammasi "Olim tekshiruvi kerak" holatida.
5. **Namoz vaqtlari:** Fatvo boti bilan faqat bitta nuqtada (Namangan viloyati) 7 kun tekshirildi. Boshqa viloyatlar uchun ham botdan haftalik jadval olib tekshirish kerak (bot faqat Telegram'da joylashuv bo'yicha ishlaydi). Yozda (iyun) yana bir marta tekshiring. muslim.uz'da boshqa kun/hudud jadvali yo'q. Ramazon taqvimi chiqqach, uni Idoraning rasmiy taqvimi bilan almashtiring.
6. **Sura nomlari:** hozir faqat arabcha va Quran.com transliteratsiyasida. O'zbekcha nomlarni manbadan oling.
7. **Audio litsenziyasi:** Google Play'dan oldin Quran Foundation API shartlarini tekshiring va API kaliti oling.
8. **Tarjima versiyalari:** `uzbek_sadiq` va `russian_rwwad` versiyalari aniqlanmagan. QuranEnc'dan so'rang.
9. **Lotin yozuvidagi tarjima:** buning uchun tarjima egasining yozma ruxsati kerak.
10. **Kelajakda:** Duolar va Hadislar bo'limlari, payg'ambarlar mo'jizalari (rejaga qarang), Google Play uchun TWA yoki Capacitor.

## Ishlash tartibi
- Har bir o'zgarishdan keyin 390px kenglikdagi telefon ekranida tekshiring: konsolda xato bo'lmasligi kerak.
- Har bir bosqichni egasiga ko'rsating, keyin davom eting.
- `sw.js` da `V` versiyasini oshirishni unutmang, aks holda telefonda eski versiya qoladi.

## Havolalar
- Ilova rejasi: https://claude.ai/artifact/1Vjb9pJoNvicvFHHJJYY18
- Dizayn prototipi (K6/K7): https://claude.ai/artifact/6poFX6FTTQwYN2zvcnW471
