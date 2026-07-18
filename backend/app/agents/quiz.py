"""T3 — Quiz üretimi: anlatılan/zayıf konudan doğrulanmış benzer soru üretir.

Doğrulama protokolü (veri protokolümüzle aynı ilke): üretilen soru, cevabını görmeyen
bağımsız ikinci bir model çağrısıyla çözdürülür; çözücünün cevabı üreticinin cevabıyla
uyuşmazsa soru elenir ve bir kez yeniden denenir. Böylece öğrenciye hatalı cevap anahtarı
gösterme riski azaltılır.

Öğrencinin quiz sonucu mevcut `POST /students/{id}/events` ucuna `source="quiz"` ile
gönderilir; doğru cevap ustalık haritasını YUKARI günceller (döngü burada kapanır).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..config import settings

MAX_ATTEMPTS = 2

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


def _llm(temperature: float) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model, google_api_key=settings.google_api_key,
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


def generate_quiz(topic: str) -> Quiz:
    """Konudan soru üretir; bağımsız çözücü doğrulamasından geçemeyen soruyu eler."""
    last_error = "üretim başarısız"
    for _ in range(MAX_ATTEMPTS):
        uretim = _ask(_llm(temperature=0.8), GENERATE_PROMPT.format(topic=topic))
        secenekler = uretim.get("secenekler") or {}
        dogru = str(uretim.get("dogru", "")).strip().upper()
        if not uretim.get("soru") or dogru not in secenekler or len(secenekler) != 5:
            last_error = "üretilen soru biçimsiz"
            continue

        # Bağımsız doğrulama: çözücü, üreticinin cevabını görmez.
        sec_metni = "\n".join(f"{h}) {m}" for h, m in sorted(secenekler.items()))
        cozucu = _ask(
            _llm(temperature=0),
            SOLVE_PROMPT.format(soru=uretim["soru"], secenekler=sec_metni),
        )
        if str(cozucu.get("cevap", "")).strip().upper() == dogru:
            return Quiz(
                soru=uretim["soru"], secenekler=dict(sorted(secenekler.items())),
                dogru=dogru, cozum=uretim.get("cozum", ""), konu=topic,
            )
        last_error = "doğrulama uyuşmadı (üretici ile çözücü farklı cevap verdi)"
    raise RuntimeError(f"Quiz üretilemedi: {last_error}")
