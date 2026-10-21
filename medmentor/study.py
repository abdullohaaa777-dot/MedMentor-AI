"""Medical study exercises using Claude, no unsafe eval or executable AI output."""
from __future__ import annotations
import json
import re
from typing import Any

from anthropic import AsyncAnthropic


def parse_quiz(text: str) -> list[dict[str, Any]]:
    text = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", text.strip())
    obj = json.loads(text)
    items = obj.get("questions", [])
    valid = []
    for q in items[:10]:
        if not isinstance(q, dict):
            continue
        opts = q.get("options", [])
        answer = q.get("answer")
        if (
            isinstance(q.get("question"), str)
            and isinstance(opts, list) and len(opts) == 4
            and all(isinstance(o, str) and o.strip() for o in opts)
            and type(answer) is int and 0 <= answer <= 3
        ):
            valid.append({
                "question": q["question"][:700],
                "options": [x[:300] for x in opts],
                "answer": answer,
                "explanation": str(q.get("explanation", "Javobni darslikdan tekshiring."))[:1000],
            })
    if not valid:
        raise ValueError("Claude to'g'ri test JSON qaytarmadi")
    return valid


async def make_quiz(client: AsyncAnthropic, model: str, source: str) -> list[dict]:
    system = (
        "Siz tibbiyot o'qituvchisisiz. Faqat JSON obyekti qaytaring, markdown yo'q. "
        "Format: {\"questions\":[{\"question\":\"...\",\"options\":[\"A\",\"B\",\"C\",\"D\"],"
        "\"answer\":0,\"explanation\":\"...\"}]}. "
        "5 ta klinik jihatdan aniq savol tuzing. answer 0..3, bittasi to'g'ri. "
        "O'zbek tilida yozing. Materialda yo'q faktlarni ma'lum fakt deb ko'rsatmang."
    )
    rsp = await client.messages.create(
        model=model, max_tokens=2500, system=system,
        messages=[{"role": "user", "content": source[:18000]}]
    )
    text = "\n".join(getattr(x, "text", "") for x in rsp.content)
    return parse_quiz(text)


async def create_case(client: AsyncAnthropic, model: str, subject: str) -> str:
    prompt = (
        "Tibbiy talaba uchun virtual bemor/OSKE klinik holatini yarating. "
        "Ismi (xayoliy), yoshi, shikoyati, anamnez va ko'rik natijalari bo'lsin. "
        "Tashxisni darhol aytmang. Oxirida talabadan tashxis, tekshiruv va davolash "
        "rejasini so'rang. Barchasi o'zbek tilida, ixcham. Mavzu: " + subject[:800]
    )
    rsp = await client.messages.create(model=model, max_tokens=1400,
       messages=[{"role": "user", "content":prompt}])
    return "\n".join(getattr(x, "text", "") for x in rsp.content)


def extract_file(filename: str, blob: bytes) -> str:
    if len(blob) > 12 * 1024 * 1024:
        raise ValueError("Fayl 12 MB dan katta")
    name = filename.lower()
    from io import BytesIO
    if name.endswith(".pdf"):
        import pymupdf
        doc = pymupdf.open(stream=blob, filetype="pdf")
        try:
            return "\n".join(p.get_text() for p in list(doc)[:45])[:45000]
        finally:
            doc.close()
    if name.endswith(".docx"):
        from docx import Document
        d = Document(BytesIO(blob))
        return "\n".join(p.text for p in d.paragraphs)[:45000]
    if name.endswith(".txt"):
        return blob.decode("utf-8-sig", errors="replace")[:45000]
    raise ValueError("PDF, DOCX yoki TXT yuboring")
