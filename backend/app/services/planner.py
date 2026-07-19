from __future__ import annotations

import json
import math
from datetime import date, timedelta

from pydantic import BaseModel, Field
from sqlmodel import Session, select

from ..models import Student, StudyPlan, StudyPlanItem
from .mastery import estimate_mastery, study_priorities
from .queries import load_observations, load_topic_weights

DAY_NAMES = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
DEFAULT_TOPICS = [
    ("Matematik", "Problemler", 1.00),
    ("Matematik", "Temel Kavramlar", 0.92),
    ("Matematik", "Denklem Çözme", 0.88),
    ("Matematik", "Üslü Sayılar", 0.82),
    ("Matematik", "Köklü Sayılar", 0.80),
]
ACTIVITY_CYCLE = [
    "Konu özeti + çözümlü örnek",
    "Yeni nesil soru çözümü",
    "Mini quiz + yanlış analizi",
]


class PlanPriority(BaseModel):
    subject: str
    topic: str
    score: float = Field(ge=0)
    mastery: float | None = Field(default=None, ge=0, le=1)


class WeeklyPlanItemOut(BaseModel):
    position: int
    day_index: int
    day_name: str
    subject: str
    topic: str
    activity: str
    duration_minutes: int = Field(gt=0)
    rationale: str


class WeeklyPlanOut(BaseModel):
    id: int | None = None
    student_id: int
    week_start: date
    created_on: date
    exam_date: date | None
    weekly_hours: int
    total_minutes: int
    days_to_exam: int | None
    summary: str
    priorities: list[PlanPriority]
    items: list[WeeklyPlanItemOut]


def monday_of(day: date) -> date:
    return day - timedelta(days=day.weekday())


def _derived_priorities(session: Session, student_id: int, limit: int = 5) -> list[PlanPriority]:
    observations = load_observations(session, student_id)
    if not observations:
        return [
            PlanPriority(subject=subject, topic=topic, score=score, mastery=None)
            for subject, topic, score in DEFAULT_TOPICS[:limit]
        ]

    masteries = estimate_mastery(observations)
    ranked = study_priorities(masteries, load_topic_weights(), top=limit)
    return [
        PlanPriority(
            subject=mastery.subject,
            topic=mastery.topic,
            score=round(float(score), 4),
            mastery=round(float(mastery.mastery), 4),
        )
        for mastery, score in ranked
    ]


def _session_count(total_minutes: int) -> int:
    # Oturumları 45-90 dakika bandında tut; en az üç temas noktası üret.
    return max(3, min(14, math.ceil(total_minutes / 75)))


def _split_minutes(total_minutes: int, count: int) -> list[int]:
    base, remainder = divmod(total_minutes, count)
    return [base + (1 if i < remainder else 0) for i in range(count)]


def _weighted_topic_sequence(priorities: list[PlanPriority], count: int) -> list[PlanPriority]:
    scores = [max(p.score, 0.05) for p in priorities]
    total = sum(scores)
    quotas = [score / total * count for score in scores]
    allocated = [int(q) for q in quotas]

    while sum(allocated) < count:
        index = max(range(len(quotas)), key=lambda i: quotas[i] - allocated[i])
        allocated[index] += 1

    pool: list[PlanPriority] = []
    for priority, amount in zip(priorities, allocated, strict=True):
        pool.extend([priority] * amount)

    # Aynı konunun arka arkaya yığılmasını önleyen basit bir dağıtım.
    sequence: list[PlanPriority] = []
    while pool:
        candidates = sorted(
            set((item.subject, item.topic) for item in pool),
            key=lambda key: sum(1 for item in pool if (item.subject, item.topic) == key),
            reverse=True,
        )
        picked_key = next(
            (
                key
                for key in candidates
                if not sequence or (sequence[-1].subject, sequence[-1].topic) != key
            ),
            candidates[0],
        )
        index = next(
            i for i, item in enumerate(pool) if (item.subject, item.topic) == picked_key
        )
        sequence.append(pool.pop(index))
    return sequence[:count]


