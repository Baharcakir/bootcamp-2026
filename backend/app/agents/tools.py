"""Koç uzmanlarının kullandığı araçlar; tüm iş mantığı services/ katmanındadır."""

from datetime import date
import json

from langchain_core.tools import tool
from sqlmodel import Session

from ..db import engine
from ..models import Student
from ..services.mastery import estimate_mastery, study_priorities
from ..services.planner import (
    generate_and_save_weekly_plan,
    get_latest_weekly_plan,
    plan_to_markdown,
)
from ..services.queries import load_exam_nets, load_observations, load_topic_weights
from ..services.trajectory import net_trend


@tool
def ogrenci_profili(student_id: int) -> str:
    """Öğrencinin adını, hedefini, sınav tarihini ve haftalık çalışma saatini döndürür."""
    with Session(engine) as session:
        student = session.get(Student, student_id)
        if not student:
            return "Öğrenci bulunamadı."
        parts = [
            f"Ad: {student.name}",
            f"Haftalık çalışma bütçesi: {student.weekly_hours} saat",
        ]
        if student.goal:
            parts.append(f"Hedef: {student.goal}")
        if student.exam_date:
            kalan = (student.exam_date - date.today()).days
            parts.append(f"Sınav tarihi: {student.exam_date} (kalan {kalan} gün)")
        return " | ".join(parts)


@tool
def konu_analizi(student_id: int) -> str:
    """Konu bazlı ustalıkları ve öncelikli çalışılacak konuları döndürür."""
    with Session(engine) as session:
        observations = load_observations(session, student_id)
        if not observations:
            return (
                "Henüz soru/quiz sinyali yok. Öğrenciden çözemediği soruları "
                "'Soru Sor' ekranından göndermesini iste."
            )
        masteries = estimate_mastery(observations)
        ranked = study_priorities(masteries, load_topic_weights())
        lines = ["Öncelikli çalışılacak konular:"]
        for mastery, score in ranked[:5]:
            lines.append(
                f"- {mastery.subject}/{mastery.topic}: ustalık %{mastery.mastery * 100:.0f}, "
                f"öncelik {score:.2f}"
            )
        strong = sorted(masteries, key=lambda item: item.ci_low, reverse=True)[:3]
        lines.append("Güçlü konular: " + ", ".join(item.topic for item in strong))
        return "\n".join(lines)


@tool
def net_gidisati(student_id: int) -> str:
    """Deneme netlerinin gidişatını ve bir sonraki deneme tahminini döndürür."""
    with Session(engine) as session:
        nets = load_exam_nets(session, student_id)
        if not nets:
            return "Henüz deneme verisi yok."
        trend = net_trend(nets)
        history = ", ".join(
            f"{exam.name} ({exam.taken_on}): {exam.net:.1f} net" for exam in trend.history
        )
        return (
            f"Denemeler: {history}. Haftalık eğilim: {trend.slope_per_week:+.1f} net/hafta. "
            f"Bir sonraki deneme tahmini: {trend.predicted_next:.1f} net."
        )


@tool
def haftalik_plan_olustur(student_id: int) -> str:
    """Öğrenci için haftalık plan üretir, veritabanına kaydeder ve JSON döndürür."""
    with Session(engine) as session:
        plan = generate_and_save_weekly_plan(session, student_id)
        return json.dumps(plan.model_dump(mode="json"), ensure_ascii=False)


@tool
def son_haftalik_plan(student_id: int) -> str:
    """Öğrencinin veritabanındaki son aktif haftalık planını döndürür."""
    with Session(engine) as session:
        plan = get_latest_weekly_plan(session, student_id)
        return plan_to_markdown(plan) if plan else "Henüz kaydedilmiş haftalık plan yok."
