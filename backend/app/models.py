from datetime import date

from sqlmodel import Field, SQLModel


class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    exam_date: date | None = None
    weekly_hours: int = 20
    goal: str | None = None


class MockExam(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    name: str
    taken_on: date


class SubjectResult(SQLModel, table=True):
    """Denemenin ders bazlı özeti; konu kırılımı QuestionEvent'ten gelir."""

    id: int | None = Field(default=None, primary_key=True)
    exam_id: int = Field(foreign_key="mockexam.id", index=True)
    subject: str
    correct: int = 0
    wrong: int = 0
    blank: int = 0


class QuestionEvent(SQLModel, table=True):
    """Soru sorma ve mini quizlerden kendiliğinden oluşan öğrenme sinyali."""

    id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    subject: str
    topic: str
    source: str = "photo_ask"
    succeeded: bool = False
    happened_on: date
    question_summary: str | None = None


class StudyPlan(SQLModel, table=True):
    """Bir öğrenci için üretilmiş haftalık çalışma planının üst kaydı."""

    id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    week_start: date = Field(index=True)
    created_on: date = Field(default_factory=date.today)
    exam_date: date | None = None
    weekly_hours: int
    total_minutes: int
    summary: str
    priorities_json: str = "[]"
    is_active: bool = Field(default=True, index=True)


class StudyPlanItem(SQLModel, table=True):
    """Haftalık plan içindeki sıralı çalışma oturumu."""

    id: int | None = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="studyplan.id", index=True)
    position: int
    day_index: int
    day_name: str
    subject: str
    topic: str
    activity: str
    duration_minutes: int
    rationale: str
