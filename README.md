# MedMentor AI — Claude Telegram bot

**Status:** Minimal Claude Telegram bot kodi GitHub'ga joylangan. Haqiqiy Claude/Telegram API bilan sinov hali o'tkazilmagan.

## Hozir mavjud
- Claude bilan tibbiy savol-javob
- JPEG/PNG rasm tahlili
- 5 tushuntirish uslubi va Telegram HTML
- FastAPI /health endpoint

**Hali mavjud emas:** o'qituvchi testlarini yuklash, virtual bemor, obuna, audio/video transkripsiya, ovozli javob va to'liq interaktiv Mini App.

## Windowsda o'rnatish
1. Repositoryni ZIP qilib yuklab, arxivdan chiqaring.
2. Python 3.13 bilan setup_windows.bat ni ishga tushiring.
3. Lokal .env faylga YANGI BOT_TOKEN va ANTHROPIC_API_KEY kiriting.
4. AI_MODEL qiymatini Anthropic hisobingizda mavjud model ID siga sozlang.
5. run_bot.bat ni faqat bir marta ishga tushiring.
6. Telegramda /start, matn va rasm bilan sinang.

## Xavfsizlik
Ilgari .env tasodifan commit qilingan. U hozirgi main tarmog'idan o'chirilgan, biroq eski Git tarixida qolishi mumkin. Oldingi bot tokeni va Claude API kalitini bekor qilib yangilang. Sirlarni GitHub'ga yuklamang.

GitHub Actions testlari haqiqiy Telegram/Claude API ishlashini tasdiqlamaydi. 24/7 ishlash uchun hosting kerak.

Docker bot: docker compose up --build -d bot
