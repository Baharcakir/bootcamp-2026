from datetime import date

from sqlmodel import Field, SQLModel


class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    exam_date: date | None = None  # hedef sınav (YKS) tarihi
    weekly_hours: int = 20  # haftalık çalışma saati bütçesi
    goal: str | None = None  # ör. "Tıp — ilk 30 bin"


class MockExam(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    name: str
    taken_on: date


class SubjectResult(SQLModel, table=True):
    """Denemenin ders bazlı özeti — öğrenci deneme başına yalnızca 4-5 satır girer.

    Konu kırılımı istemiyoruz: bu tablo sadece net gidişatını besler. Konu bazlı
    zayıflık haritası QuestionEvent'lerden (pasif sinyallerden) örülür.
    """

    id: int | None = Field(default=None, primary_key=True)
    exam_id: int = Field(foreign_key="mockexam.id", index=True)
    subject: str  # ör. "Matematik"
    correct: int = 0
    wrong: int = 0
    blank: int = 0


class QuestionEvent(SQLModel, table=True):
    """Pasif öğrenme sinyali — ürünün çekirdek verisi.

    Öğrenci çözemediği soruyu sorduğunda (source=photo_ask, succeeded=False),
    fotoğrafsız 'bu konuda takıldım' dediğinde (source=manual) veya mini quiz
    çözdüğünde (source=quiz, succeeded=doğru/yanlış) bir kayıt düşer.
    Konu etiketini ÖĞRENCİ DEĞİL, yapay zeka koyar (agents/tutor.py).
    """

    id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    subject: str
    topic: str
    source: str = "photo_ask"  # photo_ask | manual | quiz
    succeeded: bool = False  # soru soruldu = çözemedi (False); quiz doğruysa True
    happened_on: date
    question_summary: str | None = None  # Sprint 2'de RAG ve tekrar önerileri için
