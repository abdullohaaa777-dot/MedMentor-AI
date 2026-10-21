# MedMentor AI — Claude API Telegram bot

Bu repository MedMentor AI botining **maxfiy** kod bazasi uchun yaratilgan.

## Xavfsizlik
- **BOT_TOKEN** va **ANTHROPIC_API_KEY** ni GitHub'ga joylamang.
- Maxfiy qiymatlar uchun lokal `.env` yoki hosting secrets'dan foydalaning.
- `.gitignore` ushbu fayllarni Git tarixiga tushishdan saqlaydi (ilgari commit qilingan kalitlarni himoya qilmaydi).

## Loyihani yuklash
Claude versiyasi ZIP arxividan **faqat dastur fayllarini** repositoryga yuklang.
`.env`, `.venv`, `data/`, `__pycache__/` va shaxsiy ma'lumotlarni yuklamang.

## Ishga tushirish (Windows)
1. Python 3.13 ni o'rnating.
2. `setup_windows.bat` ni ishga tushiring.
3. `.env.example` dan `.env` yarating va o'zingizning tokenlaringizni kiriting.
4. `run_bot.bat` ni ishga tushiring.

> GitHub'ga kod yuklanishi botni avtomatik 24/7 ishga tushirmaydi. Buning uchun hosting kerak.
> Claude API modelining mavjudligi va billing holatini Anthropic Console'da tekshiring.

**Status:** Dastlabki xavfsiz repository sozlamalari kiritilgan; botning to'liq manba kodi hali yuklanmagan.
