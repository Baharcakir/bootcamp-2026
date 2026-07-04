"""Veritabanı sorguları ile analiz servisleri arasındaki köprü.

Hem API router'ları hem agent araçları bu modülü kullanır; iş mantığı tek yerde kalır.

Ustalık haritasının veri kaynağı QuestionEvent'lerdir (sorulan sorular, manuel işaretler,
quiz sonuçları) — öğrenci konu bazlı veri GİRMEZ, harita kullanımdan kendiliğinden birikir.
Deneme sonuçları (SubjectResult) yalnızca net gidişatını besler.
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlmodel import Session, select

from ..models import MockExam, QuestionEvent, SubjectResult
from .mastery import TopicObservation
from .trajectory import ExamNet, compute_net

TOPICS_PATH = Path(__file__).resolve().parents[1] / "data" / "topics_tyt.json"


def load_topics() -> dict:
    return json.loads(TOPICS_PATH.read_text(encoding="utf-8"))


def tutor_topic_index() -> dict[str, set[str]]:
    """Koçluk kapsamındaki (v1: TYT Matematik) ders → konu kümesi.

    Zayıflık haritası, eğitmen etiketlemesi ve manuel sinyaller yalnızca bu kapsamda
    çalışır; deneme neti girişi ise tüm dersleri kabul eder.
    """
    data = load_topics()
    scope = set(data.get("tutor_scope", []))
    return {s["name"]: set(s["topics"]) for s in data["subjects"] if s["name"] in scope}


def load_topic_weights() -> dict[tuple[str, str], float]:
    """Konu ağırlığı = dersin soru sayısı / dersteki konu sayısı (kaba sınav ağırlığı)."""
    weights: dict[tuple[str, str], float] = {}
    for subject in load_topics()["subjects"]:
        per_topic = subject["question_count"] / max(len(subject["topics"]), 1)
        for topic in subject["topics"]:
            weights[(subject["name"], topic)] = per_topic
    return weights


def load_observations(session: Session, student_id: int) -> list[TopicObservation]:
    """QuestionEvent'leri ustalık modelinin beklediği gözlemlere çevirir.

    Sorulan/çözülemeyen soru → başarısızlık sinyali; quiz doğrusu → başarı sinyali.
    Aynı gün + aynı konudaki sinyaller tek gözlemde toplanır.
    """
    events = session.exec(
        select(QuestionEvent).where(QuestionEvent.student_id == student_id)
    ).all()
    acc: dict[tuple[str, str, object], list[int]] = {}
    for event in events:
        key = (event.subject, event.topic, event.happened_on)
        cur = acc.setdefault(key, [0, 0])  # [başarı, başarısızlık]
        cur[0 if event.succeeded else 1] += 1
    return [
        TopicObservation(subject, topic, day, correct=success, wrong=failure, blank=0)
        for (subject, topic, day), (success, failure) in acc.items()
    ]


def load_exam_nets(session: Session, student_id: int) -> list[ExamNet]:
    exams = session.exec(select(MockExam).where(MockExam.student_id == student_id)).all()
    nets = []
    for exam in exams:
        results = session.exec(
            select(SubjectResult).where(SubjectResult.exam_id == exam.id)
        ).all()
        total_correct = sum(r.correct for r in results)
        total_wrong = sum(r.wrong for r in results)
        nets.append(ExamNet(exam.taken_on, exam.name, compute_net(total_correct, total_wrong)))
    return nets
