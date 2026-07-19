import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import get_session
from app.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_plan_api_uret_kaydet_ve_goster(client):
    student = client.post(
        "/students",
        json={
            "name": "Deniz",
            "exam_date": "2027-06-19",
            "weekly_hours": 8,
        },
    ).json()

    generated = client.post(f"/students/{student['id']}/plans/generate", json={})
    assert generated.status_code == 200
    body = generated.json()
    assert body["total_minutes"] == 480
    assert sum(item["duration_minutes"] for item in body["items"]) == 480

    latest = client.get(f"/students/{student['id']}/plans/latest")
    assert latest.status_code == 200
    assert latest.json()["id"] == body["id"]

    history = client.get(f"/students/{student['id']}/plans")
    assert history.status_code == 200
    assert len(history.json()) == 1
