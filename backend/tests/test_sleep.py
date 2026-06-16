"""Test sleep consolidation cycle — inject events, trigger sleep, verify report."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import SQLITE_PATH

client = TestClient(app)


def _inject_test_events() -> None:
    """Insert synthetic Caelan events directly into SQLite."""
    conn = sqlite3.connect(str(SQLITE_PATH))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS events (
            id          TEXT PRIMARY KEY,
            chapter     INTEGER NOT NULL,
            position    TEXT NOT NULL DEFAULT '',
            protagonist TEXT NOT NULL,
            summary     TEXT NOT NULL,
            importance  REAL NOT NULL DEFAULT 0.5,
            embedding   TEXT,
            related     TEXT,
            zwaan_dims  TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        INSERT OR REPLACE INTO events (id, chapter, position, protagonist, summary, importance, zwaan_dims) VALUES
            ('test_e1', 1, '1/4', 'Caelan Ashmark',
             'Caelan chose to withdraw from the negotiation rather than force a confrontation.',
             0.4, '{"time":"evening","space":"hall","causality":"political pressure","intent":"avoid"}'),
            ('test_e2', 3, '2/4', 'Caelan Ashmark',
             'Caelan secretly undermined Corvan to secure a trade deal, breaking a private oath.',
             0.8, '{"time":"night","space":"study","causality":"betrayal of trust","intent":"betray"}'),
            ('test_e3', 4, '3/4', 'Caelan Ashmark',
             'When challenged publicly, Caelan retreated instead of asserting his authority.',
             0.6, '{"time":"afternoon","space":"great hall","causality":"public challenge","intent":"flee"}'),
            ('test_e4', 2, '1/2', 'Caelan Ashmark',
             'Caelan reviewed quarterly pack reports and approved the budget.',
             0.2, '{"time":"morning","space":"office","causality":"routine","intent":"manage"}'),
            ('test_e5', 5, '1/1', 'Caelan Ashmark',
             'An elder pack member died unexpectedly. Caelan handled the arrangements in silence.',
             0.5, '{"time":"dawn","space":"pack grounds","causality":"death","intent":"manage"}');
    """)
    conn.commit()
    conn.close()


def _cleanup_test_events() -> None:
    """Remove test events from DB using a fresh connection."""
    try:
        conn = sqlite3.connect(str(SQLITE_PATH))
        conn.execute("DELETE FROM events WHERE id LIKE 'test_%'")
        conn.commit()
        conn.close()
    except Exception:
        pass  # DB may not exist yet


@pytest.fixture(autouse=True)
def _auto_cleanup():
    yield
    _cleanup_test_events()


class TestSleepCycle:

    def test_sleep_unknown_character(self) -> None:
        resp = client.post("/sleep/Unknown")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "error"
        assert "not found" in data["message"]

    def test_sleep_no_events(self) -> None:
        """Caelan exists but has no events yet. Should return empty report."""
        resp = client.post("/sleep/Caelan Ashmark")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["report"] == {}

    def test_sleep_full_cycle(self) -> None:
        _inject_test_events()
        resp = client.post("/sleep/Caelan Ashmark")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["character"] == "Caelan Ashmark"

        report = data["report"]
        p1 = report["phase1"]
        p2 = report["phase2"]
        p3 = report["phase3"]

        # Phase 1
        assert p1["events_analyzed"] == 5
        assert len(p1["conflicts_detected"]) >= 1, f"Expected conflicts, got: {p1['conflicts_detected']}"
        assert len(p1["importance_adjustments"]) >= 1

        # Phase 3 summary
        assert "5 个事件" in p3["summary"]
        assert "冲突" in p3["summary"]

        print(f"\n{'='*50}")
        print(f"📋 睡眠巩固报告")
        print(f"{'='*50}")
        print(f"📊 分析: {p1['events_analyzed']} 个事件")
        print(f"⚡ 冲突: {json.dumps(p1['conflicts_detected'], ensure_ascii=False, indent=2)}")
        print(f"🔺 重要性调整: {json.dumps(p1['importance_adjustments'], ensure_ascii=False, indent=2)}")
        print(f"🔄 弧光变化: {json.dumps(p2['arc_stage_change'], ensure_ascii=False, indent=2)}")
        print(f"📉 特质更新: {json.dumps(p2['trait_updates'], ensure_ascii=False, indent=2)}")
        print(f"📋 摘要: {p3['summary']}")

    def test_sleep_history(self) -> None:
        resp = client.get("/sleep/Caelan Ashmark/history")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"

    def test_sleep_idempotent(self) -> None:
        _inject_test_events()
        resp1 = client.post("/sleep/Caelan Ashmark")
        resp2 = client.post("/sleep/Caelan Ashmark")
        assert resp1.status_code == 200
        assert resp2.status_code == 200

    def test_event_importance_persisted(self) -> None:
        """Death event should have importance boosted from 0.5 → 0.65 in DB."""
        _inject_test_events()
        client.post("/sleep/Caelan Ashmark")

        conn = sqlite3.connect(str(SQLITE_PATH))
        row = conn.execute(
            "SELECT id, importance, summary FROM events WHERE id = 'test_e5'"
        ).fetchone()
        conn.close()

        assert row is not None
        assert row[1] > 0.6, f"Expected boosted importance (>0.6), got {row[1]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--capture=tee-sys"])
