# MedMentor AI — Claude Telegram bot

## Holati
GitHub'ga Claude bilan ishlaydigan Telegram bot kodlari va avtomatik testlari joylangan.
Python CI va Docker build tekshiriladi; **haqiqiy Telegram/Claude ulanishi tokenlarsiz sinab bo'lmaydi**.

## Mavjud funksiyalar
- O'zbek tilida Claude bilan tibbiy savol-javob va 5 uslub
- Rasm (JPEG/PNG) tahlili
- `/quiz <mavzu>`: 5 savolli test, javob tekshirish
- `/case <mavzu>` yoki `/osce`: AI klinik vaziyat, savol-javob
- PDF, DOCX, TXT: matnni o'qish va 5 savolli test
- Telegramga mos xavfsiz HTML; `/help`
- `medmentor.check_connection`: haqiqiy API ulanishini tekshirish
- Docker bot xizmati va FastAPI /health

## Hali tayyor emas
- Audio/video transkripsiyasi, ovoz chiqarish, rasm generatsiyasi
- Saqlanadigan o'quv progressi va keng test banki (joriy mashqlar RAMda)
- Stars obuna, to'lov va tarif tekshiruvlari
- To'liq interaktiv Mini App, ko'p foydalanuvchili production infratuzilma
- Klinik natijalarni tibbiy ekspert validatsiyasi

## Windows 10, Python 3.13 — ketma-ket ishga tushirish
1. https://github.com/abdullohaaa777-dot/MedMentor-AI — **Code → Download ZIP**.
2. Arxivdan chiqaring. Ichida `run_bot.bat`, `medmentor/` ko'rinib turishi kerak.
3. Shu papkadagi `setup_windows.bat` faylini ishga tushiring va kuting.
4. Ochildigan lokal `.env` faylga `BOT_TOKEN` va `ANTHROPIC_API_KEY` uchun **yangilangan** kalitlarni kiriting.
5. `AI_MODEL=claude-sonnet-5-5` ni kiriting; Anthropic hisobingiz uchun ruxsatni tekshiring.
6. CMDda papkada `.venv\Scripts\python.exe -m medmentor.check_connection` buyrug'ini bajaring.
7. `TELEGRAM: OK` va `CLAUDE: OK` chiqsa `run_bot.bat` ni **bir marta** oching.
8. @Medicalteacher_bot da `/start`, `/quiz yurak fiziologiyasi`, `/case kardiologiya` yuboring, so'ng PDF/rasm bilan tekshiring.

## Muhim xavfsizlik
Ilgari `.env` Git tarixiga commit qilingan. Joriy tarmoqdan olib tashlangan bo'lsa ham, eski commitlar uni saqlashi mumkin. **Oldingi Telegram tokeni va Claude API kalitini bekor qilib yangilarini yarating.**
Yangi maxfiy qiymatlarni hech qachon GitHub'ga yozmang. `.gitignore` avvalgi tarixni tozalamaydi.

## Docker
`docker compose up --build -d bot` — faqat bot uchun. GitHub Actions botni 24/7 ishga tushirmaydi: alohida server yoki doim yoqilgan kompyuter kerak.
