"""Quiz sorusu üretici — Sprint 2 T3.

Belirtilen konu için Gemini ile 4 şıklı bir alıştırma sorusu üretir.
GOOGLE_API_KEY yoksa veya LLM hatası olursa statik fallback soru döner
(demo/key-yok senaryosunda arayüz yine çalışır).

Yol haritası:
- T3 (Sprint 2): AI üretimi soruların doğrulama süzgeci (yanıt tutarlılığı).
- T6 (Sprint 3): ÖSYM çıkmış sorulardan gerçek quiz bankası.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# API_KEY yokken veya üretim başarısız olursa gösterilecek konu-bağımsız fallback.
_FALLBACK: dict[str, dict] = {
    "default": {
        "question": "Bir sınıftaki öğrencilerin %40'ı kız, %60'ı erkektir. Sınıfta 30 öğrenci varsa kaç kız öğrenci vardır?",
        "choices": ["A) 10", "B) 12", "C) 15", "D) 18"],
        "answer_index": 1,
        "explanation": "30 × 0.40 = 12 kız öğrenci.",
    },
    "Problemler": {
        "question": "Ali'nin yaşı Veli'nin yaşının 3 katından 5 eksiktir. Veli 10 yaşındaysa Ali kaç yaşındadır?",
        "choices": ["A) 25", "B) 30", "C) 35", "D) 40"],
        "answer_index": 0,
        "explanation": "Ali = 3 × 10 − 5 = 25.",
    },
    "Olasılık": {
        "question": "Bir torbada 3 kırmızı, 2 mavi top var. Rastgele çekilen topun kırmızı olma olasılığı nedir?",
        "choices": ["A) 1/5", "B) 2/5", "C) 3/5", "D) 4/5"],
        "answer_index": 2,
        "explanation": "3 kırmızı / 5 toplam = 3/5.",
    },
    "Çember ve Daire": {
        "question": "Yarıçapı 7 cm olan bir dairenin alanı kaç cm²'dir? (π ≈ 22/7)",
        "choices": ["A) 44", "B) 154", "C) 132", "D) 176"],
        "answer_index": 1,
        "explanation": "Alan = π × r² = (22/7) × 49 = 154 cm².",
    },
}

QUIZ_PROMPT = """Sen bir TYT Matematik soru yazarısın.
Konu: {topic}

Bu konuyla ilgili, TYT zorluk düzeyinde, 4 şıklı (A, B, C, D) tek doğru cevaplı bir soru yaz.
Soruyu SADECE aşağıdaki JSON biçiminde ver, başka hiçbir şey yazma:

{{
  "question": "Soru metni buraya",
  "choices": ["A) ...", "B) ...", "C) ...", "D) ..."],
  "answer_index": 0,
  "explanation": "Kısa çözüm açıklaması"
}}

Kurallar:
- answer_index 0-3 arası tam sayı (hangi şıkkın doğru olduğu)
- Açıklama 1-2 cümle, adım adım
- Soru net ve özgün olsun
"""


@dataclass(frozen=True)
class QuizQuestion:
    topic: str
    question: str
    choices: list[str]
    answer_index: int
    explanation: str
    is_fallback: bool = False  # True ise AI üretmedi, statik fallback kullanıldı


def _fallback(topic: str) -> QuizQuestion:
    data = _FALLBACK.get(topic, _FALLBACK["default"])
    return QuizQuestion(
        topic=topic,
        question=data["question"],
        choices=data["choices"],
        answer_index=data["answer_index"],
        explanation=data["explanation"],
        is_fallback=True,
    )


def generate_quiz_question(topic: str, google_api_key: str | None) -> QuizQuestion:
    """Verilen konu için quiz sorusu üretir.

    API key yoksa veya üretim hata verirse konu-bazlı statik fallback döner —
    arayüz her koşulda çalışmaya devam eder.
    """
    if not google_api_key:
        logger.info("GOOGLE_API_KEY tanımlı değil; fallback quiz sorusu kullanılıyor.")
        return _fallback(topic)

    try:
        from langchain_core.messages import HumanMessage
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key,
            temperature=0.7,
        )
        prompt = QUIZ_PROMPT.format(topic=topic)
        reply = llm.invoke([HumanMessage(content=prompt)]).content
        if not isinstance(reply, str):
            reply = str(reply)

        # JSON temizle
        cleaned = reply.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").removeprefix("json").strip()

        data = json.loads(cleaned)
        choices = data.get("choices", [])
        answer_index = int(data.get("answer_index", 0))

        if not data.get("question") or len(choices) != 4 or not (0 <= answer_index <= 3):
            raise ValueError("Geçersiz quiz yapısı")

        return QuizQuestion(
            topic=topic,
            question=data["question"],
            choices=choices,
            answer_index=answer_index,
            explanation=data.get("explanation", ""),
            is_fallback=False,
        )
    except Exception as exc:
        logger.warning("Quiz üretimi başarısız (%s); fallback kullanılıyor.", exc)
        return _fallback(topic)
