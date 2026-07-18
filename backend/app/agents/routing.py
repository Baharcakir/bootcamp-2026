from __future__ import annotations

import re
import unicodedata
from typing import Literal

from pydantic import BaseModel, Field

RouteName = Literal["analyst", "planner", "tutor"]


class RoutingDecision(BaseModel):
    route: RouteName
    confidence: float = Field(ge=0, le=1)
    reason: str


def _normalize(text: str) -> str:
    text = text.casefold().replace("ı", "i")
    text = unicodedata.normalize("NFKD", text)
    return "".join(char for char in text if not unicodedata.combining(char))


def _contains(text: str, phrases: tuple[str, ...]) -> list[str]:
    return [phrase for phrase in phrases if re.search(rf"\b{re.escape(phrase)}\b", text)]


def classify_intent(message: str) -> RoutingDecision:
    """Koordinatörün test edilebilir, LLM'siz yönlendirme kararı.

    Plan üretimi veri yazdığı için kritik rota deterministik tutulur. Bu sayede model
    değişse bile "bu hafta ne çalışayım?" isteği yanlış uzmana gitmez.
    """

    text = _normalize(message.strip())
    if not text:
        return RoutingDecision(route="tutor", confidence=1.0, reason="Boş/generic mesaj")

    planner_phrases = (
        "bu hafta ne calisayim",
        "haftalik plan",
        "calisma plani",
        "program hazirla",
        "program yap",
        "plan olustur",
        "ders programi",
        "saat butcesi",
        "hangi gun",
        "ne calismaliyim",
    )
    analyst_phrases = (
        "nerelerde zayifim",
        "zayif konular",
        "konu analizi",
        "net gidisati",
        "netlerim",
        "performansim",
        "durumum",
        "analiz et",
        "guclu konular",
        "gelisimim",
    )
    tutor_phrases = (
        "anlat",
        "nasil cozulur",
        "nasil cozerim",
        "ogret",
        "ornek ver",
        "neden",
        "soru cozum",
        "konuyu acikla",
    )

    planner_hits = _contains(text, planner_phrases)
    analyst_hits = _contains(text, analyst_phrases)
    tutor_hits = _contains(text, tutor_phrases)

    # Plan fiilleri, haftalık ifade içermese de planlayıcıyı kesinleştirir.
    if planner_hits or re.search(r"\b(plan|program)\b", text):
        reason = planner_hits[0] if planner_hits else "plan/program anahtar sözcüğü"
        return RoutingDecision(route="planner", confidence=0.98, reason=reason)
    if analyst_hits:
        return RoutingDecision(route="analyst", confidence=0.95, reason=analyst_hits[0])
    if tutor_hits:
        return RoutingDecision(route="tutor", confidence=0.92, reason=tutor_hits[0])

    # Tek sözcüklü daha gevşek sinyaller.
    scores: dict[RouteName, int] = {
        "planner": sum(word in text for word in ("hafta", "calis", "takvim", "gun")),
        "analyst": sum(word in text for word in ("zayif", "net", "analiz", "basari", "ustalik")),
        "tutor": sum(word in text for word in ("soru", "konu", "coz", "acikla", "matematik")),
    }
    route = max(scores, key=scores.get)
    if scores[route] == 0:
        route = "tutor"
        return RoutingDecision(route=route, confidence=0.55, reason="Genel koçluk/eğitmen isteği")
    return RoutingDecision(route=route, confidence=0.75, reason=f"Anahtar sözcük skoru: {scores}")