def build_weekly_plan(
    student: Student,
    priorities: list[PlanPriority],
    week_start: date | None = None,
    today: date | None = None,
) -> WeeklyPlanOut:
    today = today or date.today()
    week_start = monday_of(week_start or today)
    weekly_hours = max(1, min(int(student.weekly_hours), 80))
    total_minutes = weekly_hours * 60
    count = _session_count(total_minutes)
    durations = _split_minutes(total_minutes, count)
    topics = _weighted_topic_sequence(priorities, count)

    # Cumartesiye biraz daha fazla, pazara ise toparlama oturumu bırak.
    day_pattern = [0, 1, 2, 3, 4, 5, 5, 6]
    items: list[WeeklyPlanItemOut] = []
    for position, (duration, priority) in enumerate(zip(durations, topics, strict=True), start=1):
        day_index = day_pattern[(position - 1) % len(day_pattern)]
        mastery_text = (
            "ustalık verisi henüz az olduğu için teşhis önceliği"
            if priority.mastery is None
            else f"ustalık %{priority.mastery * 100:.0f} ve yüksek öncelik skoru"
        )
        items.append(
            WeeklyPlanItemOut(
                position=position,
                day_index=day_index,
                day_name=DAY_NAMES[day_index],
                subject=priority.subject,
                topic=priority.topic,
                activity=ACTIVITY_CYCLE[(position - 1) % len(ACTIVITY_CYCLE)],
                duration_minutes=duration,
                rationale=mastery_text,
            )
        )

    days_to_exam = (student.exam_date - today).days if student.exam_date else None
    deadline_text = (
        f"Sınava {days_to_exam} gün kaldığı için"
        if days_to_exam is not None
        else "Sınav tarihi girilmediği için"
    )
    summary = (
        f"{deadline_text} {weekly_hours} saatlik bütçe, "
        f"{len(priorities)} öncelikli konuya {count} oturum halinde dağıtıldı."
    )

    return WeeklyPlanOut(
        student_id=student.id or 0,
        week_start=week_start,
        created_on=today,
        exam_date=student.exam_date,
        weekly_hours=weekly_hours,
        total_minutes=total_minutes,
        days_to_exam=days_to_exam,
        summary=summary,
        priorities=priorities,
        items=items,
    )


def _deactivate_old_plans(session: Session, student_id: int) -> None:
    old_plans = session.exec(
        select(StudyPlan).where(
            StudyPlan.student_id == student_id,
            StudyPlan.is_active.is_(True),
        )
    ).all()
    for plan in old_plans:
        plan.is_active = False
        session.add(plan)


def generate_and_save_weekly_plan(
    session: Session,
    student_id: int,
    week_start: date | None = None,
    priorities: list[PlanPriority] | None = None,
    today: date | None = None,
) -> WeeklyPlanOut:
    student = session.get(Student, student_id)
    if not student:
        raise ValueError("Öğrenci bulunamadı")

    selected_priorities = priorities or _derived_priorities(session, student_id)
    draft = build_weekly_plan(student, selected_priorities, week_start=week_start, today=today)

    _deactivate_old_plans(session, student_id)
    plan = StudyPlan(
        student_id=student_id,
        week_start=draft.week_start,
        created_on=draft.created_on,
        exam_date=draft.exam_date,
        weekly_hours=draft.weekly_hours,
        total_minutes=draft.total_minutes,
        summary=draft.summary,
        priorities_json=json.dumps(
            [priority.model_dump() for priority in draft.priorities],
            ensure_ascii=False,
        ),
        is_active=True,
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)

    for item in draft.items:
        session.add(StudyPlanItem(plan_id=plan.id, **item.model_dump()))
    session.commit()

    return draft.model_copy(update={"id": plan.id})


def _priorities_for_plan(session: Session, plan: StudyPlan) -> list[PlanPriority]:
    try:
        raw = json.loads(plan.priorities_json)
        return [PlanPriority.model_validate(item) for item in raw]
    except (json.JSONDecodeError, TypeError, ValueError):
        # Eski veritabanı kaydıyla geriye uyumluluk.
        return _derived_priorities(session, plan.student_id)


def plan_to_output(session: Session, plan: StudyPlan) -> WeeklyPlanOut:
    items = session.exec(
        select(StudyPlanItem)
        .where(StudyPlanItem.plan_id == plan.id)
        .order_by(StudyPlanItem.position)
    ).all()
    days_to_exam = (plan.exam_date - date.today()).days if plan.exam_date else None
    return WeeklyPlanOut(
        id=plan.id,
        student_id=plan.student_id,
        week_start=plan.week_start,
        created_on=plan.created_on,
        exam_date=plan.exam_date,
        weekly_hours=plan.weekly_hours,
        total_minutes=plan.total_minutes,
        days_to_exam=days_to_exam,
        summary=plan.summary,
        priorities=_priorities_for_plan(session, plan),
        items=[WeeklyPlanItemOut.model_validate(item, from_attributes=True) for item in items],
    )


def get_latest_weekly_plan(session: Session, student_id: int) -> WeeklyPlanOut | None:
    plan = session.exec(
        select(StudyPlan)
        .where(StudyPlan.student_id == student_id, StudyPlan.is_active.is_(True))
        .order_by(StudyPlan.id.desc())
    ).first()
    return plan_to_output(session, plan) if plan else None


def list_weekly_plans(session: Session, student_id: int) -> list[WeeklyPlanOut]:
    plans = session.exec(
        select(StudyPlan)
        .where(StudyPlan.student_id == student_id)
        .order_by(StudyPlan.id.desc())
    ).all()
    return [plan_to_output(session, plan) for plan in plans]


def plan_to_markdown(plan: WeeklyPlanOut) -> str:
    lines = [
        f"## {plan.week_start:%d.%m.%Y} haftası çalışma planın",
        plan.summary,
        "",
    ]
    for item in plan.items:
        lines.append(
            f"- **{item.day_name}:** {item.topic} - {item.activity} "
            f"({item.duration_minutes} dk)"
        )
    lines.append("")
    lines.append(f"Toplam: **{plan.total_minutes // 60} saat**")
    return "\n".join(lines)
