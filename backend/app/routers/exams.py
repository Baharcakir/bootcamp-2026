from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from ..db import get_session
from ..models import MockExam, Student, SubjectResult
from ..services.queries import load_topics
from ..services.trajectory import compute_net

router = APIRouter(tags=["exams"])


class SubjectResultIn(BaseModel):
    subject: str
    correct: int = 0
    wrong: int = 0
    blank: int = 0


class ExamIn(BaseModel):
    """Deneme girişi bilerek kaba tutulur: ders başına tek satır (4-5 satır, ~10 saniye).

    Konu kırılımı istemeyiz; konu haritası soru sorma akışından kendiliğinden oluşur.
    """

    name: str
    taken_on: date
    results: list[SubjectResultIn]


class ExamOut(BaseModel):
    id: int
    name: str
    taken_on: date
    net: float


@router.get("/topics")
def get_topics() -> dict:
    """TYT ders → konu taksonomisi (eğitmenin otomatik etiketlemesi ve arayüz için)."""
    return load_topics()


@router.post("/students/{student_id}/exams", response_model=ExamOut)
def add_exam(
    student_id: int, payload: ExamIn, session: Session = Depends(get_session)
) -> ExamOut:
    if not session.get(Student, student_id):
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    if not payload.results:
        raise HTTPException(status_code=422, detail="En az bir ders sonucu girilmeli")

    exam = MockExam(student_id=student_id, name=payload.name, taken_on=payload.taken_on)
    session.add(exam)
    session.commit()
    session.refresh(exam)
    for result in payload.results:
        session.add(SubjectResult(exam_id=exam.id, **result.model_dump()))
    session.commit()

    net = compute_net(
        sum(r.correct for r in payload.results), sum(r.wrong for r in payload.results)
    )
    return ExamOut(id=exam.id, name=exam.name, taken_on=exam.taken_on, net=net)


@router.get("/students/{student_id}/exams", response_model=list[ExamOut])
def list_exams(student_id: int, session: Session = Depends(get_session)) -> list[ExamOut]:
    if not session.get(Student, student_id):
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    exams = session.exec(select(MockExam).where(MockExam.student_id == student_id)).all()
    out = []
    for exam in exams:
        results = session.exec(
            select(SubjectResult).where(SubjectResult.exam_id == exam.id)
        ).all()
        net = compute_net(sum(r.correct for r in results), sum(r.wrong for r in results))
        out.append(ExamOut(id=exam.id, name=exam.name, taken_on=exam.taken_on, net=net))
    return out
