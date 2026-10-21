"""MedMentor AI: tekshiruv. Kalitlarni ekranga chiqarmaydi."""
import asyncio
import os
import sys

from dotenv import load_dotenv
from anthropic import AsyncAnthropic, AuthenticationError, NotFoundError, RateLimitError, APIStatusError
from aiogram import Bot

load_dotenv()
token = os.getenv("BOT_TOKEN", "").strip()
api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
model = os.getenv("AI_MODEL", "claude-sonnet-5-5").strip()

async def main():
    if not token or not api_key:
        print("XATO: .env ichida BOT_TOKEN va ANTHROPIC_API_KEY to'ldirilishi kerak.")
        return 1

    try:
        bot = Bot(token=token)
        try:
            me = await bot.get_me()
            print("TELEGRAM: OK — @" + (me.username or "bot"))
        finally:
            await bot.session.close()
    except Exception as exc:
        print("TELEGRAM: XATO — " + type(exc).__name__)
        return 1

    client = AsyncAnthropic(api_key=api_key, timeout=25.0, max_retries=0)
    try:
        result = await client.messages.create(
            model=model,
            max_tokens=32,
            messages=[{"role": "user", "content": "Salom deb javob bering."}],
        )
        print("CLAUDE: OK — " + model)
        print("JAVOB: " + " ".join(getattr(block, "text", "") for block in result.content)[:140])
        return 0
    except AuthenticationError:
        print("CLAUDE: 401 — API kalit yaroqsiz; yangi kalit yarating.")
    except NotFoundError:
        print("CLAUDE: 404 — model yo'q yoki hisobingizda mavjud emas: " + model)
    except RateLimitError:
        print("CLAUDE: 429 — balans/limit/rate limit muammosi.")
    except APIStatusError as exc:
        print("CLAUDE: HTTP " + str(exc.status_code) + " — Anthropic Console sozlamalarini tekshiring.")
    except Exception as exc:
        print("CLAUDE: " + type(exc).__name__ + " — internet/tarmoqni tekshiring.")
    finally:
        await client.close()
    return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
