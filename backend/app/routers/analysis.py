from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..db import get_session
from ..models import Student
from ..services.mastery import estimate_mastery, study_priorities
from ..services.queries import load_exam_nets, load_observations, load_subject_nets, load_topic_weights
from ..services.trajectory import net_trend

router = APIRouter(tags=["analysis"])


def _ensure_student(session: Session, student_id: int) -> None:
    if not session.get(Student, student_id):
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")


@router.get("/students/{student_id}/mastery")
def get_mastery(student_id: int, session: Session = Depends(get_session)) -> list[dict]:
    _ensure_student(session, student_id)
    masteries = estimate_mastery(load_observations(session, student_id))
    return [asdict(m) for m in masteries]


@router.get("/students/{student_id}/priorities")
def get_priorities(
    student_id: int, top: int = 10, session: Session = Depends(get_session)
) -> list[dict]:
    _ensure_student(session, student_id)
    masteries = estimate_mastery(load_observations(session, student_id))
    ranked = study_priorities(masteries, load_topic_weights(), top=top)
    return [
        {
            "subject": m.subject,
            "topic": m.topic,
            "mastery": round(m.mastery, 3),
            "priority": round(score, 3),
        }
        for m, score in ranked
    ]


@router.get("/students/{student_id}/trend")
def get_trend(student_id: int, session: Session = Depends(get_session)) -> dict:
    _ensure_student(session, student_id)
    trend = net_trend(load_exam_nets(session, student_id))
    return {
        "history": [asdict(e) for e in trend.history],
        "slope_per_week": trend.slope_per_week,
        "predicted_next": trend.predicted_next,
    }


@router.get("/students/{student_id}/subject_trend")
def get_subject_trend(student_id: int, session: Session = Depends(get_session)) -> dict:
    """Ders bazında ayrı net gidişatı.

    Veritabanında kayıtlı hangi ders varsa onu döner — hardcoded ders ismi yok.
    Dönen yapı: {"subjects": {"Matematik": {history, slope_per_week, predicted_next}, ...}}
    """
    _ensure_student(session, student_id)
    subject_nets = load_subject_nets(session, student_id)  # {ders: [ExamNet]}
    result = {}
    for subject, nets in subject_nets.items():
        trend = net_trend(nets)
        result[subject] = {
            "history": [asdict(e) for e in trend.history],
            "slope_per_week": trend.slope_per_week,
            "predicted_next": trend.predicted_next,
        }
    return {"subjects": result}
