"""Tests for decay.py — recall_score, classify, select_context.

Also tests episodic memory decay features: record_access, archive_event,
and the archive REM integration in sleep.py.
"""

from __future__ import annotations

import pytest

from app.services.decay import recall_score, classify, select_context


# ════════════════════════════════════════════════════════════
#  recall_score
# ════════════════════════════════════════════════════════════


class TestRecallScore:
    def test_fresh_event_max_score(self) -> None:
        """An event with importance=0.5 in the current chapter → score ≈ 0.5."""
        score = recall_score(0.5, 0)
        assert score == pytest.approx(0.5, abs=0.01)

    def test_decays_over_chapters(self) -> None:
        """The same event decays as chapters pass."""
        fresh = recall_score(0.5, 0)
        aged = recall_score(0.5, 10)
        assert aged < fresh

    def test_higher_importance_decays_slower_relative(self) -> None:
        """A high-importance event stays above threshold longer."""
        high = recall_score(0.9, 20)
        low = recall_score(0.3, 20)
        assert high > low

    def test_zero_importance_returns_zero(self) -> None:
        assert recall_score(0.0, 5) == 0.0

    def test_negative_chapter_is_clamped(self) -> None:
        """Negative chapters_elapsed (shouldn't happen) → treated as 0."""
        score = recall_score(0.5, -5)
        assert score == pytest.approx(0.5, abs=0.01)

    def test_conservative_params_demo_data(self) -> None:
        """Demo data: importance=0.3, 5 chapters elapsed → still active."""
        score = recall_score(0.3, 5)
        assert score >= 0.15  # well above archive threshold

    def test_many_chapters_eventually_archives(self) -> None:
        """Low-importance event, many chapters → below archive threshold."""
        score = recall_score(0.2, 200)
        assert score < 0.05


# ════════════════════════════════════════════════════════════
#  classify
# ════════════════════════════════════════════════════════════


class TestClassify:
    def test_above_active_threshold(self) -> None:
        assert classify(0.20) == "active"
        assert classify(0.15) == "active"

    def test_between_thresholds_is_fading(self) -> None:
        assert classify(0.10) == "fading"
        assert classify(0.07) == "fading"

    def test_below_archive_threshold(self) -> None:
        assert classify(0.04) == "archived"
        assert classify(0.0) == "archived"


# ════════════════════════════════════════════════════════════
#  select_context
# ════════════════════════════════════════════════════════════


class TestSelectContext:
    def test_all_active_returns_all(self) -> None:
        events = [
            {"id": "e1", "chapter": 5, "importance": 0.5, "summary": "Event one"},
            {"id": "e2", "chapter": 5, "importance": 0.4, "summary": "Event two"},
        ]
        result = select_context(events, current_chapter=5)
        assert len(result["active"]) == 2
        assert len(result["fading"]) == 0
        assert len(result["all_ids"]) == 2

    def test_old_events_become_fading(self) -> None:
        """An event many chapters behind gets classified as fading."""
        events = [
            {"id": "e1", "chapter": 1, "importance": 0.5, "summary": "Old event"},
        ]
        result = select_context(events, current_chapter=200)
        assert len(result["active"]) == 0
        assert len(result["fading"]) == 1

    def test_very_old_events_are_excluded(self) -> None:
        events = [
            {"id": "e1", "chapter": 1, "importance": 0.2, "summary": "Very old"},
        ]
        result = select_context(events, current_chapter=300)
        assert len(result["active"]) == 0
        assert len(result["fading"]) == 0
        assert len(result["all_ids"]) == 0

    def test_respects_max_active(self) -> None:
        events = [
            {"id": f"e{i}", "chapter": 10, "importance": 0.5,
             "summary": f"Event {i}"}
            for i in range(15)
        ]
        result = select_context(events, current_chapter=10, max_active=5)
        assert len(result["active"]) == 5

    def test_fading_summary_truncated(self) -> None:
        events = [
            {"id": "e1", "chapter": 1, "importance": 0.5,
             "summary": "A" * 200},
        ]
        result = select_context(events, current_chapter=200)
        assert len(result["fading"]) == 1
        text = result["fading"][0]["summary"]
        assert text.endswith("…")
        assert len(text) <= 105  # 100 + ellipsis

    def test_events_sorted_by_recall_score(self) -> None:
        events = [
            {"id": "recent", "chapter": 10, "importance": 0.3,
             "summary": "Recent event"},
            {"id": "old", "chapter": 1, "importance": 0.9,
             "summary": "Old but important"},
        ]
        result = select_context(events, current_chapter=10, max_active=2)
        # The old-but-important event (imp=0.9, ch=1) has higher recall_score
        # than the recent event (imp=0.3, ch=10)
        ids = [e["id"] for e in result["active"]]
        assert ids[0] == "old"

    def test_empty_events(self) -> None:
        result = select_context([], current_chapter=5)
        assert result["active"] == []
        assert result["fading"] == []
        assert result["all_ids"] == []


