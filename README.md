# Kitab

Qur'on o'quv ilovasi (PWA, telefon uchun). **Sinov versiyasi — O'zbekiston musulmonlari idorasi tasdiqlamaguncha ommaga chiqarilmaydi.**

## Nima bor
- 114 sura, 6236 oyat: arabcha matn (Tanzil Uthmani 1.1) + tarjima (o'zbekcha kirill / ruscha / inglizcha, QuranEnc).
- Har bir oyatni alohida tinglash, butun surani avtomatik o'qish, 9 qori (Quran.com audio).
- Pastki menyu: Qur'on, Namoz vaqti, Tasbeh, Qibla, Yana.
- "Yana": Ramazon taqvimi, Makka/Madina jonli efiri, Tajvid, Arab harflari, Milodiy + hijriy sana, Sozlamalar, Manbalar.
- Interfeys Lotin va Kirill yozuvida. Dizayn: qora fon, kisva uslubidagi oltin ramka (K6/K7).

## Qoidalar
- Diniy matn faqat manbadan, so'zma-so'z olinadi (`data/`), xotiradan yozilmaydi.
- Tekshiruv natijasi: `docs/tekshiruv-hisoboti.md`.
- Tanzil litsenziyasi: `data/TANZIL-LICENSE.txt`.

## Ishga tushirish
Istalgan statik server: `python3 -m http.server` va brauzerda `http://localhost:8000`.

## Ma'lumotni qayta yig'ish
`tools/build_data.py` — Tanzil va QuranEnc fayllaridan `data/` ni yaratadi.
`tools/verify_arabic.py` — ikki manbani harfma-harf solishtiradi.
