from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from ..config import settings
from ..db import get_session
from ..models import Student

router = APIRouter(tags=["coach"])


class ChatIn(BaseModel):
    message: str


class ChatOut(BaseModel):
    reply: str


@router.post("/students/{student_id}/chat", response_model=ChatOut)
def chat_with_coach(
    student_id: int, payload: ChatIn, session: Session = Depends(get_session)
) -> ChatOut:
    if not session.get(Student, student_id):
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    if not payload.message.strip():
        raise HTTPException(status_code=422, detail="Mesaj boş olamaz")
    if not settings.google_api_key:
        raise HTTPException(
            status_code=503,
            detail="GOOGLE_API_KEY tanımlı değil. Kök dizinde .env dosyası oluşturup "
            "anahtarınızı girin (bkz. .env.example).",
        )

    # Agent bağımlılıkları ağır olduğundan tembel yüklenir; API anahtarsız da uygulama ayakta kalır.
    try:
        from ..agents.graph import ask_coach
    except ImportError as exc:
        raise HTTPException(
            status_code=503, detail=f"Agent bağımlılıkları kurulu değil: {exc}"
        ) from exc

    return ChatOut(reply=ask_coach(student_id, payload.message))