# ════════════════════════════════════════════════════════════
#  EpisodicMemory decay features (requires DB)
# ════════════════════════════════════════════════════════════


@pytest.fixture
def fresh_episodic(tmp_path):
    """Create an EpisodicMemory instance with a temp SQLite DB."""
    from app.memory.episodic import EpisodicMemory
    db = EpisodicMemory(tmp_path / "test.db")
    return db


class TestRecordAccess:
    def test_record_access_increments_count(self, fresh_episodic) -> None:
        from app.models.event import NarrativeEvent
        ev = NarrativeEvent(
            id="evt_001", chapter=1, position="1.1",
            protagonist="Elizabeth",
            summary="Test event",
            importance=0.5,
            related_entities=["Darcy"],
            zwaan_dims={"time": "morning", "space": "Netherfield",
                        "causality": "meeting", "intent": "observe",
                        "protagonist": "Elizabeth"},
            embedding=None,
        )
        fresh_episodic.add_event(ev)
        fresh_episodic.record_access(["evt_001"])
        stored = fresh_episodic.get_event("evt_001")
        assert stored is not None
        assert stored["access_count"] == 1
        assert stored["last_accessed_at"] is not None

    def test_record_access_multiple_times(self, fresh_episodic) -> None:
        from app.models.event import NarrativeEvent
        ev = NarrativeEvent(
            id="evt_002", chapter=1, position="1.0",
            protagonist="Elizabeth", summary="Another test",
            importance=0.5, related_entities=[],
            zwaan_dims={"time": "evening"},
            embedding=None,
        )
        fresh_episodic.add_event(ev)
        for _ in range(5):
            fresh_episodic.record_access(["evt_002"])
        stored = fresh_episodic.get_event("evt_002")
        assert stored["access_count"] == 5

    def test_record_access_empty_list_does_nothing(self, fresh_episodic) -> None:
        fresh_episodic.record_access([])  # should not raise


class TestArchiveEvent:
    def test_archive_moves_event(self, fresh_episodic) -> None:
        from app.models.event import NarrativeEvent
        ev = NarrativeEvent(
            id="evt_010", chapter=1, position="1.0",
            protagonist="Darcy",
            summary="Darcy saves Elizabeth's reputation at the ball",
            importance=0.3,
            related_entities=["Elizabeth"],
            zwaan_dims={"time": "evening"},
            embedding=None,
        )
        fresh_episodic.add_event(ev)
        assert fresh_episodic.count_events("Darcy") == 1

        result = fresh_episodic.archive_event("evt_010")
        assert result is True

        # Should be gone from active store
        assert fresh_episodic.count_events("Darcy") == 0
        # Should exist in archive
        assert fresh_episodic.count_archived("Darcy") == 1

    def test_archive_nonexistent_returns_false(self, fresh_episodic) -> None:
        result = fresh_episodic.archive_event("nonexistent")
        assert result is False

    def test_get_archive_returns_archived_data(self, fresh_episodic) -> None:
        from app.models.event import NarrativeEvent
        ev = NarrativeEvent(
            id="evt_020", chapter=2, position="2.1",
            protagonist="Elizabeth",
            summary="A very long summary " + "x" * 200,
            importance=0.4,
            related_entities=["Darcy", "Jane"],
            zwaan_dims={"time": "afternoon"},
            embedding=None,
        )
        fresh_episodic.add_event(ev)
        fresh_episodic.archive_event("evt_020", "Truncated summary")

        archived = fresh_episodic.get_archive("Elizabeth")
        assert len(archived) == 1
        assert archived[0]["summary"] == "Truncated summary"
        # full_text should preserve original
        assert len(archived[0]["full_text"]) > 100

    def test_get_max_chapter(self, fresh_episodic) -> None:
        from app.models.event import NarrativeEvent
        for i in range(1, 6):
            fresh_episodic.add_event(NarrativeEvent(
                id=f"evt_ch{i}", chapter=i, position="1.0",
                protagonist="Elizabeth",
                summary=f"Event in chapter {i}",
                importance=0.5,
                related_entities=[],
                zwaan_dims={},
                embedding=None,
            ))
        assert fresh_episodic.get_max_chapter("Elizabeth") == 5
