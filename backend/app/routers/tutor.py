from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlmodel import Session, select

from ..config import settings
from ..db import get_session
from ..models import QuestionEvent, Student
from ..services.queries import tutor_topic_index

router = APIRouter(tags=["tutor"])


class AskOut(BaseModel):
    explanation: str
    subject: str
    topic: str
    in_scope: bool  # kapsam dışıysa sinyal kaydedilmez, arayüz nazik mesajı gösterir


class EventIn(BaseModel):
    subject: str
    topic: str
    succeeded: bool = False
    source: str = "manual"  # manual | quiz (photo_ask yalnızca /ask üzerinden düşer)


def _ensure_student(session: Session, student_id: int) -> None:
    if not session.get(Student, student_id):
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")


def _in_scope(subject: str, topic: str) -> bool:
    index = tutor_topic_index()
    return subject in index and topic in index[subject]


@router.post("/students/{student_id}/ask", response_model=AskOut)
async def ask_question(
    student_id: int,
    file: UploadFile | None = File(None),
    text: str | None = Form(None),
    session: Session = Depends(get_session),
) -> AskOut:
    """Çekirdek akış: soru fotoğrafı/metni → anlatım + otomatik konu etiketi.

    Kapsam içi (v1: TYT Matematik) her soru bir QuestionEvent düşürür; zayıflık haritası
    böyle örülür — öğrenci hiçbir zaman konu seçmez/etiketlemez. Kapsam dışı sorular
    kibarca yönlendirilir, kayıt düşmez.
    """
    _ensure_student(session, student_id)
    if file is None and not (text and text.strip()):
        raise HTTPException(status_code=422, detail="Fotoğraf veya soru metni gönderin")
    if not settings.google_api_key:
        raise HTTPException(
            status_code=503,
            detail="GOOGLE_API_KEY tanımlı değil. Kök dizindeki .env dosyasına anahtarınızı "
            "girin (bkz. .env.example).",
        )

    try:
        from ..agents.tutor import explain_question
    except ImportError as exc:
        raise HTTPException(
            status_code=503, detail=f"Agent bağımlılıkları kurulu değil: {exc}"
        ) from exc

    image_bytes = await file.read() if file else None
    result = explain_question(image_bytes, file.content_type if file else None, text)

    in_scope = _in_scope(result.subject, result.topic)
    if in_scope:
        session.add(
            QuestionEvent(
                student_id=student_id,
                subject=result.subject,
                topic=result.topic,
                source="photo_ask",
                succeeded=False,  # soruyu sordu = çözememişti
                happened_on=date.today(),
                question_summary=result.question_summary or None,
            )
        )
        session.commit()
    return AskOut(
        explanation=result.explanation,
        subject=result.subject,
        topic=result.topic,
        in_scope=in_scope,
    )


@router.post("/students/{student_id}/events", response_model=QuestionEvent)
def log_event(
    student_id: int, payload: EventIn, session: Session = Depends(get_session)
) -> QuestionEvent:
    """Fotoğrafsız geri düşüş ('bu konuda takıldım') ve quiz sonuçları (T3) için."""
    _ensure_student(session, student_id)
    if not _in_scope(payload.subject, payload.topic):
        raise HTTPException(
            status_code=422,
            detail="Çarpan v1 yalnızca TYT Matematik konularını takip ediyor. "
            f"Geçersiz ders/konu: {payload.subject} / {payload.topic}",
        )

    event = QuestionEvent(
        student_id=student_id, happened_on=date.today(), **payload.model_dump()
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.get("/students/{student_id}/events", response_model=list[QuestionEvent])
def list_events(
    student_id: int, limit: int = 50, session: Session = Depends(get_session)
) -> list[QuestionEvent]:
    _ensure_student(session, student_id)
    events = session.exec(
        select(QuestionEvent)
        .where(QuestionEvent.student_id == student_id)
        .order_by(QuestionEvent.id.desc())
        .limit(limit)
    ).all()
    return list(events)
