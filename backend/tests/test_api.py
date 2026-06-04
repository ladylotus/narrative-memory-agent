"""Basic API smoke tests — updated for real services."""

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


def test_ask_real() -> None:
    """/ask should now return real options for seeded character."""
    resp = client.post(
        "/ask/",
        json={"character": "Caelan Ashmark", "question": "What keeps you up at night?", "num_options": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert len(data["options"]) == 3
    # Each option should have OOC risk
    for opt in data["options"]:
        assert "ooc_risk" in opt
        assert 0.0 <= opt["ooc_risk"] <= 1.0


def test_ask_unknown_character() -> None:
    resp = client.post(
        "/ask/",
        json={"character": "Unknown", "question": "Hello?", "num_options": 3},
    )
    assert resp.status_code == 404


def test_profile_real() -> None:
    """/profile should now return real data from database."""
    resp = client.get("/profile/Caelan Ashmark")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["character"] == "Caelan Ashmark"
    assert len(data["traits"]) > 0
    # Should have core traits
    core_traits = [t for t in data["traits"] if t.get("category") == "core"]
    assert len(core_traits) > 0


def test_profile_unknown() -> None:
    resp = client.get("/profile/Unknown")
    assert resp.status_code == 404


def test_sleep_stub() -> None:
    resp = client.post("/sleep/Caelan Ashmark")
    assert resp.status_code == 200
