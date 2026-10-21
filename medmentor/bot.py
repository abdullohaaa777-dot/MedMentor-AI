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
from .study import make_quiz, create_case, extract_file

load_dotenv()
logger = logging.getLogger("medmentor")
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
MODEL = os.getenv("AI_MODEL", "").strip() or "claude-sonnet-5-5"
MODES = {
    "👨‍🏫 Professor": "Professor darajasida, chuqur fiziologik mexanizmlar va klinik misollar bilan",
    "🧒 Sodda": "10 yoshli bolaga sodda va tushunarli",
    "🧠 Mnemonika": "eslab qolishga qulay mnemonikalar bilan",
    "🩺 Klinik": "OSKE uslubida klinik holatlar bilan",
    "📘 Aralash": "ta'rif, mexanizm, klinik bog'liqlik va eslab qolish usullari bilan",
}
user_modes: dict[int, str] = {}
user_quizzes: dict[int, dict] = {}
user_cases: dict[int, str] = {}
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
        "🧩 /quiz kardiologiya — 5 ta test.\n"
        "🩺 /case terapiya — OSKE mashqi.\n"
        "📄 PDF, DOCX yoki TXT yuklang — test tuziladi.\n"
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



@dp.message(Command("quiz"))
async def quiz_start(message: Message):
    uid = message.from_user.id if message.from_user else 0
    topic = (message.text or "").partition(" ")[2].strip() or "Yurak fiziologiyasi"
    await message.answer("🧩 5 ta test tayyorlanyapti...")
    try:
        questions = await make_quiz(client, MODEL, topic)
        user_quizzes[uid] = {"questions": questions, "index": 0, "score": 0}
        await present_quiz(message, uid)
    except Exception:
        logger.exception("Quiz generation error")
        await message.answer("⚠️ Test yaratilmadi. API model, balans va terminal xatosini tekshiring.")


async def present_quiz(message: Message, uid: int):
    session = user_quizzes.get(uid)
    if not session:
        return
    idx = session["index"]
    if idx >= len(session["questions"]):
        await message.answer(f"🏆 Natija: {session['score']}/{len(session['questions'])} to'g'ri.")
        user_quizzes.pop(uid, None)
        return
    q = session["questions"][idx]
    options = "\n".join(f"{i+1}. {escape(x)}" for i, x in enumerate(q["options"]))
    await message.answer(f"🧩 <b>Savol {idx+1}/{len(session['questions'])}</b>\n{escape(q['question'])}\n\n{options}\n\nJavob uchun 1, 2, 3 yoki 4 yuboring.")


@dp.message(Command("case", "osce"))
async def case_start(message: Message):
    uid = message.from_user.id if message.from_user else 0
    topic = (message.text or "").partition(" ")[2].strip() or "Kardiologiya"
    await message.answer("🩺 Virtual bemor tayyorlanyapti...")
    try:
        scenario = await create_case(client, MODEL, topic)
        user_cases[uid] = scenario
        await send_result(message, scenario)
        await message.answer("Tashxis va rejangizni yozing; /finishcase bilan yakunlang.")
    except Exception:
        logger.exception("Case generation error")
        await message.answer("⚠️ Klinik vaziyatni yaratib bo'lmadi.")


@dp.message(Command("finishcase"))
async def case_end(message: Message):
    uid = message.from_user.id if message.from_user else 0
    user_cases.pop(uid, None)
    await message.answer("✅ Klinik vaziyat yakunlandi. /case bilan yangisini boshlang.")


@dp.message(F.document)
async def document_upload(message: Message):
    doc = message.document
    uid = message.from_user.id if message.from_user else 0
    if doc.file_size and doc.file_size > 12*1024*1024:
        await message.answer("⚠️ Maksimal fayl hajmi 12 MB.")
        return
    try:
        buffer = io.BytesIO()
        await message.bot.download(doc, destination=buffer)
        source = extract_file(doc.file_name or "", buffer.getvalue())
        if len(source.strip()) < 80:
            await message.answer("⚠️ Fayldan matn olinmadi. Skan PDF uchun OCR talab qilinadi.")
            return
        await message.answer("📄 Material o'qildi, 5 ta test tuzilmoqda...")
        questions = await make_quiz(client, MODEL, source)
        user_quizzes[uid] = {"questions": questions, "index": 0, "score": 0}
        await present_quiz(message, uid)
    except ValueError as exc:
        await message.answer("⚠️ " + escape(str(exc)))
    except Exception:
        logger.exception("Document quiz error")
        await message.answer("⚠️ Fayldan test tuzib bo'lmadi; terminalni tekshiring.")


@dp.message(F.text)
async def on_text(message: Message):
    if not message.text or message.text.startswith("/"):
        return
    uid = message.from_user.id if message.from_user else 0
    quiz = user_quizzes.get(uid)
    if quiz and message.text.strip() in ("1", "2", "3", "4"):
        idx = quiz["index"]
        q = quiz["questions"][idx]
        choice = int(message.text.strip())-1
        ok = choice == q["answer"]
        quiz["score"] += int(ok)
        quiz["index"] += 1
        await message.answer(("✅ To'g'ri!" if ok else "❌ Noto'g'ri.") + "\n" + escape(q["explanation"]))
        await present_quiz(message, uid)
        return
    if uid in user_cases:
        await generate_reply(message, "Quyidagi klinik vaziyatda talabaga diagnostik fikrlash bo'yicha xolis fikr bildiring, xavfli tavsiyalar bermang.\nVaziyat: " + user_cases[uid] + "\nTalaba javobi: " + message.text)
        return
    await generate_reply(message, message.text)


@dp.message()
async def other(message: Message):
    await message.answer("Matn, rasm, PDF/DOCX/TXT va /quiz hamda /case ishlatiladi. Audio va video funksiyalari hali qo‘shilmagan.")


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
