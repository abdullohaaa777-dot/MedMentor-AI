"""MedMentor AI: Telegram medical tutor using Anthropic Claude."""
from __future__ import annotations

import asyncio
import io
import logging
import os
import re
from html import escape
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from anthropic import AsyncAnthropic, AnthropicError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("medmentor")
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
MODEL = os.getenv("AI_MODEL", "").strip() or "claude-sonnet-4-5"
MODES = {
    "👨‍🏫 Professor": "Professor darajasida, chuqur fiziologik mexanizmlar va klinik misollar bilan",
    "🧒 Sodda": "10 yoshli bolaga sodda va tushunarli",
    "🧠 Mnemonika": "eslab qolishga qulay mnemonikalar bilan",
    "🩺 Klinik": "OSKE uslubida klinik holatlar bilan",
    "📘 Aralash": "ta'rif, mexanizm, klinik bog'liqlik va eslab qolish usullari bilan",
}
user_modes: dict[int, str] = {}
dp = Dispatcher()
client: AsyncAnthropic | None = None


def format_html(raw: str) -> list[str]:
    """Escape generated text before adding safe Telegram HTML."""
    raw = re.sub(r"\\rightarrow|\\to", "→", raw)
    raw = re.sub(r"\\alpha", "α", raw)
    raw = re.sub(r"\\beta", "β", raw)
    raw = raw.replace("G_i", "Gi").replace("G_s", "Gs")
    raw = raw.replace("$", "").replace("**", "").replace("`", "")
    lines = []
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            lines.append("")
            continue
        s = re.sub(r"^#{1,6}\s*", "", s)
        s = re.sub(r"^---+$", "──────────", s)
        safe = escape(s)
        if line.lstrip().startswith("#"):
            safe = "<b>" + safe + "</b>"
        lines.append(safe)
    text = "\n".join(lines).strip()
    parts = []
    while text:
        if len(text) <= 3300:
            parts.append(text)
            break
        cut = text.rfind("\n", 0, 3300)
        if cut < 600:
            cut = 3300
        parts.append(text[:cut])
        text = text[cut:].lstrip("\n")
    return parts or ["Javob bo‘sh."]


async def send_result(message: Message, result: str) -> None:
    for part in format_html(result):
        await message.answer(part)


async def ask_claude(prompt: str, mode: str, image: bytes | None = None) -> str:
    if client is None:
        raise RuntimeError("Claude client sozlanmagan")
    import base64
    blocks: list[dict] = [{"type": "text", "text": prompt[:16000]}]
    if image:
        blocks.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": base64.b64encode(image).decode("ascii"),
            },
        })
    system = (
        "Siz MedMentor AI tibbiyot o'qituvchisisiz. O'zbek tilida ilmiy to'g'ri, "
        "aniq va o'qilishi oson javob bering. Bemor uchun masofadan turib aniq "
        "tashxis qo'ymang. Zarur bo'lsa shifokorga yo'naltiring. "
        "Markdown/LaTeX matematik sintaksis ishlatmang; oddiy Unicode ishlating. "
        "Qisqa sarlavhalar va paragraflar qo'llang. O'qitish uslubi: " + mode
    )
    response = await client.messages.create(
        model=MODEL, max_tokens=1800, system=system,
        messages=[{"role": "user", "content": blocks}],
    )
    return "\n".join(x.text for x in response.content if x.type == "text").strip()


@dp.message(CommandStart())
async def start(message: Message):
    buttons = [[KeyboardButton(text=x)] for x in MODES]
    markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer(
        "🩺 <b>MedMentor AI</b>\n\nMenga tibbiyotga oid savol yoki rasm yuboring. "
        "Quyidan tushuntirish uslubini tanlang. /help — yordam.",
        reply_markup=markup,
    )


@dp.message(Command("help"))
async def help_message(message: Message):
    await message.answer(
        "📚 Matn yuboring — Claude tushuntiradi.\n"
        "🖼 Rasm yuboring — rasm mazmunini tahlil qiladi.\n"
        "🎓 Tugmalar — o'qitish uslubini tanlash.\n"
        "⚠️ Bot shifokor ko'rigi o'rnini bosmaydi."
    )


@dp.message(F.text.in_(list(MODES)))
async def switch_mode(message: Message):
    if message.from_user:
        user_modes[message.from_user.id] = message.text
    await message.answer("✅ Uslub tanlandi: " + escape(message.text or ""))


async def generate_reply(message: Message, prompt: str, image: bytes | None = None):
    mode_key = user_modes.get(message.from_user.id if message.from_user else 0, "📘 Aralash")
    try:
        await message.bot.send_chat_action(message.chat.id, "typing")
        answer = await ask_claude(prompt, MODES[mode_key], image)
        await send_result(message, answer or "Claude bo'sh javob qaytardi.")
    except AnthropicError as exc:
        logger.exception("Claude API error (%s)", type(exc).__name__)
        await message.answer(
            "⚠️ Claude API so'rovi bajarilmadi. Kalit, hisob balansi, model ruxsati "
            "va terminaldagi xato turini tekshiring."
        )
    except Exception:
        logger.exception("Unexpected bot error")
        await message.answer("⚠️ Xabarni qayta ishlashda xato. Terminal jurnalini tekshiring.")


@dp.message(F.photo)
async def on_photo(message: Message):
    try:
        from PIL import Image
        photo = message.photo[-1]
        data = io.BytesIO()
        await message.bot.download(photo, destination=data)
        data.seek(0)
        with Image.open(data) as img:
            img = img.convert("RGB")
            img.thumbnail((1536, 1536))
            out = io.BytesIO()
            img.save(out, "JPEG", quality=85)
        await generate_reply(message, message.caption or "Rasmda nima tasvirlangan? Tibbiy jihatdan sharhlang.", out.getvalue())
    except Exception:
        logger.exception("Image decode error")
        await message.answer("⚠️ Rasmni o'qib bo'lmadi. JPEG yoki PNG yuboring.")


@dp.message(F.text)
async def on_text(message: Message):
    if not message.text or message.text.startswith("/"):
        return
    await generate_reply(message, message.text)


@dp.message()
async def other(message: Message):
    await message.answer("Hozir ushbu versiyada matn va rasm qabul qilinadi. Audio, video va hujjat modullari hali ulanmagan.")


async def main():
    global client
    if not BOT_TOKEN or not API_KEY:
        raise RuntimeError("BOT_TOKEN va ANTHROPIC_API_KEY .env ichida bo'lishi shart")
    logging.basicConfig(level=logging.INFO)
    client = AsyncAnthropic(api_key=API_KEY, timeout=60.0, max_retries=1)
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    logger.info("MedMentor AI Claude online: %s", MODEL)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
