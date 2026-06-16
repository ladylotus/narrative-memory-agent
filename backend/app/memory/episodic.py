"""Episodic memory — SQLite + vector retrieval (Zwaan-indexed events)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.config import SQLITE_PATH
from app.models.event import NarrativeEvent


class EpisodicMemory:
    """Event-indexed episodic store backed by SQLite.

    Each event is indexed by (time, space, protagonist, causality, intent)
    — Zwaan's event-indexing model — plus a vector embedding for
    similarity search.
    """

    def __init__(self, db_path: Path | str = SQLITE_PATH) -> None:
        self._path = Path(db_path)
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id          TEXT PRIMARY KEY,
                chapter     INTEGER NOT NULL,
                position    TEXT NOT NULL DEFAULT '',
                protagonist TEXT NOT NULL,
                summary     TEXT NOT NULL,
                importance  REAL NOT NULL DEFAULT 0.5,
                embedding   TEXT,          -- JSON float array
                related     TEXT,          -- JSON string array
                zwaan_dims  TEXT,          -- JSON dict
                emotion_tags TEXT,         -- JSON string array (Plutchik emotions)
                created_at  TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_events_protag
                ON events(protagonist);
            CREATE INDEX IF NOT EXISTS idx_events_chapter
                ON events(chapter);
        """)
        # Migration: add emotion_tags if missing (existing DB)
        try:
            self._conn.execute("ALTER TABLE events ADD COLUMN emotion_tags TEXT")
            self._conn.commit()
        except sqlite3.OperationalError:
            pass  # column already exists
        self._conn.commit()

    def add_event(self, event: NarrativeEvent) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO events
                (id, chapter, position, protagonist, summary,
                 importance, embedding, related, zwaan_dims)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.id,
                event.chapter,
                event.position,
                event.protagonist,
                event.summary,
                event.importance,
                json.dumps(event.embedding) if event.embedding else None,
                json.dumps(event.related_entities),
                json.dumps(event.zwaan_dims),
            ),
        )
        self._conn.commit()

    def get_events(
        self,
        protagonist: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM events"
        params: list[Any] = []
        if protagonist:
            query += " WHERE protagonist = ?"
            params.append(protagonist)
        query += " ORDER BY chapter, position LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = self._conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def update_importance(self, event_id: str, new_importance: float) -> None:
        """Update the importance score of an existing event."""
        self._conn.execute(
            "UPDATE events SET importance = ? WHERE id = ?",
            (new_importance, event_id),
        )
        self._conn.commit()

    def update_emotion_tags(
        self, event_id: str, tags: list[str]
    ) -> None:
        """Store Plutchik emotion tags for an event."""
        self._conn.execute(
            "UPDATE events SET emotion_tags = ? WHERE id = ?",
            (json.dumps(tags, ensure_ascii=False), event_id),
        )
        self._conn.commit()

    def delete_event(self, event_id: str) -> None:
        """Remove an event from the store."""
        self._conn.execute(
            "DELETE FROM events WHERE id = ?",
            (event_id,),
        )
        self._conn.commit()

    def count_events(self, protagonist: str | None = None) -> int:
        query = "SELECT COUNT(*) FROM events"
        params: list[Any] = []
        if protagonist:
            query += " WHERE protagonist = ?"
            params.append(protagonist)
        return self._conn.execute(query, params).fetchone()[0]
