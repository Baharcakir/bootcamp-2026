import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import get_session
from app.main import app


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
    resp = client.post("/students", json={"name": "Ayşe", "weekly_hours": 25})
    assert resp.status_code == 200
    return resp.json()["id"]


def test_deneme_ders_bazinda_girilir_ve_net_hesaplanir(student_id, client):
    exam = {
        "name": "TYT Deneme 1",
        "taken_on": "2026-06-28",
        "results": [
            {"subject": "Matematik", "correct": 25, "wrong": 8, "blank": 7},
            {"subject": "Türkçe", "correct": 30, "wrong": 4, "blank": 6},
        ],
    }
    resp = client.post(f"/students/{student_id}/exams", json=exam)
    assert resp.status_code == 200
    # net = (25+30) - (8+4)/4 = 55 - 3
    assert resp.json()["net"] == 52.0

    resp = client.get(f"/students/{student_id}/trend")
    assert resp.status_code == 200
    assert resp.json()["predicted_next"] == 52.0  # tek denemede tahmin = son net


def test_sinyaller_ustalik_haritasina_donusur(student_id, client):
    # Öğrenci 3 kez Problemler'de takıldı, 1 kez Kümeler quizini doğru çözdü
    for _ in range(3):
        resp = client.post(
            f"/students/{student_id}/events",
            json={"subject": "Matematik", "topic": "Problemler", "succeeded": False},
        )
        assert resp.status_code == 200
    resp = client.post(
        f"/students/{student_id}/events",
        json={"subject": "Matematik", "topic": "Kümeler", "succeeded": True, "source": "quiz"},
    )
    assert resp.status_code == 200

    resp = client.get(f"/students/{student_id}/mastery")
    assert resp.status_code == 200
    by_topic = {m["topic"]: m for m in resp.json()}
    assert set(by_topic) == {"Problemler", "Kümeler"}
    assert by_topic["Problemler"]["mastery"] < by_topic["Kümeler"]["mastery"]

    resp = client.get(f"/students/{student_id}/priorities", params={"top": 1})
    assert resp.status_code == 200
    assert resp.json()[0]["topic"] == "Problemler"

    resp = client.get(f"/students/{student_id}/events")
    assert len(resp.json()) == 4


def test_bilinmeyen_ders_reddedilir(student_id, client):
    resp = client.post(
        f"/students/{student_id}/events",
        json={"subject": "Simya", "topic": "Felsefe Taşı"},
    )
    assert resp.status_code == 422


def test_kapsam_disi_ders_sinyal_uretemez(student_id, client):
    # Türkçe deneme netine girilebilir ama koçluk kapsamı (v1) dışıdır: sinyal reddedilir
    resp = client.post(
        f"/students/{student_id}/events",
        json={"subject": "Türkçe", "topic": "Paragraf"},
    )
    assert resp.status_code == 422
    assert "TYT Matematik" in resp.json()["detail"]


def test_gecersiz_matematik_konusu_reddedilir(student_id, client):
    resp = client.post(
        f"/students/{student_id}/events",
        json={"subject": "Matematik", "topic": "Türev"},  # AYT konusu, taksonomide yok
    )
    assert resp.status_code == 422


def test_olmayan_ogrenci_404(client):
    assert client.get("/students/999").status_code == 404
    assert client.get("/students/999/mastery").status_code == 404


def test_sonucsuz_deneme_reddedilir(student_id, client):
    resp = client.post(
        f"/students/{student_id}/exams",
        json={"name": "Boş", "taken_on": "2026-06-28", "results": []},
    )
    assert resp.status_code == 422


def test_api_anahtari_yoksa_soru_sorma_503_doner(student_id, client, monkeypatch):
    monkeypatch.setattr("app.routers.tutor.settings.google_api_key", None)
    resp = client.post(f"/students/{student_id}/ask", data={"text": "Bu soruyu çözemedim"})
    assert resp.status_code == 503
    assert "GOOGLE_API_KEY" in resp.json()["detail"]


def test_bos_soru_gonderilemez(student_id, client):
    resp = client.post(f"/students/{student_id}/ask", data={"text": "  "})
    assert resp.status_code == 422


def test_api_anahtari_yoksa_koc_503_doner(student_id, client, monkeypatch):
    monkeypatch.setattr("app.routers.coach.settings.google_api_key", None)
    resp = client.post(f"/students/{student_id}/chat", json={"message": "Nasılım?"})
    assert resp.status_code == 503


def test_quiz_gecersiz_konu_422(student_id, client):
    resp = client.post(f"/students/{student_id}/quiz", json={"topic": "Türev"})
    assert resp.status_code == 422


def test_quiz_konusuz_ve_verisiz_422(student_id, client):
    resp = client.post(f"/students/{student_id}/quiz", json={})
    assert resp.status_code == 422
    assert "konu" in resp.json()["detail"].lower()


def test_quiz_anahtarsiz_503(student_id, client, monkeypatch):
    monkeypatch.setattr("app.routers.tutor.settings.google_api_key", None)
    resp = client.post(f"/students/{student_id}/quiz", json={"topic": "Problemler"})
    assert resp.status_code == 503


def test_kazanim_ve_benzer_soru_getirme():
    from app.services.queries import benzer_cikmis_sorular, kazanim_for_topic

    kaynak = kazanim_for_topic("Problemler")
    assert kaynak is not None and "9.3.5.2" in kaynak
    assert kazanim_for_topic("Olmayan Konu") is None

    benzer = benzer_cikmis_sorular("Problemler")
    assert benzer, "T4 setinde Problemler etiketi var, öneri boş olmamalı"
    assert all("TYT s." in b for b in benzer)
