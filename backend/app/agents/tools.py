"""Koç agent'ının araçları — servis katmanını LLM'e açar.

Kural: araçlar veritabanına doğrudan SQL ile değil, services/ üzerinden erişir; iş mantığı
tek yerde kalır (bkz. docs/mimari.md).
"""

from datetime import date

from langchain_core.tools import tool
from sqlmodel import Session

from ..db import engine
from ..models import Student
from ..services.mastery import estimate_mastery, study_priorities
from ..services.queries import load_exam_nets, load_observations, load_topic_weights
from ..services.trajectory import net_trend


@tool
def ogrenci_profili(student_id: int) -> str:
    """Öğrencinin adını, hedefini, sınav tarihini ve haftalık çalışma saatini döndürür."""
    with Session(engine) as session:
        student = session.get(Student, student_id)
        if not student:
            return "Öğrenci bulunamadı."
        parts = [f"Ad: {student.name}", f"Haftalık çalışma bütçesi: {student.weekly_hours} saat"]
        if student.goal:
            parts.append(f"Hedef: {student.goal}")
        if student.exam_date:
            kalan = (student.exam_date - date.today()).days
            parts.append(f"Sınav tarihi: {student.exam_date} (kalan {kalan} gün)")
        return " | ".join(parts)


@tool
def konu_analizi(student_id: int) -> str:
    """Öğrencinin sorduğu sorulardan ve quiz sonuçlarından konu bazlı ustalık analizi yapar;
    öncelikli çalışılacak konuları ve güçlü konuları döndürür."""
    with Session(engine) as session:
        observations = load_observations(session, student_id)
    if not observations:
        return (
            "Henüz soru/quiz sinyali yok. Öğrenciden çözemediği soruların fotoğrafını "
            "'Soru Sor' ekranından göndermesini iste; harita kullandıkça oluşur."
        )

    masteries = estimate_mastery(observations)
    ranked = study_priorities(masteries, load_topic_weights())
    lines = ["Öncelikli çalışılacak konular (ağırlık × belirsizlik/zayıflık sırasıyla):"]
    for m, score in ranked[:5]:
        lines.append(
            f"- {m.subject} / {m.topic}: ustalık %{m.mastery * 100:.0f} "
            f"(güven aralığı %{m.ci_low * 100:.0f}–%{m.ci_high * 100:.0f}), öncelik {score:.2f}"
        )
    strong = sorted(masteries, key=lambda m: m.ci_low, reverse=True)[:3]
    lines.append("Güçlü konular: " + ", ".join(f"{m.subject}/{m.topic}" for m in strong))
    return "\n".join(lines)


@tool
def net_gidisati(student_id: int) -> str:
    """Öğrencinin deneme netlerinin zaman içindeki gidişatını ve bir sonraki deneme net
    tahminini döndürür."""
    with Session(engine) as session:
        nets = load_exam_nets(session, student_id)
    if not nets:
        return "Henüz deneme verisi yok."

    trend = net_trend(nets)
    history = ", ".join(f"{e.name} ({e.taken_on}): {e.net:.1f} net" for e in trend.history)
    return (
        f"Denemeler: {history}. Haftalık eğilim: {trend.slope_per_week:+.1f} net/hafta. "
        f"Bir sonraki deneme tahmini: {trend.predicted_next:.1f} net."
    )
