from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlmodel import Session, select

from ..config import settings
from ..db import get_session
from ..models import QuestionEvent, Student
from ..services.mastery import estimate_mastery, study_priorities
from ..services.queries import (
    benzer_cikmis_sorular,
    kazanim_for_topic,
    load_observations,
    load_topic_weights,
    tutor_topic_index,
)

router = APIRouter(tags=["tutor"])


class AskOut(BaseModel):
    explanation: str
    subject: str
    topic: str
    in_scope: bool  # kapsam dışıysa sinyal kaydedilmez, arayüz nazik mesajı gösterir
    kaynak: str | None = None  # T2: konunun MEB kazanım referansı
    benzer_sorular: list[str] = []  # T2: aynı konudan çıkmış gerçek ÖSYM soruları


class QuizIn(BaseModel):
    topic: str | None = None  # verilmezse öğrencinin en zayıf konusu seçilir


class QuizOut(BaseModel):
    soru: str
    secenekler: dict[str, str]
    dogru: str
    cozum: str
    konu: str


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
        kaynak=kazanim_for_topic(result.topic) if in_scope else None,
        benzer_sorular=benzer_cikmis_sorular(result.topic) if in_scope else [],
    )


@router.post("/students/{student_id}/quiz", response_model=QuizOut)
def create_quiz(
    student_id: int, payload: QuizIn, session: Session = Depends(get_session)
) -> QuizOut:
    """T3: Doğrulanmış mini quiz üretir (konu verilmezse en zayıf konu seçilir).

    Öğrencinin cevabı arayüzden `POST /students/{id}/events` (source="quiz") ile
    gönderilir; doğru cevap ustalık haritasını yukarı günceller.
    """
    _ensure_student(session, student_id)

    topic = (payload.topic or "").strip() or None
    if topic and not _in_scope("Matematik", topic):
        raise HTTPException(status_code=422, detail=f"Geçersiz konu: {topic}")
    if topic is None:
        observations = load_observations(session, student_id)
        if not observations:
            raise HTTPException(
                status_code=422,
                detail="Önce bir soru sorun ya da quiz için konu belirtin — zayıf konu "
                "seçebilmek için haritada sinyal olmalı.",
            )
        ranked = study_priorities(estimate_mastery(observations), load_topic_weights(), top=1)
        topic = ranked[0][0].topic

    if not settings.google_api_key:
        raise HTTPException(
            status_code=503,
            detail="GOOGLE_API_KEY tanımlı değil. Kök dizindeki .env dosyasına anahtarınızı "
            "girin (bkz. .env.example).",
        )

    try:
        from ..agents.quiz import generate_quiz
    except ImportError as exc:
        raise HTTPException(
            status_code=503, detail=f"Agent bağımlılıkları kurulu değil: {exc}"
        ) from exc

    try:
        quiz = generate_quiz(topic)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return QuizOut(
        soru=quiz.soru, secenekler=quiz.secenekler, dogru=quiz.dogru,
        cozum=quiz.cozum, konu=quiz.konu,
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


# ---------------------------------------------------------------------------
# Quiz endpoint'leri (T3 — Sprint 2)
# ---------------------------------------------------------------------------

class QuizOut(BaseModel):
    topic: str
    question: str
    choices: list[str]
    answer_index: int      # doğru şık (0-3); arayüz gösterir, kullanıcı cevapladıktan sonra
    explanation: str
    is_fallback: bool      # True → AI üretmedi, statik örnek soru kullanıldı


class QuizAnswerIn(BaseModel):
    topic: str
    selected_index: int    # öğrencinin seçtiği şık (0-3)
    correct_index: int     # doğru cevabın indeksi


class QuizAnswerOut(BaseModel):
    succeeded: bool
    explanation: str
    event_id: int          # haritaya işlenen QuestionEvent ID'si


@router.get("/students/{student_id}/quiz", response_model=QuizOut)
def generate_quiz(
    student_id: int,
    topic: str,
    session: Session = Depends(get_session),
) -> QuizOut:
    """Verilen konu için quiz sorusu üretir.

    GOOGLE_API_KEY yoksa veya LLM hatası olursa statik fallback soru döner;
    arayüz her koşulda çalışmaya devam eder.
    """
    _ensure_student(session, student_id)
    if not _in_scope("Matematik", topic):
        raise HTTPException(
            status_code=422,
            detail=f"Quiz yalnızca TYT Matematik konuları için üretilir. Geçersiz konu: {topic}",
        )

    from ..agents.quiz import generate_quiz_question

    q = generate_quiz_question(topic, settings.google_api_key)
    return QuizOut(
        topic=q.topic,
        question=q.question,
        choices=q.choices,
        answer_index=q.answer_index,
        explanation=q.explanation,
        is_fallback=q.is_fallback,
    )


@router.post("/students/{student_id}/quiz/answer", response_model=QuizAnswerOut)
def submit_quiz_answer(
    student_id: int,
    payload: QuizAnswerIn,
    session: Session = Depends(get_session),
) -> QuizAnswerOut:
    """Öğrencinin quiz cevabını haritaya işler.

    Doğruysa succeeded=True → ustalık yukarı; yanlışsa False → zayıflık sinyali.
    """
    _ensure_student(session, student_id)
    if not _in_scope("Matematik", payload.topic):
        raise HTTPException(status_code=422, detail="Geçersiz konu")

    succeeded = payload.selected_index == payload.correct_index
    event = QuestionEvent(
        student_id=student_id,
        subject="Matematik",
        topic=payload.topic,
        source="quiz",
        succeeded=succeeded,
        happened_on=date.today(),
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return QuizAnswerOut(
        succeeded=succeeded,
        explanation="" ,  # explanation arayüzde zaten gösteriliyor
        event_id=event.id,
    )
