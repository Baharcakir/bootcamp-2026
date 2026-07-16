"""Demo verisi yükleyici — tek komutla ekran görüntüsü/jüri demosuna hazır ürün.

Kullanım (repo kökünden):
    python backend/scripts/seed_demo.py

Ne üretir: 1 demo öğrenci, ~3 haftaya yayılmış soru/quiz sinyalleri (zayıf konular sık,
güçlü konular quiz başarılı) ve netleri yükselen 4 deneme. Böylece Analiz Panosu ve koç
sohbeti veriyle dolu açılır. Deterministiktir (sabit random seed).
"""

import random
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlmodel import Session  # noqa: E402

from app.db import engine, init_db  # noqa: E402
from app.models import MockExam, QuestionEvent, Student, SubjectResult  # noqa: E402

TODAY = date.today()
WEAK_TOPICS = ["Problemler", "İkinci Dereceden Denklemler", "Olasılık"]
MID_TOPICS = ["Fonksiyonlar", "Üslü Sayılar", "Denklem Çözme"]
STRONG_TOPICS = ["Kümeler", "Temel Kavramlar"]
# (kaç gün önce, matematik doğru, matematik yanlış) — yükselen bir hikaye
EXAMS = [(28, 14, 10), (21, 17, 9), (12, 19, 8), (4, 22, 6)]


def build_events(student_id: int) -> list[QuestionEvent]:
    rng = random.Random(42)
    events = []
    for days_ago in range(21, -1, -1):
        day = TODAY - timedelta(days=days_ago)
        for topic, ask_prob in [(t, 0.35) for t in WEAK_TOPICS] + [
            (t, 0.15) for t in MID_TOPICS
        ]:
            if rng.random() < ask_prob:
                events.append(
                    QuestionEvent(
                        student_id=student_id,
                        subject="Matematik",
                        topic=topic,
                        source="photo_ask",
                        succeeded=False,
                        happened_on=day,
                    )
                )
        for topic in STRONG_TOPICS:
            if rng.random() < 0.2:
                events.append(
                    QuestionEvent(
                        student_id=student_id,
                        subject="Matematik",
                        topic=topic,
                        source="quiz",
                        succeeded=True,
                        happened_on=day,
                    )
                )
    return events


def build_exams(session: Session, student_id: int) -> None:
    for i, (days_ago, mat_correct, mat_wrong) in enumerate(EXAMS, start=1):
        exam = MockExam(
            student_id=student_id,
            name=f"TYT Deneme {i}",
            taken_on=TODAY - timedelta(days=days_ago),
        )
        session.add(exam)
        session.commit()
        session.refresh(exam)
        session.add_all(
            [
                SubjectResult(
                    exam_id=exam.id, subject="Türkçe", correct=28 + i, wrong=6, blank=6 - i
                ),
                SubjectResult(
                    exam_id=exam.id,
                    subject="Matematik",
                    correct=mat_correct,
                    wrong=mat_wrong,
                    blank=40 - mat_correct - mat_wrong,
                ),
                SubjectResult(
                    exam_id=exam.id, subject="Fen Bilimleri", correct=8 + i, wrong=5, blank=7 - i
                ),
                SubjectResult(
                    exam_id=exam.id,
                    subject="Sosyal Bilimler",
                    correct=11 + i,
                    wrong=4,
                    blank=5 - i,
                ),
            ]
        )
    session.commit()


def main() -> None:
    init_db()
    with Session(engine) as session:
        student = Student(
            name="Demo Öğrenci",
            exam_date=date(2027, 6, 19),
            weekly_hours=20,
            goal="Bilgisayar Mühendisliği — ilk 50 bin",
        )
        session.add(student)
        session.commit()
        session.refresh(student)

        events = build_events(student.id)
        session.add_all(events)
        session.commit()
        build_exams(session, student.id)

        print(
            f"Demo öğrenci #{student.id} oluşturuldu: {len(events)} sinyal, {len(EXAMS)} deneme."
        )
        print("Şimdi API'yi ve arayüzü başlatın; Analiz Panosu dolu gelecek.")


if __name__ == "__main__":
    main()
