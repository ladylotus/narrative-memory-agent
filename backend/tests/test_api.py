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
        json={"character": "Elizabeth Bennet", "question": "What keeps you up at night?", "num_options": 3},
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
    resp = client.get("/profile/Elizabeth Bennet")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["character"] == "Elizabeth Bennet"
    assert len(data["traits"]) > 0
    # Should have core traits
    core_traits = [t for t in data["traits"] if t.get("category") == "core"]
    assert len(core_traits) > 0


def test_profile_unknown() -> None:
    resp = client.get("/profile/Unknown")
    assert resp.status_code == 404


def test_sleep_stub() -> None:
    resp = client.post("/sleep/Elizabeth Bennet")
    assert resp.status_code == 200

def test_feedback_missing_scores() -> None:
    """Missing score dimensions should return 400."""
    resp = client.post(
        "/feedback/",
        json={
            "character": "Elizabeth Bennet",
            "option_label": "Direction 01",
            "scores": {"T": 0.8, "B": 0.7},  # missing D/C/P
            "marks": [],
        },
    )
    assert resp.status_code == 400
    data = resp.json()
    assert "Missing score dimension" in data["detail"]


def test_feedback_unknown_character() -> None:
    """Unknown character should return 404."""
    resp = client.post(
        "/feedback/",
        json={
            "character": "Nobody",
            "option_label": "A",
            "scores": {"T": 0.5, "B": 0.5, "D": 0.5, "C": 0.5, "P": 0.5},
            "marks": [],
        },
    )
    assert resp.status_code == 404


def test_feedback_full_flow() -> None:
    """Character-driven mark updates preferred_profile via EMA."""
    # First, fetch current profile to get baseline
    resp = client.get("/profile/Elizabeth Bennet")
    assert resp.status_code == 200
    before = resp.json()

    # Submit feedback: character-driven → EMA α=0.3
    resp = client.post(
        "/feedback/",
        json={
            "character": "Elizabeth Bennet",
            "option_label": "Direction 01",
            "scores": {"T": 0.85, "B": 0.80, "D": 0.15, "C": 0.90, "P": 0.10},
            "marks": ["role-driven"],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["updated"] is True
    assert data["preferred_profile"] is not None
    assert len(data["preferred_profile"]) == 5


def test_feedback_plot_driven_no_update() -> None:
    """Plot-driven mark should NOT update preferred_profile."""
    resp = client.post(
        "/feedback/",
        json={
            "character": "Elizabeth Bennet",
            "option_label": "Direction 02",
            "scores": {"T": 0.7, "B": 0.6, "D": 0.3, "C": 0.8, "P": 0.2},
            "marks": ["plot-driven"],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    # Plot-driven marks don't trigger EMA update
    assert data["updated"] is False


def test_feedback_experimental_no_update() -> None:
    """Experiment mark should NOT update preferred_profile."""
    resp = client.post(
        "/feedback/",
        json={
            "character": "Elizabeth Bennet",
            "option_label": "Direction 03",
            "scores": {"T": 0.5, "B": 0.5, "D": 0.6, "C": 0.6, "P": 0.5},
            "marks": ["experimental"],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["updated"] is False


def test_feedback_default_mark_slow_ema() -> None:
    """Default/'gut-feeling' mark uses slow EMA a=0.1 and still updates."""
    resp = client.post(
        "/feedback/",
        json={
            "character": "Elizabeth Bennet",
            "option_label": "Direction 04",
            "scores": {"T": 0.2, "B": 0.1, "D": 0.9, "C": 0.3, "P": 0.8},
            "marks": ["gut-feeling"],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["updated"] is True
    assert data["preferred_profile"] is not None
