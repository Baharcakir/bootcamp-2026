from datetime import date

from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.models import QuestionEvent, Student, StudyPlan, StudyPlanItem
from app.services.planner import generate_and_save_weekly_plan, get_latest_weekly_plan


def make_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_plan_saat_butcesini_tam_kullanir_ve_db_ye_kaydeder():
    with make_session() as session:
        student = Student(
            name="Ayşe",
            exam_date=date(2027, 6, 19),
            weekly_hours=10,
            goal="İlk 50 bin",
        )
        session.add(student)
        session.commit()
        session.refresh(student)

        plan = generate_and_save_weekly_plan(
            session,
            student.id,
            today=date(2026, 7, 18),
        )

        assert plan.total_minutes == 600
        assert sum(item.duration_minutes for item in plan.items) == 600
        assert plan.id is not None
        assert session.exec(select(StudyPlan)).all()
        assert len(session.exec(select(StudyPlanItem)).all()) == len(plan.items)


def test_zayif_konu_plan_onceligine_girer():
    with make_session() as session:
        student = Student(name="Mehmet", weekly_hours=6)
        session.add(student)
        session.commit()
        session.refresh(student)

        for _ in range(5):
            session.add(
                QuestionEvent(
                    student_id=student.id,
                    subject="Matematik",
                    topic="Problemler",
                    source="manual",
                    succeeded=False,
                    happened_on=date(2026, 7, 18),
                )
            )
        session.add(
            QuestionEvent(
                student_id=student.id,
                subject="Matematik",
                topic="Kümeler",
                source="quiz",
                succeeded=True,
                happened_on=date(2026, 7, 18),
            )
        )
        session.commit()

        plan = generate_and_save_weekly_plan(session, student.id, today=date(2026, 7, 18))
        assert plan.priorities[0].topic == "Problemler"
        assert sum(item.topic == "Problemler" for item in plan.items) >= 1


def test_yeni_plan_onceki_plani_pasif_yapar():
    with make_session() as session:
        student = Student(name="Ece", weekly_hours=4)
        session.add(student)
        session.commit()
        session.refresh(student)

        first = generate_and_save_weekly_plan(session, student.id, today=date(2026, 7, 18))
        second = generate_and_save_weekly_plan(session, student.id, today=date(2026, 7, 19))
        assert first.id != second.id

        plans = session.exec(select(StudyPlan).order_by(StudyPlan.id)).all()
        assert plans[0].is_active is False
        assert plans[1].is_active is True
        assert get_latest_weekly_plan(session, student.id).id == second.id
