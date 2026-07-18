from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from ..db import get_session
from ..models import Student
from ..services.planner import (
    WeeklyPlanOut,
    generate_and_save_weekly_plan,
    get_latest_weekly_plan,
    list_weekly_plans,
)

router = APIRouter(tags=["plans"])


class GeneratePlanIn(BaseModel):
    week_start: date | None = None


def _ensure_student(session: Session, student_id: int) -> None:
    if not session.get(Student, student_id):
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")


@router.post("/students/{student_id}/plans/generate", response_model=WeeklyPlanOut)
def generate_plan(
    student_id: int,
    payload: GeneratePlanIn | None = None,
    session: Session = Depends(get_session),
) -> WeeklyPlanOut:
    _ensure_student(session, student_id)
    return generate_and_save_weekly_plan(
        session,
        student_id,
        week_start=payload.week_start if payload else None,
    )


@router.get("/students/{student_id}/plans/latest", response_model=WeeklyPlanOut | None)
def latest_plan(
    student_id: int,
    session: Session = Depends(get_session),
) -> WeeklyPlanOut | None:
    _ensure_student(session, student_id)
    return get_latest_weekly_plan(session, student_id)


@router.get("/students/{student_id}/plans", response_model=list[WeeklyPlanOut])
def plans_history(
    student_id: int,
    session: Session = Depends(get_session),
) -> list[WeeklyPlanOut]:
    _ensure_student(session, student_id)
    return list_weekly_plans(session, student_id)
