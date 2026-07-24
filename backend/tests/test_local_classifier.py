"""T6 — yerel konu sınıflandırıcısı ve anahtarsız (demo modu) akış testleri."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.config import settings
from app.db import get_session
from app.main import app
from app.services.classifier import classify_topic
from app.services.queries import tutor_topic_index


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    def override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def student_id(client):
    resp = client.post("/students", json={"name": "Deniz", "weekly_hours": 20})
    assert resp.status_code == 200
    return resp.json()["id"]


def test_yerel_siniflandirici_taksonomiden_konu_doner():
    topic = classify_topic(
        "Bir torbada 5 kırmızı ve 3 mavi top vardır. Torbadan rastgele çekilen bir "
        "topun kırmızı olma olasılığı kaçtır?"
    )
    assert topic in tutor_topic_index()["Matematik"]


def test_bos_metin_none_doner():
    assert classify_topic("") is None
    assert classify_topic(None) is None


def test_anahtarsiz_metin_soru_yerel_etiketlenir_ve_sinyal_duser(
    client, student_id, monkeypatch
):
    monkeypatch.setattr(settings, "google_api_key", "")
    resp = client.post(
        f"/students/{student_id}/ask",
        data={"text": "Bir zar iki kez atılıyor. Üste gelen sayıların toplamının 7 "
              "olma olasılığı kaçtır?"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["yerel_etiket"] is True
    assert body["in_scope"] is True
    assert body["topic"] in tutor_topic_index()["Matematik"]

    events = client.get(f"/students/{student_id}/events").json()
    assert len(events) == 1
    assert events[0]["topic"] == body["topic"]
    assert events[0]["succeeded"] is False


def test_anahtarsiz_fotografli_soru_503_doner(client, student_id, monkeypatch):
    monkeypatch.setattr(settings, "google_api_key", "")
    resp = client.post(
        f"/students/{student_id}/ask",
        files={"file": ("soru.jpg", b"sahte-goruntu", "image/jpeg")},
    )
    assert resp.status_code == 503


def test_anahtarsiz_quiz_fallback_calisir(client, student_id, monkeypatch):
    monkeypatch.setattr(settings, "google_api_key", "")
    resp = client.get(f"/students/{student_id}/quiz", params={"topic": "Olasılık"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_fallback"] is True
    assert len(body["choices"]) == 5
    assert 0 <= body["answer_index"] < 5
