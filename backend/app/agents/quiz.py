"""T3 — Quiz üretimi: anlatılan/zayıf konudan doğrulanmış benzer soru üretir.

Doğrulama protokolü: üretilen soru, cevabını görmeyen bağımsız ikinci bir model çağrısıyla
çözdürülür; çözücünün cevabı üreticinin cevabıyla uyuşmazsa soru elenir ve bir kez yeniden
denenir. Böylece öğrenciye hatalı cevap anahtarı gösterme riski azaltılır.

GOOGLE_API_KEY tanımlı değilse veya üretim başarısız olursa konu-bazlı fallback mekanizması çalışır.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..config import settings

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 2

# API_KEY yokken veya üretim başarısız olursa gösterilecek 5 şıklı konu-bazlı fallback'ler.
_FALLBACK: dict[str, dict] = {
    "default": {
        "soru": "Bir sınıftaki öğrencilerin %40'ı kız, %60'ı erkektir. Sınıfta 30 öğrenci varsa kaç kız öğrenci vardır?",
        "secenekler": {"A": "10", "B": "12", "C": "15", "D": "18", "E": "20"},
        "dogru": "B",
        "cozum": "30 × 0.40 = 12 kız öğrenci.",
    },
    "Problemler": {
        "soru": "Ali'nin yaşı Veli'nin yaşının 3 katından 5 eksiktir. Veli 10 yaşındaysa Ali kaç yaşındadır?",
        "secenekler": {"A": "25", "B": "30", "C": "35", "D": "40", "E": "45"},
        "dogru": "A",
        "cozum": "Ali = 3 × 10 − 5 = 25.",
    },
    "Olasılık": {
        "soru": "Bir torbada 3 kırmızı, 2 mavi top var. Rastgele çekilen topun kırmızı olma olasılığı nedir?",
        "secenekler": {"A": "1/5", "B": "2/5", "C": "3/5", "D": "4/5", "E": "1"},
        "dogru": "C",
        "cozum": "3 kırmızı / 5 toplam = 3/5.",
    },
    "Çember ve Daire": {
        "soru": "Yarıçapı 7 cm olan bir dairenin alanı kaç cm²'dir? (π ≈ 22/7)",
        "secenekler": {"A": "44", "B": "88", "C": "132", "D": "154", "E": "176"},
        "dogru": "D",
        "cozum": "Alan = π × r² = (22/7) × 49 = 154 cm².",
    },
}

GENERATE_PROMPT = """Sen TYT Matematik soru yazarısın. "{topic}" konusundan, gerçek TYT tarzında
(gerçek hayat bağlamlı, orta zorlukta, 5 şıklı) YENİ bir soru yaz.

Kurallar:
- Soru yalnızca "{topic}" konusunun tekniğiyle çözülmeli.
- Şıklardan tam olarak biri doğru olmalı; çeldiriciler makul olmalı.
- Sayılar temiz seçilmeli (sonuç tam sayı ya da basit kesir).
- LaTeX kullanma; düz metin yaz (üs için ^ kullanabilirsin).

Cevabını SADECE şu JSON biçiminde ver:
{{"soru": "...", "secenekler": {{"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."}},
"dogru": "C", "cozum": "adım adım kısa çözüm"}}"""

SOLVE_PROMPT = """Aşağıdaki 5 şıklı TYT Matematik sorusunu çöz ve yalnızca doğru şıkkın harfini ver.

Soru: {soru}
Şıklar:
{secenekler}

Cevabını SADECE şu JSON biçiminde ver: {{"cevap": "C"}}"""


@dataclass(frozen=True)
class Quiz:
    soru: str
    secenekler: dict[str, str]
    dogru: str
    cozum: str
    konu: str
    is_fallback: bool = False


def _llm(temperature: float, google_api_key: str | None = None) -> ChatGoogleGenerativeAI:
    api_key = google_api_key or settings.google_api_key
    model = settings.gemini_model or "gemini-2.5-flash"
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
    )


def _parse_json(reply: str) -> dict:
    cleaned = reply.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").removeprefix("json").strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


def _ask(llm: ChatGoogleGenerativeAI, prompt: str) -> dict:
    reply = llm.invoke([HumanMessage(content=prompt)]).content
    return _parse_json(reply if isinstance(reply, str) else str(reply))


def _fallback(topic: str) -> Quiz:
    data = _FALLBACK.get(topic, _FALLBACK["default"])
    return Quiz(
        soru=data["soru"],
        secenekler=data["secenekler"],
        dogru=data["dogru"],
        cozum=data["cozum"],
        konu=topic,
        is_fallback=True,
    )


def generate_quiz(topic: str, google_api_key: str | None = None) -> Quiz:
    """Konudan soru üretir; bağımsız çözücü doğrulamasından geçemeyen soruyu eler.

    GOOGLE_API_KEY tanımlı değilse doğrudan mock/fallback soru döner.
    """
    api_key = google_api_key or settings.google_api_key
    if not api_key:
        logger.info("GOOGLE_API_KEY tanımlı değil; fallback quiz sorusu kullanılıyor.")
        return _fallback(topic)

    last_error = "üretim başarısız"
    for _ in range(MAX_ATTEMPTS):
        try:
            llm_gen = _llm(temperature=0.8, google_api_key=api_key)
            uretim = _ask(llm_gen, GENERATE_PROMPT.format(topic=topic))
            secenekler = uretim.get("secenekler") or {}
            dogru = str(uretim.get("dogru", "")).strip().upper()
            if not uretim.get("soru") or dogru not in secenekler or len(secenekler) != 5:
                last_error = "üretilen soru biçimsiz veya şık sayısı 5 değil"
                continue

            # Bağımsız doğrulama: çözücü, üreticinin cevabını görmez.
            sec_metni = "\n".join(f"{h}) {m}" for h, m in sorted(secenekler.items()))
            llm_solv = _llm(temperature=0, google_api_key=api_key)
            cozucu = _ask(
                llm_solv,
                SOLVE_PROMPT.format(soru=uretim["soru"], secenekler=sec_metni),
            )
            if str(cozucu.get("cevap", "")).strip().upper() == dogru:
                return Quiz(
                    soru=uretim["soru"],
                    secenekler=dict(sorted(secenekler.items())),
                    dogru=dogru,
                    cozum=uretim.get("cozum", ""),
                    konu=topic,
                    is_fallback=False,
                )
            last_error = "doğrulama uyuşmadı (üretici ile çözücü farklı cevap verdi)"
        except Exception as exc:
            last_error = f"LLM hatası: {exc}"

    logger.warning("Quiz üretimi başarısız (%s); fallback kullanılıyor.", last_error)
    return _fallback(topic)
