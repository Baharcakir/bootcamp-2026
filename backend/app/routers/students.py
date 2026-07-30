import os
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
import joblib
import numpy as np

from ..db import get_session
from ..models import Student

router = APIRouter(tags=["students"])

# 1. Modeli Yükleme (Eğittiğimiz joblib dosyasını bağlıyoruz)
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "net_predictor.joblib"))

model = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    print(f"⚠️ UYARI: Model dosyası bulunamadı: {MODEL_PATH}")


class StudentIn(BaseModel):
    name: str
    exam_date: date | None = None
    weekly_hours: int = 20
    goal: str | None = None


class PredictionResponse(BaseModel):
    student_id: int
    predicted_net: float
    status: str


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


# 2. Görevde İstenen Yeni Endpoint: ML Modelinden Beslenen Net Tahmini
@router.get("/students/{student_id}/prediction", response_model=PredictionResponse)
def get_student_prediction(student_id: int, session: Session = Depends(get_session)) -> PredictionResponse:
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    
    if model is None:
        raise HTTPException(status_code=500, detail="Net tahmin modeli sunucuda yüklü değil.")

    # Öğrencinin son metrikleri (Varsayılan veya DB'den çekilecek değerler)
    # Örnek: [son_deneme_neti, ustalik_ortalamasi, sinyal_yogunlugu]
    # Gerekirse veritabanındaki öğrenci geçmişinden dinamik hesaplanabilir
    features = np.array([[25.0, 0.75, 0.8]]) 
    
    predicted_val = model.predict(features)[0]

    return PredictionResponse(
        student_id=student_id,
        predicted_net=round(float(predicted_val), 2),
        status="success"
    )