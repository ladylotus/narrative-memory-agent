"""Basic API smoke tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_ingest_stub() -> None:
    resp = client.post("/ingest/")
    assert resp.status_code == 200


def test_ask_stub() -> None:
    resp = client.post(
        "/ask/",
        json={"character": "Leo", "question": "What now?", "num_options": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "not_implemented"


def test_profile_stub() -> None:
    resp = client.get("/profile/Leo")
    assert resp.status_code == 200


def test_sleep_stub() -> None:
    resp = client.post("/sleep/Leo")
    assert resp.status_code == 200
