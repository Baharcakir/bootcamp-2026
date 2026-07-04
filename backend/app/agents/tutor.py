"""Eğitmen servisi — ürünün çekirdek döngüsü (v1 kapsamı: TYT Matematik).

Öğrenci çözemediği sorunun fotoğrafını (veya metnini) gönderir; Gemini:
1. TYT Matematik kapsamındaysa soruyu adım adım anlatır,
2. Soruyu taksonomimizden bir konuyla OTOMATİK etiketler (öğrenci asla etiketlemez),
3. Tek cümlelik özet çıkarır (RAG, tekrar önerileri ve değerlendirme setleri için).

Kapsam dışı sorular (Türkçe, fen, sosyal, AYT'ye özgü ileri konular) kibarca yönlendirilir ve
sinyal olarak KAYDEDİLMEZ — harita yalnızca kapsam içi sinyallerle örülür.

Yol haritası:
- T2 (Sprint 2): anlatımı kazanım dokümanları + ÖSYM çıkmış sorularıyla temellendir (RAG).
- T3 (Sprint 2): anlatım sonrası benzer soru + mini quiz → başarı sinyali ustalığı günceller.
- T4 (Sprint 2): ÖSYM çıkmış sorularından etiketli değerlendirme seti; etiketleme doğruluğu raporu.
- T6 (Sprint 3): kendi konu sınıflandırıcımızı eğit (embedding + klasik ML), Gemini ile karşılaştır.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..config import settings
from ..services.queries import tutor_topic_index

OUT_OF_SCOPE = "Kapsam Dışı"

TUTOR_PROMPT = """Sen deneyimli ve sabırlı bir TYT Matematik eğitmenisin. Öğrenci çözemediği bir
soru gönderdi. Çarpan v1 yalnızca TYT Matematik (geometri dahil) kapsamında çalışır.

Görevlerin:
1. KAPSAM KONTROLÜ: Soru TYT Matematik/Geometri kapsamında değilse (Türkçe, fen, sosyal,
   yabancı dil ya da AYT'ye özgü ileri konular: türev, integral, logaritma, trigonometri...)
   anlatım yapma; "explanation" alanına kibarca şu an yalnızca TYT Matematik'te uzman olduğunu,
   diğer derslerin yolda olduğunu yaz. "subject" ve "topic" alanlarına "{out_of_scope}" koy.
2. Kapsam içindeyse soruyu adım adım, lise seviyesinde Türkçe anlat; sonucu açıkça ver.
   "Neden bu adımı attık" mantığını kur, öğrenciyi küçümseme.
3. Soruyu aşağıdaki konu listesinden TAM olarak bir konuyla etiketle (listede olmayan etiket
   uydurma); "subject" alanına "Matematik" yaz.
4. Soruyu bir cümleyle özetle ("question_summary").

Konu listesi (TYT Matematik):
{taxonomy}

Cevabını SADECE şu JSON biçiminde ver, başka hiçbir şey yazma:
{{"explanation": "...", "subject": "...", "topic": "...", "question_summary": "..."}}"""


@dataclass(frozen=True)
class TutorResult:
    explanation: str
    subject: str
    topic: str
    question_summary: str


def _taxonomy_text() -> str:
    lines = []
    for subject, topics in tutor_topic_index().items():
        lines.append(f"- {subject}: {', '.join(sorted(topics))}")
    return "\n".join(lines)


def _parse_reply(reply: str) -> dict:
    """Modelin cevabından JSON ayıklar; ```json çitlerini temizler, bozuksa güvenli düşüş yapar."""
    cleaned = reply.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict) and data.get("explanation"):
            return data
    except json.JSONDecodeError:
        pass
    # JSON gelmediyse anlatımı kaybetme; etiketi belirsiz bırak (kapsam dışı sayılır, kayıt düşmez).
    return {
        "explanation": reply,
        "subject": OUT_OF_SCOPE,
        "topic": OUT_OF_SCOPE,
        "question_summary": "",
    }


def explain_question(
    image_bytes: bytes | None, mime_type: str | None, text: str | None
) -> TutorResult:
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.2,
    )
    prompt = TUTOR_PROMPT.format(taxonomy=_taxonomy_text(), out_of_scope=OUT_OF_SCOPE)
    content: list[dict] = [{"type": "text", "text": prompt}]
    if text:
        content.append({"type": "text", "text": f"Öğrencinin sorusu/notu: {text}"})
    if image_bytes:
        data_uri = (
            f"data:{mime_type or 'image/jpeg'};base64,"
            + base64.b64encode(image_bytes).decode()
        )
        content.append({"type": "image_url", "image_url": {"url": data_uri}})

    reply = llm.invoke([HumanMessage(content=content)]).content
    data = _parse_reply(reply if isinstance(reply, str) else str(reply))
    return TutorResult(
        explanation=data.get("explanation", ""),
        subject=data.get("subject", OUT_OF_SCOPE),
        topic=data.get("topic", OUT_OF_SCOPE),
        question_summary=data.get("question_summary", ""),
    )
