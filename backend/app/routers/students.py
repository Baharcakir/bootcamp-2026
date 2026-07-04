from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from ..db import get_session
from ..models import Student

router = APIRouter(tags=["students"])


class StudentIn(BaseModel):
    name: str
    exam_date: date | None = None
    weekly_hours: int = 20
    goal: str | None = None


@router.post("/students", response_model=Student)
def create_student(payload: StudentIn, session: Session = Depends(get_session)) -> Student:
    student = Student(**payload.model_dump())
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


@router.get("/students", response_model=list[Student])
def list_students(session: Session = Depends(get_session)) -> list[Student]:
    return list(session.exec(select(Student)).all())


@router.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int, session: Session = Depends(get_session)) -> Student:
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    return student
